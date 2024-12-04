from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from helpers.image_utils import resize_image
from helpers.gcp_utils import upload_to_gcp
from constants.app_constants import MAX_IMAGE_SIZE

router = APIRouter()


class ImageInput(BaseModel):
    url: HttpUrl
    bucket_name: str
    bucket_prefix: str
    file_name: str


@router.post("/resize-and-upload")
async def resize_and_upload_image(data: ImageInput):
    try:
        resized_image = resize_image(data.url, MAX_IMAGE_SIZE)
        gcp_url = upload_to_gcp(
            resized_image, data.bucket_name, data.bucket_prefix, data.file_name
        )
        return {"uploaded_url": gcp_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
