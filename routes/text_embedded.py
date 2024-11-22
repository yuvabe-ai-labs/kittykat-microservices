import logging
from fastapi import APIRouter, HTTPException
from services.handle_textSearch import handle_text_search
from models.models import TextSearchRequest, TextEmbedResponse

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
        raise HTTPException(
            status_code=400, detail="Search query is required for text search."
        )

    embedding = await handle_text_search(text)

    # Perform the image search
    return embedding
