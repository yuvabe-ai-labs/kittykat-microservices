import logging
import uuid
from fastapi import APIRouter, HTTPException
from services.handle_textSearch import handle_text_search
from models.models import TextRequest, TextEmbedResponse

router = APIRouter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.post("/text/embed", summary="Search by Text", response_model=TextEmbedResponse)
async def search_text(request: TextRequest):
    """
    The text_embedded endpoint converts text to embeddings.
    It takes a text query as input and returns the embeddings.
    """
    request_id = request.request_id
    response_id = uuid.uuid4().hex
    logger.info(
        f"Request received. Request ID: {request_id}, Response ID: {response_id}"
    )

    text = request.text
    if not text:
        logger.warning(
            f"Text not provided. Request ID: {request_id}, Response ID: {response_id}"
        )
        return TextEmbedResponse(
            text=text,
            request_id=request_id,
            response_id=response_id,
            textEmbedding=[],
            message="Text is required for embeddings",
        )

    try:
        logger.info(
            f"Processing text embedding. Request ID: {request_id}, Text: {text}"
        )
        embedding = await handle_text_search(text)
        logger.info(
            f"Text embedding generated successfully. Request ID: {request_id}, Response ID: {response_id}"
        )
    except Exception as e:
        logger.error(
            f"Error generating text embedding. Request ID: {request_id}, Response ID: {response_id}, Error: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to generate text embeddings"
        )

    return TextEmbedResponse(
        text=text,
        request_id=request_id,
        response_id=response_id,
        textEmbedding=embedding,
        message="Success",
    )
