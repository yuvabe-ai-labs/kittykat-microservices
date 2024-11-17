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
    try:
        # Read and process the image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Convert RGBA to RGB if needed
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Proceed directly to getting the embedding
        embedding = await send_img_to_embed(image)
        return {"embedding": embedding}  # Return the image embedding

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during image search: {e}"
        )
