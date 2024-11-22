import io
import logging
from typing import Dict, List, Optional
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from services.embed_utils import send_img_to_embed
from PIL import Image

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ImagesResponse(BaseModel):
    images: Dict[str, str]
    last_id: Optional[str]


async def handle_image_embeddeding(file: UploadFile):
    """
    Handles the embedding process for a single uploaded image file.

    Parameters:
        file (UploadFile): An uploaded file object provided by the client. The file should contain image data.

    Returns:
        dict: A dictionary containing the normalized embedding of the input image.
    """
    try:
        # Read the binary data from the uploaded file
        image_data = await file.read()

        # Open the image using PIL
        image = Image.open(io.BytesIO(image_data))

        # Convert RGBA images to RGB to ensure compatibility with the embedding model
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Generate the embedding using the embedding utility
        embedding = await send_img_to_embed(image)

        # Return the embedding as part of the response
        return {"embedding": embedding}

    except Exception as e:
        # Log the error and raise an HTTP exception with a 500 status code
        logger.error(f"Error occurred during image embedding: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred during image search: {e}"
        )
