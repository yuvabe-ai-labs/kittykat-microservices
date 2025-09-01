from fastapi import APIRouter, status
from core.utils import BaseApiResponse
from config.logger import logger
from .models import BytePlusImageGenerationRequest
from .service import BytePlusService


router = APIRouter(prefix="/byteplus", tags=["BytePlus"])


@router.post("/generate", response_model=BaseApiResponse)
async def generate_image(
    request: BytePlusImageGenerationRequest
):
    """
    Generate an image using Byteplus's image generation API.
    """

    try:
        byteplus_service = BytePlusService()

        data = byteplus_service.generate_image(request=request)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image generated successfully",
            data=data
        )

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while generating the image. Please try again later",
            data={
                "error": str(e),
                "is_nsfw_detected": False
            }
        )
