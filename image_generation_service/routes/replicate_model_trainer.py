import asyncio
import io
import zipfile
from fastapi import (
    HTTPException,
    Depends,
    Request,
    BackgroundTasks,
    Query,
    Path,
    APIRouter,
)
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import httpx
import uuid
from pydantic import HttpUrl
from config.gcp import bucket_prefix, bucket
from config.logger import logger
from config.replicate import get_api_client
from models.replicate_models import (
    HardwareInfo,
    PaginatedTrainings,
    TrainingInput,
    TrainingResponse,
    TrainingStatus,
    ZipRequest,
)
from services.enhance_prompt import image_to_description

router = APIRouter()


@router.post("/replicate/images-to-zip", response_model=HttpUrl)
async def create_zip(image_data: ZipRequest):
    """Create a zip file from image URLs and return the GCP URL."""
    if not image_data.image_urls:
        logger.error("No image URLs provided")
        raise HTTPException(status_code=400, detail="No image URLs provided")

    logger.info(f"Received request to create ZIP for folder: {image_data.folder_id}")

    try:
        zip_buffer = io.BytesIO()

        async def download_and_process_image(url, index):
            try:
                logger.info(
                    f"Downloading image {index + 1}/{len(image_data.image_urls)}: {url}"
                )
                async with httpx.AsyncClient(timeout=120.0) as img_client:
                    response = await img_client.get(str(url))
                    response.raise_for_status()

                    # Save image to zip
                    image_filename = f"image_{index:04d}.webp"
                    zip_file.writestr(image_filename, response.content)

                    # Generate and save description
                    description = await image_to_description(
                        str(url),
                        image_data.caption,
                        image_data.focus_entity,
                        image_data.trigger_word,
                    )
                    text_filename = f"image_{index:04d}.txt"
                    zip_file.writestr(text_filename, description.encode())

                    logger.info(f"Saved description in {text_filename}")

            except Exception as e:
                logger.error(f"Error processing image {url}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error downloading or processing image {url}: {e}",
                )

        # Create zip file and process images concurrently
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            await asyncio.gather(
                *[
                    download_and_process_image(url, i)
                    for i, url in enumerate(image_data.image_urls)
                ]
            )

        # Upload zip file to GCP
        zip_buffer.seek(0)
        zip_filename = f"{bucket_prefix}/replicate_training_data/{image_data.folder_id}/zip_{uuid.uuid4().hex[:8]}.zip"
        blob = bucket.blob(zip_filename)

        # Upload concurrently (if you have multiple files, use asyncio.gather)
        await asyncio.to_thread(
            blob.upload_from_file, zip_buffer, content_type="application/zip"
        )

        logger.info(f"Successfully created and uploaded ZIP: {blob.public_url}")
        return HttpUrl(blob.public_url)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post(
    "/replicate/models/trainings", response_model=TrainingResponse, status_code=201
)
async def create_training(
    training_input: TrainingInput,
    client: httpx.AsyncClient = Depends(get_api_client),
):
    """Create a new model training job, with support for direct image URLs."""
    try:
        logger.info(
            f"Creating training for model {training_input.model_owner}/{training_input.model_name}"
        )

        # Ensure we have input_images URL at this point
        if not training_input.input_images:
            raise HTTPException(
                status_code=400, detail="Failed to prepare input images for training"
            )

        # Prepare the request URL and payload
        url = f"/models/{training_input.model_owner}/{training_input.model_name}/versions/{training_input.version_id}/trainings"

        # Convert TrainingInputExtended to payload (excluding image_urls field)
        payload = training_input.to_replicate_payload()

        # Send the request to Replicate API
        response = await client.post(url, json=payload)

        # Handle error responses
        if response.status_code >= 400:
            logger.error(f"Training creation failed: {response.text}")
            error_detail = response.json().get("detail", response.text)
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create training: {error_detail}",
            )

        # Return the training response
        result = response.json()
        logger.info(f"Training created with ID: {result.get('id')}")
        return result

    except httpx.RequestError as e:
        logger.exception("Network error creating training")
        raise HTTPException(
            status_code=503,
            detail=f"Network error communicating with Replicate API: {str(e)}",
        )
    except Exception as e:
        logger.exception("Error creating training")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get(
    "/replicate/models/trainings/{training_id}", response_model=TrainingResponse
)
async def get_training(
    training_id: str = Path(..., description="Training ID"),
    client: httpx.AsyncClient = Depends(get_api_client),
    # _: str = Depends(verify_api_token),
):
    """Get status and details of a specific training job."""
    try:
        logger.info(f"Getting training info for ID: {training_id}")

        # Send request to Replicate API
        response = await client.get(f"/trainings/{training_id}")

        # Handle error responses
        if response.status_code == 404:
            raise HTTPException(
                status_code=404, detail=f"Training with ID {training_id} not found"
            )
        elif response.status_code >= 400:
            error_detail = response.json().get("detail", response.text)
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get training: {error_detail}",
            )

        # Return the training details
        return response.json()

    except httpx.RequestError as e:
        logger.exception(f"Network error getting training {training_id}")
        raise HTTPException(
            status_code=503,
            detail=f"Network error communicating with Replicate API: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting training {training_id}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/replicate/models/trainings", response_model=PaginatedTrainings)
