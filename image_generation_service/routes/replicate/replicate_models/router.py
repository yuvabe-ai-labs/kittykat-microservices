from typing import Optional
from fastapi import APIRouter, Body, Header, Path
from .models import (
    CreateModelPredictionRequest,
    CreateModelRequest,
    ModelVersionRequest,
    DeleteModelVersionRequest,
)
from ..core.utils import BaseApiResponse, format_prediction_response
from ..core.utils import create_response, format_model_response
from ..core.config import DEFAULT_OWNER, make_request

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("", response_model=BaseApiResponse)
async def list_models():
    """
    Get a paginated list of public models.
    """
    url = "https://api.replicate.com/v1/models"

    status_code, response_data = make_request("GET", url)

    if status_code == 200:
        return create_response(
            status_code=200,
            message="Models listed successfully",
            data=response_data,
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to list models",
            data=response_data,
        )


@router.post("/search", response_model=BaseApiResponse)
async def search_models(query: str = Body(..., embed=True)):
    """
    Search for public models matching a query.
    """
    url = "https://api.replicate.com/v1/models"

    # For the search endpoint, Replicate uses a special QUERY method
    # We'll use a POST request here and handle it server-side
    headers = {"Content-Type": "text/plain"}

    status_code, response_data = make_request(
        "POST", url, payload=query, custom_headers=headers, is_search=True
    )

    if status_code == 200:
        return create_response(
            status_code=200,
            message="Models search completed successfully",
            data=response_data,
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to search models",
            data=response_data,
        )


@router.post("/create", response_model=BaseApiResponse)
async def create_model(request: CreateModelRequest):
    url = "https://api.replicate.com/v1/models"

    payload = {
        "owner": request.owner,
        "name": request.name,
        "visibility": request.visibility.value,
        "hardware": request.hardware.value,
    }

    status_code, response_data = make_request("POST", url, payload)
    print(response_data)

    if status_code == 201:
        return create_response(
            status_code=201,
            message="Model created successfully",
            data=format_model_response(response_data),
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to create model",
            data=response_data,
        )


@router.get("/{owner}/{model}", response_model=BaseApiResponse)
def get_model_details(model: str, owner: str = DEFAULT_OWNER):
    url = f"https://api.replicate.com/v1/models/{owner}/{model}"

    status_code, response_data = make_request("GET", url)

    if status_code == 200:
        return create_response(
            status_code=200,
            message="Model details retrieved successfully",
            data=format_model_response(response_data),
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to retrieve model details",
            data=response_data,
        )


@router.post("/versions", response_model=BaseApiResponse)
def get_model_versions(request: ModelVersionRequest):
    url = (
        f"https://api.replicate.com/v1/models/{request.owner}/{request.model}/versions"
    )

    status_code, response_data = make_request("GET", url)

    if status_code == 200:
        return create_response(
            status_code=200,
            message="Model versions retrieved successfully",
            data=response_data,
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to retrieve model versions",
            data=response_data,
        )


@router.delete("/version", response_model=BaseApiResponse)
def delete_model_version(request: DeleteModelVersionRequest):
    url = f"https://api.replicate.com/v1/models/{request.owner}/{request.model}/versions/{request.version_id}"

    status_code, response_data = make_request("DELETE", url)

    if status_code == 204:
        return create_response(
            status_code=204, message="Model version deleted successfully", data=None
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to delete model version",
            data=response_data,
        )


@router.delete("/{name}", response_model=BaseApiResponse)
async def delete_model(name: str, owner: str = DEFAULT_OWNER):
    if "/" in name:
        name = name.split("/")[-1]

    url = f"https://api.replicate.com/v1/models/{owner}/{name}"

    status_code, response_data = make_request("DELETE", url)

    if status_code == 204:
        return create_response(
            status_code=204, message=f"Model '{name}' deleted successfully", data=None
        )
    else:
        return create_response(
            status_code=status_code,
            message=f"Failed to delete model '{name}'",
            data=response_data,
        )


@router.post("/{model_owner}/{model_name}/predictions", response_model=BaseApiResponse)
async def create_model_prediction(
    request: CreateModelPredictionRequest,
    model_owner: str = Path(
        ..., description="The name of the user or organization that owns the model"
    ),
    model_name: str = Path(..., description="The name of the model"),
    prefer: Optional[str] = Header(None),
):
    """
    Create a prediction using an official model.
    """
    url = f"https://api.replicate.com/v1/models/{model_owner}/{model_name}/predictions"

    # Prepare headers with potential Prefer header for wait mode
    custom_headers = {}
    if prefer:
        custom_headers["Prefer"] = prefer

    payload = request.dict(exclude_none=True)

    status_code, response_data = make_request("POST", url, payload, custom_headers)

    if 200 <= status_code < 300:
        return create_response(
            status_code=status_code,
            message="Model prediction created successfully",
            data=format_prediction_response(response_data),
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to create model prediction",
            data=response_data,
        )


@router.get("/versions/{owner}/{model}/{version_id}", response_model=BaseApiResponse)
async def get_model_version(
    owner: str = Path(..., description="The owner of the model"),
    model: str = Path(..., description="The name of the model"),
    version_id: str = Path(..., description="The specific version ID of the model"),
):
    """
    Get a specific model version from Replicate API.
    """
    url = f"https://api.replicate.com/v1/models/{owner}/{model}/versions/{version_id}"

    status_code, response_data = make_request("GET", url)

    if status_code == 200:
        return create_response(
            status_code=200,
            message="Model version retrieved successfully",
            data=response_data,
        )
    else:
        return create_response(
            status_code=status_code,
            message="Failed to retrieve model version",
            data=response_data,
        )
