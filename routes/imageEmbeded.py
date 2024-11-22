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

