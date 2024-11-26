import logging
import uuid
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, File, UploadFile
import numpy as np
from PIL import Image
import base64
import io
from pydantic import ValidationError
from models.models import UrlRequest, ImageEmbedResponse, UrlValidator
from services.image_search_utils import handle_image_embeddeding
from services.image_process_utils import process_image_from_url
from services.embed_utils import send_img_to_embed
from services.image_dimension_validator import check_image_dimensions
import aiohttp

# Initialize router
router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.post(
    "/image/embed/url",
    summary="Embedding an Image from a URL",
    response_model=ImageEmbedResponse,
)
async def embed_images(request: UrlRequest):
    """Endpoint to embed image from a provided URL, process it, and return image embeddings."""

    url = request.url
    request_id = request.request_id
    response_id = uuid.uuid4().hex

    # Check if URL is provided
    if not url:
        logger.warning(
            f"{request_id}, Image Processing Warning: URL not provided, {response_id}"
        )
        return ImageEmbedResponse(
            url=url,
            request_id=request_id,
            response_id=response_id,
            ImageEmbeddings=[],
            Message="URL is Empty.",
        )

    # Validate URL format
    try:
        UrlValidator(url=url)
    except ValidationError:
        logger.warning(
            f"{request_id}, Image Processing Warning: Invalid URL format: {url}, {response_id}"
        )
        return ImageEmbedResponse(
            url=url,
            request_id=request_id,
            response_id=response_id,
            ImageEmbeddings=[],
            Message="Invalid URL format provided.",
        )

    # Check URL accessibility
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 401:  # Unauthorized
                    logger.warning(
                        f"{request_id}, Image Processing Warning: URL requires authentication: {url}, {response_id}"
                    )
                    return ImageEmbedResponse(
                        url=url,
                        request_id=request_id,
                        response_id=response_id,
                        ImageEmbeddings=[],
                        Message="URL requires authentication.",
                    )
                elif response.status == 403:  # Forbidden
                    logger.warning(
                        f"{request_id}, Image Processing Warning: URL is forbidden: {url}, {response_id}"
                    )
                    return ImageEmbedResponse(
                        url=url,
                        request_id=request_id,
                        response_id=response_id,
                        ImageEmbeddings=[],
                        Message="URL is Forbidden.",
                    )
                elif response.status == 404:  # Not Found
                    logger.warning(
                        f"{request_id}, Image Processing Warning: URL is Not Found: {url}, {response_id}"
                    )
                    return ImageEmbedResponse(
                        url=url,
                        request_id=request_id,
                        response_id=response_id,
                        ImageEmbeddings=[],
                        Message="URL is Not Found",
                    )
                elif response.status != 200:  # Other HTTP errors
                    logger.warning(
                        f"{request_id}, Image Processing Warning: URL returned status code {response.status}, {response_id}"
                    )
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"URL returned status code {response.status}.",
                    )

        except aiohttp.ClientError as e:
            logger.error(
                f"{request_id}, Image Processing Error: Error accessing the URL {url}: {str(e)}, {response_id}"
            )
            return ImageEmbedResponse(
                url=url,
                request_id=request_id,
                response_id=response_id,
                ImageEmbeddings=[],
                Message=f"Error accessing the URL {url}: {e}.",
            )
            
    # Validate image dimensions
    valid, message = await check_image_dimensions(url)
    if not valid:
        logger.warning(
            f"{request_id}, Image Processing Warning: {message}, {response_id}"
        )
        return ImageEmbedResponse(
            url=url,
            request_id=request_id,
            response_id=response_id,
            ImageEmbeddings=[],
            Message=message,
        )

    # Process image from URL
    try:
        embedding = await process_image_from_url(url)
        logger.info(
            f"{request_id}, Image Processing Completed Successfully, {response_id}"
        )
        return ImageEmbedResponse(
            url=url,
            request_id=request_id,
            response_id=response_id,
            ImageEmbeddings=embedding,
            Message="Success.",
        )
    except Exception as e:
        logger.error(
            f"{request_id}, Image Processing Error: Failed to process image from URL {url}: {str(e)}, {response_id}"
        )
        return ImageEmbedResponse(
            url=url,
            request_id=request_id,
            response_id=response_id,
            ImageEmbeddings=[],
            Message="Failed to process image from URL.",
        )
