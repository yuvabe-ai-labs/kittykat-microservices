from fastapi import APIRouter
from .models import CreateModelRequest, ModelVersionRequest, DeleteModelVersionRequest
from ..core.utils import BaseApiResponse
from ..core.utils import create_response, format_model_response
from ..core.config import DEFAULT_OWNER, make_request

router = APIRouter(prefix="/models", tags=["Models"])


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
