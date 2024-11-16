import logging
from fastapi import HTTPException
from services.embed_utils import send_text_to_embed

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def handle_text_search(search_query: str):
    try:
        embedding1 = await send_text_to_embed(search_query)
        return {"embedding": embedding1}  # Return the text embedding
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during text search: {e}"
        )
