import base64
from fastapi import APIRouter, Query, Path, Header, status
import httpx
from core.utils import BaseApiResponse
from .models import ImageUpscaleRequest
from config.logger import logger
from .service import ImageUpscaleService

router = APIRouter(prefix="/image-upscaling")


@router.post("", response_model=BaseApiResponse)
async def upscale_image(request: ImageUpscaleRequest):
    """
    Upscale an image using Magnific's asynchronous API.
    Returns task_id which can be tracked via webhook or polling.
    """
    try:
        result = await ImageUpscaleService.call_magnific_api(request)
        print(f"Received response from Magnific API: {result}")
        task_id = result.get("data", {}).get("task_id")

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image upscale task created successfully.",
            data={"task_id": task_id}
        )

    except ValueError as ve:
        logger.error(f"Invalid request: {ve}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(ve),
            data=None
        )

    except RuntimeError as re:
        logger.error(f"Magnific API error: {re}")
        return BaseApiResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            message="Magnific API returned an error.",
            data={"error": str(re)}
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while starting the image upscale task.",
            data={"error": str(e)}
        )
