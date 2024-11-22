import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, File, UploadFile
import numpy as np
from PIL import Image
import base64
import io
from pydantic import BaseModel
from models.models import Base64ImageRequest, ImageEmbedResponse
from services.image_search_utils import handle_image_embeddeding
from services.image_process_utils import process_image_from_url
from services.embed_utils import send_img_to_embed

router = APIRouter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.post(
    "/image/embed/file", summary="Embedding a Image", response_model=ImageEmbedResponse
)
async def embed_images(
    file: UploadFile = File(..., description="Image file to search by")
):
    """The search-by-image  endpoint allows users to search for similar images by uploading an image file. It accepts an image file, the number of top similar items to return (top_k), and a list of namespaces to search within. The image is processed to extract its embedding, and then the system retrieves similar images by comparing the embedding across the provided namespaces."""
    if not file:
        raise HTTPException(
            status_code=400, detail="Image file is required for the search."
        )
    # Handle image search
    embedding = await handle_image_embeddeding(file)
    return embedding


@router.post(
    "/image/embed/url",
    summary="Embedding a Imagen from url",
    response_model=ImageEmbedResponse,
)
async def embed_images(url: str):
    """The search-by-image  endpoint allows users to search for similar images by uploading an image file. It accepts an image file, the number of top similar items to return (top_k), and a list of namespaces to search within. The image is processed to extract its embedding, and then the system retrieves similar images by comparing the embedding across the provided namespaces."""
    if not url:
        raise HTTPException(
            status_code=400, detail="Image file is required for the search."
        )
    # Handle image search
    embedding = await process_image_from_url(url)
    return embedding


@router.post(
    "/image/embed/base64",
    summary="Embedding a base64 Image",
    response_model=ImageEmbedResponse,
)
async def embed_base64_image(request: Base64ImageRequest):
    """
    This endpoint allows users to search for similar images by providing an image in base64 format.
    It accepts a base64 string, processes it to extract its embedding, and returns the embedding.
    """
    base64_image = request.base64_image

    if not base64_image:
        raise HTTPException(
            status_code=400, detail="Base64 image data is required for the search."
        )

    try:
        # Decode the base64 string to bytes
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))

        # Convert RGBA to RGB if needed
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Get the embedding
        embedding = await send_img_to_embed(image)
        return {"embedding": embedding}  # Return the image embedding

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during image embedding: {e}"
        )
