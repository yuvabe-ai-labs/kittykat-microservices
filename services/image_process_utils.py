from datetime import datetime
import io
import uuid
from PIL import ImageOps, Image
from fastapi import HTTPException, UploadFile
import logging
import requests
from services.embed_utils import send_img_to_embed


ALLOWED_FORMATS = ["JPEG", "PNG", "TIFF", "BMP", "WEBP", "JPG"]


def resize_image(img: Image.Image):
    """
    Resizes the image while maintaining the aspect ratio and compresses it.
    Converts the image to JPEG for better compression.
    """
    quality = 85
    img = ImageOps.exif_transpose(img)
    max_dimensions = (1024, 1024)

    img.thumbnail(max_dimensions, Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", optimize=True, quality=quality)
    buffer.seek(0)

    return img


async def process_image_from_url(url: str):
    """
    Fetches an image from a URL, validates the format, and processes it.
    """
    try:
        logging.info(f"Fetching image from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()

        img = Image.open(io.BytesIO(response.content))
        img_format = img.format.upper()

        if img_format not in ALLOWED_FORMATS:
            logging.error(f"Unsupported image format from URL: {img_format}")
            raise HTTPException(
                status_code=400, detail=f"Unsupported image format: {img_format}"
            )

        return await process_image(img, url)

    except Exception as e:
        logging.error(f"Error processing image from URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process image from URL.")


async def process_image(img: Image.Image, filename: str):
    """
    Converts, processes, resizes, and stores an image.
    Generates an embedding and stores the image in GCP.
    """
    try:
        # Generate a unique filename for the image
        unique_filename = f"{uuid.uuid4().hex}.jpeg"
        logging.info(f"Generated unique filename: {unique_filename}")

        # Convert RGBA to RGB if necessary
        if img.mode == "RGBA":
            logging.info("Image has 4 channels (RGBA), converting to 3 channels (RGB).")
            img = img.convert("RGB")

        # Resize and compress the image
        img = resize_image(img)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", optimize=True)
        buffer.seek(0)

        # Generate the embedding for the image
        logging.info("Sending image to embedding service.")
        embedding = await send_img_to_embed(img)
        logging.info(f"Received embedding for image: {filename}")

        # Get the current date in YYYY-MM-DD format
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Return the vector for upsert to Pinecone, including the original filename and current date in metadata
        return embedding

    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process image.")
