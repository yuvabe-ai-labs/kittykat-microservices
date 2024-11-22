import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, File, UploadFile
import numpy as np
from PIL import Image
import base64
import io
from pydantic import BaseModel
from models.models import UrlRequest, ImageEmbedResponse
from services.image_search_utils import handle_image_embeddeding
from services.image_process_utils import process_image_from_url
from services.embed_utils import send_img_to_embed
from exceptions.ImageEmbedExceptions import urlNotFoundException

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
        logger.warning("Url not Provided.")
        raise urlNotFoundException()
    # Handle image search
    embedding = await process_image_from_url(url)
    return {"ImageEmbeddings": embedding}
