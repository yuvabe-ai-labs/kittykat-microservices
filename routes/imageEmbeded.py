import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, File, UploadFile
import numpy as np
from PIL import Image
import base64
import io
from pydantic import BaseModel, HttpUrl, ValidationError
from models.models import UrlRequest, ImageEmbedResponse
from services.image_search_utils import handle_image_embeddeding
from services.image_process_utils import process_image_from_url
from services.embed_utils import send_img_to_embed
from exceptions.ImageEmbedExceptions import (
    urlNotFoundException,
    InvalidUrlException,
    UnauthorizedUrlException,
    ImageProcessingException,
)
import aiohttp


class UrlValidator(BaseModel):
    url: HttpUrl


router = APIRouter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.post(
    "/image/embed/url",
    summary="Embedding a Imagen from url",
    response_model=ImageEmbedResponse,
)
async def embed_images(request: UrlRequest):
    """The search-by-image  endpoint allows users to search for similar images by uploading an image file. It accepts an image file, the number of top similar items to return (top_k), and a list of namespaces to search within. The image is processed to extract its embedding, and then the system retrieves similar images by comparing the embedding across the provided namespaces."""

    url = request.url

    if not url:
        logger.warning("URL not provided.")
        raise InvalidUrlException("URL is required but not provided.")
    # Validate URL format
    try:
        UrlValidator(url=url)
    except ValidationError:
        logger.warning("Invalid URL format provided.")
        raise InvalidUrlException("Invalid URL format provided.")

    # Check URL accessibility
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 401:  # Unauthorized
                    logger.warning("URL requires authentication.")
                    raise UnauthorizedUrlException()
                elif response.status != 200:  # Other HTTP errors
                    logger.warning(f"URL returned status code {response.status}.")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"URL returned status code {response.status}.",
                    )
        except aiohttp.ClientError as e:
            logger.warning(f"Error accessing the URL: {e}")
            raise InvalidUrlException("Could not access the provided URL.")

    # Process image from URL
    try:
        embedding = await process_image_from_url(url)
        return {"ImageEmbeddings": embedding}
    except Exception as e:
        logger.error(f"Failed to process image from URL: {e}")
        raise ImageProcessingException("Failed to process image from URL.")
