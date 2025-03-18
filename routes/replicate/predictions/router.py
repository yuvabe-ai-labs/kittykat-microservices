from fastapi import APIRouter, Query, Path, Header
from typing import Optional, List
from pydantic import HttpUrl

from .models import (
    CreatePredictionRequest,
    PredictionResponse,
    PaginatedPredictionsResponse,
)
from ..core.utils import BaseApiResponse, create_response, format_prediction_response
from ..core.config import make_request

router = APIRouter(prefix="/predictions")


@router.post("", response_model=BaseApiResponse)
async def create_prediction(
    request: CreatePredictionRequest, prefer: Optional[str] = Header(None)
):
    """
    Create a prediction for the model version and inputs provided.
    """
    url = "https://api.replicate.com/v1/predictions"

    # Prepare headers with potential Prefer header for wait mode
    custom_headers = {}
    if prefer:
        custom_headers["Prefer"] = prefer

    payload = request.dict(exclude_none=True)

    status_code, response_data = make_request("POST", url, payload, custom_headers)
    print("p", response_data)

    if 200 <= status_code < 300:
        return create_response(
            status_code=status_code,
            message="Prediction created successfully",
            data=format_prediction_response(response_data),
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to create prediction",
            data=response_data,
        )


@router.get("/{prediction_id}", response_model=BaseApiResponse)
async def get_prediction(
    prediction_id: str = Path(..., description="The ID of the prediction to get")
):
    """
    Get the current state of a prediction.
    """
    url = f"https://api.replicate.com/v1/predictions/{prediction_id}"

    status_code, response_data = make_request("GET", url)

    if status_code == 200:
        return create_response( 
            status_code=200,
            message="Prediction retrieved successfully",
            data=format_prediction_response(response_data),
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to retrieve prediction",
            data=response_data,
        )


@router.get("", response_model=BaseApiResponse)
async def list_predictions(
    created_after: Optional[str] = Query(
        None,
        description="Include only predictions created at or after this date-time, in ISO 8601 format",
    ),
    created_before: Optional[str] = Query(
        None,
        description="Include only predictions created before this date-time, in ISO 8601 format",
    ),
):
    """
    Get a paginated list of all predictions created by the user or organization associated with the provided API token.
    """
    url = "https://api.replicate.com/v1/predictions"

    # Add query parameters if provided
    params = {}
    if created_after:
        params["created_after"] = created_after
    if created_before:
        params["created_before"] = created_before

    status_code, response_data = make_request("GET", url, params=params)

    if status_code == 200:
        return create_response(
            status_code=200,
            message="Predictions listed successfully",
            data=response_data,
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to list predictions",
            data=response_data,
        )


@router.post("/{prediction_id}/cancel", response_model=BaseApiResponse)
async def cancel_prediction(
    prediction_id: str = Path(..., description="The ID of the prediction to cancel")
):
    """
    Cancel a prediction.
    """
    url = f"https://api.replicate.com/v1/predictions/{prediction_id}/cancel"

    status_code, response_data = make_request("POST", url)
    print("p", response_data)

    if status_code == 200:
        return create_response(
            status_code=200,
            message="Prediction canceled successfully",
            data=response_data,
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to cancel prediction",
            data=response_data,
        )
