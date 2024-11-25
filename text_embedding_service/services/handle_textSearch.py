import logging
from fastapi import HTTPException
from services.embed_utils import send_text_to_embed

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def handle_text_search(search_query: str):
    """
    Processes a text search query and generates an embedding for the text.

    Parameters:
        search_query (str): The input text query for which an embedding is to be generated.

    Returns:
        dict: A dictionary containing the embedding of the input text.
    """
    try:
        # Generate the embedding for the input text query
        embedding1 = await send_text_to_embed(search_query)
        return embedding1  # Return the text embedding

    except Exception as e:
        # Raise an HTTP exception with the error message
        raise HTTPException(
            status_code=500, detail=f"An error occurred during text search: {e}"
        )
