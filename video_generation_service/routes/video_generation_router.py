from fastapi import APIRouter, Depends
from models.video_generation_model import RunPredictionRequest, PredictionStatus, RunPredictionResponse
from services.video_generation_service import ReplicateService
from services.gcp import upload_video_to_gcp
from utils.utils import BaseApiResponse
from config.logger import logger  # Importing the logger

router = APIRouter()


@router.post("/kling/predictions/run", response_model=BaseApiResponse[str])
async def create_prediction(
    request: RunPredictionRequest, replicate_service: ReplicateService = Depends()
):
    try:
        prediction_id = await replicate_service.create_prediction(request)
        return BaseApiResponse(status_code=200, message="Prediction created successfully", data=prediction_id)
    except Exception as e:
        return BaseApiResponse(status_code=500, message=f"Error creating prediction: {str(e)}", data=None)


@router.get("/kling/predictions/{prediction_id}", response_model=BaseApiResponse[PredictionStatus])
async def get_prediction_status(
    prediction_id: str, replicate_service: ReplicateService = Depends()
):
    try:
        logger.info(f"Fetching prediction status for ID: {prediction_id}")
        status = await replicate_service.get_prediction_status(prediction_id)
        logger.debug(f"Prediction status response: {status}")

        if status.status == "succeeded":
            output_urls = status.output
            logger.info(f"Prediction succeeded. Uploading outputs to GCP for ID: {prediction_id}")

            uploaded_urls = []
            for idx, url in enumerate(output_urls):
                destination_blob_name = f"video_generations/{prediction_id}_{idx}.mp4"
                try:
                    logger.debug(f"Uploading {url} to GCP as {destination_blob_name}")
                    uploaded_url = upload_video_to_gcp(url, destination_blob_name)
                    uploaded_urls.append(uploaded_url)
                    logger.info(f"Uploaded to GCP: {uploaded_url}")
                except Exception as e:
                    logger.error(f"Error uploading to GCP for {url}: {str(e)}", exc_info=True)
                    return BaseApiResponse(
                        status_code=500,
                        message=f"Error uploading to GCP: {str(e)}",
                        data=None,
                    )

            return BaseApiResponse(
                status_code=200,
                data=PredictionStatus(
                    status=status.status,
                    id=status.id,
                    output=uploaded_urls,
                ),
                message="Prediction status retrieved and uploaded to GCP successfully",
            )

        logger.info(f"Prediction not completed yet. Status: {status.status}")
        return BaseApiResponse(
            status_code=200,
            data=PredictionStatus(
                status=status.status, id=status.id, output=status.output
            ),
            message="Prediction status retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Error retrieving prediction status or uploading to GCP: {str(e)}", exc_info=True)
        return BaseApiResponse(
            status_code=500,
            message=f"Error retrieving prediction status or uploading to GCP: {str(e)}",
            data=None,
        )

@router.post("/kling/predictions/{prediction_id}/cancel", response_model=BaseApiResponse[dict])
async def cancel_prediction(
    prediction_id: str, replicate_service: ReplicateService = Depends()
):
    try:
        response = await replicate_service.cancel_prediction(prediction_id)
        return BaseApiResponse(status_code=200, message="Prediction canceled successfully", data=response)
    except Exception as e:
        return BaseApiResponse(status_code=500, message=f"Error canceling prediction: {str(e)}", data=None)


@router.get("/kling/predictions", response_model=BaseApiResponse[list])
async def list_all_predictions(replicate_service: ReplicateService = Depends()):
    try:
        predictions = await replicate_service.list_all_predictions()
        return BaseApiResponse(status_code=200, message="Predictions retrieved successfully", data=predictions)
    except Exception as e:
        return BaseApiResponse(status_code=500, message=f"Error listing predictions: {str(e)}", data=None)
