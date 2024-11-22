import logging
from fastapi import APIRouter, HTTPException
from services.handle_textSearch import handle_text_search
from models.models import TextRequest, TextEmbedResponse
from exceptions.TextEmbedExceptions import TextNotFoundException

router = APIRouter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


router = APIRouter()


@router.post("/text/embed", summary="Search by Text", response_model=TextEmbedResponse)
async def search_text(request: TextRequest):
    """The text_embedded endpoint converts text to embeddibgs.
    It takes a text query as input and returns the embeddings ."""

    text = request.text

    if not text:
        logger.warning("Text not Provided.")
        raise TextNotFoundException()

    embedding = await handle_text_search(text)

    # Perform the image search
    return embedding