async def list_trainings(
    limit: int = Query(100, description="Number of results per page", ge=1, le=500),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    client: httpx.AsyncClient = Depends(get_api_client),
    # _: str = Depends(verify_api_token),
):
    """List all training jobs with pagination."""
    try:
        logger.info("Listing trainings")

        # Build query parameters
        params = {}
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor

        # Send request to Replicate API
        response = await client.get("/trainings", params=params)

        # Handle error responses
        if response.status_code >= 400:
            error_detail = response.json().get("detail", response.text)
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to list trainings: {error_detail}",
            )

        # Return the paginated list
        return response.json()

    except httpx.RequestError as e:
        logger.exception("Network error listing trainings")
        raise HTTPException(
            status_code=503,
            detail=f"Network error communicating with Replicate API: {str(e)}",
        )
    except Exception as e:
        logger.exception("Error listing trainings")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post(
    "/replicate/models/trainings/{training_id}/cancel", response_model=TrainingResponse
)
async def cancel_training(
    training_id: str = Path(..., description="Training ID"),
    client: httpx.AsyncClient = Depends(get_api_client),
    # _: str = Depends(verify_api_token),
):
    """Cancel a training job in progress."""
    try:
        logger.info(f"Canceling training: {training_id}")

        # Send cancel request to Replicate API
        response = await client.post(f"/trainings/{training_id}/cancel")

        # Handle error responses
        if response.status_code == 404:
            raise HTTPException(
                status_code=404, detail=f"Training with ID {training_id} not found"
            )
        elif response.status_code == 400:
            # Training might already be completed or canceled
            error_detail = response.json().get("detail", response.text)
            raise HTTPException(
                status_code=400, detail=f"Cannot cancel training: {error_detail}"
            )
        elif response.status_code >= 400:
            error_detail = response.json().get("detail", response.text)
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to cancel training: {error_detail}",
            )

        # Return the updated training info
        return response.json()

    except httpx.RequestError as e:
        logger.exception(f"Network error canceling training {training_id}")
        raise HTTPException(
            status_code=503,
            detail=f"Network error communicating with Replicate API: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error canceling training {training_id}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# @router.get("/replicate/models/training/hardware", response_model=List[HardwareInfo])
# async def list_hardware(
#     client: httpx.AsyncClient = Depends(get_api_client),
#     # _: str = Depends(verify_api_token),
# ):
#     """List available hardware options for model training."""
#     try:
#         logger.info("Listing available hardware")

#         # Send request to Replicate API
#         response = await client.get("/hardware")

#         # Handle error responses
#         if response.status_code >= 400:
#             error_detail = response.json().get("detail", response.text)
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail=f"Failed to list hardware: {error_detail}",
#             )

#         # Return the hardware list
#         return response.json()

#     except httpx.RequestError as e:
#         logger.exception("Network error listing hardware")
#         raise HTTPException(
#             status_code=503,
#             detail=f"Network error communicating with Replicate API: {str(e)}",
#         )
#     except Exception as e:
#         logger.exception("Error listing hardware")
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# # Webhook handling endpoint
# @router.post("/replicate/models/training/webhook-receiver")
# async def webhook_receiver(request: Request, background_tasks: BackgroundTasks):
#     """
#     Receive and process webhook notifications from Replicate.
#     This can be used as the webhook URL in training requests.
#     """
#     try:
#         # Get the raw webhook data
#         webhook_data = await request.json()
#         training_id = webhook_data.get("id")
#         status = webhook_data.get("status")

#         if not training_id:
#             return JSONResponse(
#                 status_code=400,
#                 content={"detail": "Missing training ID in webhook data"},
#             )

#         # Log the webhook event
#         logger.info(f"Received webhook for training {training_id} with status {status}")

#         # Process the webhook asynchronously
#         background_tasks.add_task(process_webhook_event, webhook_data)

#         # Acknowledge receipt immediately
#         return JSONResponse(
#             status_code=202,
#             content={
#                 "status": "accepted",
#                 "message": "Webhook received and queued for processing",
#             },
#         )

#     except Exception as e:
#         logger.exception("Error processing webhook")
#         # Still return 202 to prevent Replicate from retrying
#         return JSONResponse(
#             status_code=202, content={"status": "accepted", "error": str(e)}
#         )


# # Background task to process webhooks
# async def process_webhook_event(webhook_data: Dict[str, Any]):
#     """
#     Process a webhook event from Replicate.
#     This would typically involve updating a database, notifying users, etc.
#     """
#     try:
#         training_id = webhook_data.get("id")
#         status = webhook_data.get("status")

#         # Here you would implement your business logic, such as:
#         # - Updating a database record
#         # - Sending notifications to users
#         # - Triggering follow-up actions on completion

#         logger.info(
#             f"Processing webhook for training {training_id} with status {status}"
#         )

#         # Example processing based on status
#         if status == TrainingStatus.SUCCEEDED:
#             # Handle successful completion
#             logger.info(f"Training {training_id} completed successfully")
#             # You might want to trigger a notification or follow-up process

#         elif status == TrainingStatus.FAILED:
#             # Handle failure
#             error = webhook_data.get("error", "Unknown error")
#             logger.error(f"Training {training_id} failed: {error}")
#             # You might want to trigger alerts or retries

#         elif status == TrainingStatus.CANCELED:
#             # Handle cancellation
#             logger.info(f"Training {training_id} was canceled")

#         # For other statuses (starting, processing), you might update progress indicators

#     except Exception as e:
#         logger.exception(
#             f"Error processing webhook for training {webhook_data.get('id')}"
#         )
