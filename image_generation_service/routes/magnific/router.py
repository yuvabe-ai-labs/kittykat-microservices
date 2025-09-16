from fastapi import APIRouter, status
from core.utils import BaseApiResponse
from core.models import ImageResponse
from .models import ImageUpscaleRequest
from config.logger import logger
from .service import ImageUpscaleService

router = APIRouter(prefix="/magnific")


@router.post("/upscale", response_model=BaseApiResponse[ImageResponse])
async def upscale_image(request: ImageUpscaleRequest):
    """
    Upscale an image using Magnific's asynchronous API.
    Returns task_id which can be tracked via webhook or polling.
    """
    try:
        image_upscale_service = ImageUpscaleService()

        result = await image_upscale_service.call_magnific_api(request)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image upscale task created successfully.",
            data=result
        )

    except ValueError as ve:
        logger.error(f"Invalid request: {ve}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(ve),
            data=ImageResponse(
                error=str(ve),
                is_nsfw_detected=False,
            )
        )

    except RuntimeError as re:
        logger.error(f"Magnific API error: {re}")
        return BaseApiResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            message="Magnific API returned an error.",
            data=ImageResponse(
                error=str(re),
                is_nsfw_detected=False,
            )
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while starting the image upscale task",
            data=ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
            )
        )
