import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from helpers.image_utils import resize_image
from helpers.gcp_utils import upload_to_gcp
from constants.app_constants import MAX_IMAGE_SIZE

router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class ImageInput(BaseModel):
    url: HttpUrl
    bucket_name: str
    bucket_prefix: str
    file_name: str


@router.post("/resize-and-upload")
async def resize_and_upload_image(data: ImageInput):
    try:
        logger.info(
            f"Resizing and uploading image from {data.url} to bucket {data.bucket_name} with prefix {data.bucket_prefix}"
        )

        resized_image = resize_image(data.url, MAX_IMAGE_SIZE)
        logger.info(f"Image resized successfully to {MAX_IMAGE_SIZE}.")

        gcp_url = upload_to_gcp(
            resized_image, data.bucket_name, data.bucket_prefix, data.file_name
        )

        logger.info(f"Image uploaded to GCP with URL: {gcp_url}")
        return {"uploaded_url": gcp_url}

    except Exception as e:
        logger.error(f"Error resizing and uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
