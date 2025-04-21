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
    If Prefer header is set to wait, poll until the prediction is complete.
    """
    url = "https://api.replicate.com/v1/predictions"

    # Prepare headers with potential Prefer header for wait mode
    custom_headers = {}
    if prefer:
        custom_headers["Prefer"] = prefer

    payload = request.dict(exclude_none=True)

    status_code, response_data = make_request("POST", url, payload, custom_headers)
    print("p", response_data)

    # If prefer header contains 'wait' and we got a 202 response, poll until complete
    if prefer and "wait" in prefer and status_code == 202 and "id" in response_data:
        # Extract prediction ID from the response
        prediction_id = response_data["id"]

        # Poll the prediction status until it's complete or fails
        max_polls = 30  # Maximum number of polling attempts
        poll_interval = 1  # Time in seconds between polling attempts

        for _ in range(max_polls):
            # Wait before polling again
            import time

            time.sleep(poll_interval)

            # Poll the prediction status
            poll_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
            poll_status_code, poll_response = make_request("GET", poll_url)

            print(f"Polling prediction: {poll_response.get('status', 'unknown')}")

            # Check if prediction is complete or has failed
            if poll_response.get("status") in ["succeeded", "completed"]:
                return create_response(
                    status_code=200,
                    message="Prediction completed successfully",
                    data=format_prediction_response(poll_response),
                )
            elif poll_response.get("status") in ["failed", "canceled"]:
                return create_response(
                    status_code=400,
                    message=f"Prediction failed with status: {poll_response.get('status')}",
                    data=poll_response,
                )

            # If still processing, continue polling

        # If we've reached the maximum polling attempts and still no complete result
        return create_response(
            status_code=202,
            message="Prediction is still processing after maximum polling attempts",
            data=format_prediction_response(poll_response),
        )

    # Handle the original response if no polling was needed or if polling didn't complete
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
