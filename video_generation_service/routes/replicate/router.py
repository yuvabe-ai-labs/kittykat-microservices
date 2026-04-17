
from typing import Optional

from core.models import VideoResponse
from fastapi import APIRouter, Header
from utils.utils import BaseApiResponse

from .models import CreatePredictionRequest
from .utils import make_request

router = APIRouter(
    prefix="/replicate"
)


@router.post("/generate", response_model=BaseApiResponse[VideoResponse])
async def create_prediction(
    request: CreatePredictionRequest, prefer: Optional[str] = Header(None)
):
    try:
        """
            Create a prediction for the model version and inputs provided.
            If Prefer header is set to wait, poll until the prediction is complete.
        """
        url = "https://api.replicate.com/v1/predictions"

        if not request.webhook:
            return BaseApiResponse(status_code=400, message="Webhook URL is required for this endpoint", data=None)

        # Prepare headers with potential Prefer header for wait mode
        custom_headers = {}
        if prefer:
            custom_headers["Prefer"] = prefer

        payload = request.dict(exclude_none=True)

        status_code, response_data = await make_request(
            "POST", url, payload, custom_headers)

        # Handle the original response if no polling was needed or if polling didn't complete
        if 200 <= status_code < 300:
            return BaseApiResponse(status_code=status_code, message="Replicate webhook handled successfully", data=VideoResponse(
                webhook_url=request.webhook, model_response=response_data
            ))

        else:
            return BaseApiResponse(status_code=status_code, message="Replicate webhook handled successfully", data=VideoResponse(
                webhook_url=request.webhook, model_response=response_data
            ))

    except Exception as e:

        return BaseApiResponse(status_code=500, message=f"An error occurred: {str(e)}", data=VideoResponse(
            error=str(e)
        ))
