from fastapi import APIRouter, status
from core.utils import BaseApiResponse
from core.models import ImageResponse
from config.logger import logger
from .models import GeminiImageGenerationRequest, GeminiImageEditRequest, GeminiVirtualTryOnRequest
from .service import GeminiService


router = APIRouter(prefix="/gemini", tags=["Gemini Image Generation"])


@router.post("/generate", response_model=BaseApiResponse[ImageResponse])
async def generate_image(
    request: GeminiImageGenerationRequest
):
    """
    Generate an image using Gemini's image generation API.
    """

    try:
        gemini_service = GeminiService()
        data = await gemini_service.generate_image(request)

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
async def edit_image(
    request: GeminiImageEditRequest
):
    """
    Edit an image using Gemini's image generation API.
    """

    try:
        gemini_service = GeminiService()

        data = await gemini_service.edit_image(request)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image edited successfully",
            data=data
        )

    except Exception as e:
        logger.error(f"Error editing image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while edit the image. Please try again later",
            data=ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
            )
        )


@router.post("/vton", response_model=BaseApiResponse)
async def generte_vton_image(request: GeminiVirtualTryOnRequest):
    """
    Virtual Try-On (VTON) image generation.
    """
    try:
        gemini_service = GeminiService()

        data = await gemini_service.generate_vton_image(request)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image edited successfully",
            data=data
        )

    except Exception as e:
        logger.error(f"Error editing image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while edit the image. Please try again later",
            data=ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
            )
        )
