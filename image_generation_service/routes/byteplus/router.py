from fastapi import APIRouter, status
from core.utils import BaseApiResponse
from core.models import ImageResponse
from config.logger import logger
from .models import BytePlusImageGenerationRequest, BytePlusImageEditRequest
from .service import BytePlusService


router = APIRouter(prefix="/byteplus", tags=["BytePlus"])


@router.post("/generate", response_model=BaseApiResponse[ImageResponse])
async def generate_image(
    request: BytePlusImageGenerationRequest
):
    """
    Generate an image using Byteplus's image generation API.
    """

    try:
        byteplus_service = BytePlusService()

        if request.model in ["seedream-4-0-250828", "seedream-4-5-251128"]:
            data = byteplus_service.generate_image_with_seedream_4_suite_models(
                request=request)
        else:
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
            data=ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
            )
        )


@router.post("/edit", response_model=BaseApiResponse[ImageResponse])
async def generate_image(
    request: BytePlusImageEditRequest
):
    """
    Edit an image using Byteplus's image generation API.
    """

    try:
        byteplus_service = BytePlusService()

        if request.model == "seedream-4-0-250828":
            data = byteplus_service.generate_image_with_seedream_4(
                request=request)
        else:
            data = byteplus_service.edit_image(request=request)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image edited successfully",
            data=data
        )

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while edit the image. Please try again later",
            data=ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
            )
        )
