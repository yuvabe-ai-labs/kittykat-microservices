from fastapi import APIRouter, HTTPException
import httpx
from dotenv import load_dotenv
import os
from pydantic import ValidationError
from constants.url_constants import BASE_URL
from models.media_schema import (
    MediaQueryParams,
    MediaResponse,
    MediaUploadRequest,
    MediaUploadResponse,
    MediaDetailsResponse,
)
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

# Fetch the Pinterest API token from environment variables
PINTEREST_API_TOKEN = os.getenv("PINTEREST_API_TOKEN")
BASE_URL = f"{BASE_URL.rstrip('/')}/media"


@router.get("/media", response_model=MediaResponse)
async def list_media_uploads(query: MediaQueryParams):
    """
    List media uploads filtered by given parameters.

    Args:
        query (MediaQueryParams): Query parameters for filtering media uploads.

    Returns:
        MediaResponse: List of filtered media uploads.

    Raises:
        HTTPException: If an error occurs during the API call or response handling.
    """
    url = BASE_URL
    params = query.dict(exclude_unset=True)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    logger.info(f"Listing media uploads with parameters: {params}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            logger.info("Successfully retrieved media uploads.")
            return response.json()
        else:
            logger.error(f"Error retrieving media uploads. Status code: {response.status_code}, Response: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail="Unexpected error occurred while retrieving media uploads.",
            )
    except httpx.RequestError as e:
        logger.exception("HTTP request error while listing media uploads.")
        raise HTTPException(status_code=500, detail=f"HTTP request error: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error while listing media uploads.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.post("/media/register-upload", response_model=MediaUploadResponse)
async def register_media_upload(request: MediaUploadRequest):
    """
    Register your intent to upload media (e.g., video) to Pinterest.

    Args:
        request (MediaUploadRequest): The media type to register for upload.

    Returns:
        MediaUploadResponse: Contains media ID, media type, upload URL, and upload parameters.

    Raises:
        HTTPException: If an error occurs during the API call.
    """
    url = BASE_URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    payload = request.dict()
    logger.info(f"Registering media upload with payload: {payload}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            logger.info("Successfully registered media upload.")
            return response.json()
        elif response.status_code == 400:
            logger.warning("Invalid request for registering media upload.")
            raise HTTPException(status_code=400, detail="Invalid media upload request.")
        else:
            logger.error(f"Error registering media upload. Status code: {response.status_code}, Response: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error registering media upload.")
    except httpx.RequestError as e:
        logger.exception("HTTP request error while registering media upload.")
        raise HTTPException(status_code=500, detail=f"HTTP request error: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error while registering media upload.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/media/{media_id}", response_model=MediaDetailsResponse)
async def get_media_upload_details(media_id: str):
    """
    Get details for a registered media upload, including its current status.

    Args:
        media_id (str): The unique identifier for the media upload.

    Returns:
        MediaDetailsResponse: Contains media ID, media type, and upload status.

    Raises:
        HTTPException: If the media upload details are not found or an error occurs.
    """
    url = f"{BASE_URL}/{media_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PINTEREST_API_TOKEN}",
    }

    logger.info(f"Fetching details for media upload with ID: {media_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            logger.info(f"Successfully retrieved details for media ID: {media_id}")
            return response.json()
        elif response.status_code == 404:
            logger.warning(f"Media upload with ID {media_id} not found.")
            raise HTTPException(status_code=404, detail=f"Media upload with ID {media_id} not found.")
        else:
            logger.error(f"Error retrieving media details. Status code: {response.status_code}, Response: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error retrieving media upload details.")
    except httpx.RequestError as e:
        logger.exception("HTTP request error while fetching media upload details.")
        raise HTTPException(status_code=500, detail=f"HTTP request error: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error while fetching media upload details.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
