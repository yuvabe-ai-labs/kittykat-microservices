import logging
from fastapi import APIRouter, HTTPException
from services.handle_textSearch import handle_text_search
from models.models import TextSearchRequest, TextEmbedResponse
from exceptions.TextEmbedExceptions import TextNotFoundException

router = APIRouter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


router = APIRouter()


@router.post("/text/embed", summary="Search by Text", response_model=TextEmbedResponse)
async def search_text(request: TextSearchRequest):
    """The search_text endpoint performs a text-based search for similar images.
    It takes a text query as input and returns the embeddings or similar images."""

    text = request.text

    if not text:
        logger.warning("Text not Provided.")
        raise TextNotFoundException()

    embedding = await handle_text_search(text)

    # Perform the image search
    return embedding
