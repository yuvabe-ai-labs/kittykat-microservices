from fastapi import APIRouter, Depends, HTTPException
from models.fashn_models import (
    RunPredictionRequest,
    RunPredictionResponse,
    PredictionStatus,
)
from models.global_models import GeneralResponse
from services.fashn import FashnService
from services.gcp import upload_to_gcp
from utils.shortuid import generate_short_uid
from config.logger import logger

router = APIRouter()


@router.post("/fashn/tryon/run", response_model=GeneralResponse)
async def run_prediction(
    request: RunPredictionRequest, fashn_service: FashnService = Depends()
):
    logger.info("Received request to initiate prediction")
    try:
        logger.debug(f"Request data: {request}")
        prediction_id = await fashn_service.run_prediction(request)
        logger.info(f"Prediction initiated successfully with ID: {prediction_id}")
        return GeneralResponse(
            status_code=200,
            data=RunPredictionResponse(id=prediction_id),
            message="Prediction initiated successfully",
        )
    except Exception as e:
        logger.error(f"Error initiating prediction: {str(e)}", exc_info=True)
        return GeneralResponse(
            status_code=500, message=f"Error initiating prediction: {str(e)}", data=None
        )


@router.get("/fashn/tryon/status/{prediction_id}", response_model=GeneralResponse)
async def get_prediction_status(
    prediction_id: str, fashn_service: FashnService = Depends()
):
    logger.info(f"Fetching prediction status for ID: {prediction_id}")
    try:
        response = await fashn_service.get_prediction_status(prediction_id)
        logger.debug(f"Prediction status response: {response}")

        if response.status == "completed":
            output_urls = response.output
            if not output_urls:
                logger.warning(
                    f"Prediction completed but no output URLs provided for ID: {prediction_id}"
                )
                return GeneralResponse(
                    status_code=200,
                    data=PredictionStatus(
                        status=response.status, id=response.id, output=[]
                    ),
                    message="Prediction completed but no output URLs provided",
                )

            logger.info(
                f"Prediction completed. Uploading outputs to GCP for ID: {prediction_id}"
            )

            uploaded_urls = []
            for idx, url in enumerate(output_urls):
                destination_blob_name = f"fashn_outputs/{prediction_id}_{idx}.webp"
                try:
                    logger.debug(f"Uploading {url} to GCP as {destination_blob_name}")
                    uploaded_url = upload_to_gcp(url, destination_blob_name)
                    uploaded_urls.append(uploaded_url)
                    logger.info(f"Uploaded to GCP: {uploaded_url}")
                except Exception as e:
                    logger.error(
                        f"Error uploading to GCP for {url}: {str(e)}", exc_info=True
                    )
                    return GeneralResponse(
                        status_code=500,
                        message=f"Error uploading to GCP: {str(e)}",
                        data=None,
                    )

            return GeneralResponse(
                status_code=200,
                data=PredictionStatus(
                    status=response.status,
                    id=response.id,
                    output=uploaded_urls,
                ),
                message="Prediction status retrieved and uploaded to GCP successfully",
            )

        logger.info(f"Prediction not completed yet. Status: {response.status}")
        return GeneralResponse(
            status_code=200,
            data=PredictionStatus(
                status=response.status, id=response.id, output=response.output
            ),
            message="Prediction status retrieved successfully",
        )

    except Exception as e:
        logger.error(
            f"Error retrieving prediction status or uploading to GCP: {str(e)}",
            exc_info=True,
        )
        return GeneralResponse(
            status_code=500,
            message=f"Error retrieving prediction status or uploading to GCP: {str(e)}",
            data=None,
        )
