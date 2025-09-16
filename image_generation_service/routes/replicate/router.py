
from typing import Optional
from fastapi import APIRouter, Header

from core.utils import BaseApiResponse
from core.models import ImageResponse
from routes.replicate.core.config import make_request
from routes.replicate.predictions.models import CreatePredictionRequest


router = APIRouter(
    prefix="/replicate"
)


@router.post("/generate", response_model=BaseApiResponse[ImageResponse])
async def create_prediction(
    request: CreatePredictionRequest, prefer: Optional[str] = Header(None)
):
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

    status_code, response_data = make_request(
        "POST", url, payload, custom_headers)

    # Handle the original response if no polling was needed or if polling didn't complete
    if 200 <= status_code < 300:
        return BaseApiResponse(status_code=status_code, message="Replicate webhook handled successfully", data=ImageResponse(
            webhook_url=request.webhook, model_response=response_data
        ))

    else:
        return BaseApiResponse(status_code=status_code, message="Replicate webhook handled successfully", data=ImageResponse(
            webhook_url=request.webhook, model_response=response_data
        ))
