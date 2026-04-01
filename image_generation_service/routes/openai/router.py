import openai
from config.logger import logger
from core.models import ImageResponse
from core.utils import BaseApiResponse
from fastapi import APIRouter, status
from .models import ImageEditRequest, ImageGenerationRequest, VirtualTryOnRequest
from .service import OpenAIService

router = APIRouter(prefix="/openai")


@router.post("/generate", response_model=BaseApiResponse[ImageResponse])
async def generate_image(request: ImageGenerationRequest):
    """
    Generate an image using OpenAI's image generation API.
    """
    try:
        openai_service = OpenAIService()

        data = await openai_service.generate_image(request=request)

        print(f"[generate] asset_urls={data.asset_urls} | parameters={request.parameters} | model_usage={data.model_usage}")

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image generated successfully.",
            data=data,
        )
    except openai.BadRequestError as e:
        logger.error(f"OpenAI BadRequestError: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid request parameters. Please check your input.",
            data=ImageResponse(
                error=str(e), is_nsfw_detected=e.code == "moderation_blocked"
            ),
        )

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while generating the image. Please try again later",
            data=ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
            ),
        )


@router.post("/edit", response_model=BaseApiResponse)
async def edit_image(request: ImageEditRequest):
    try:
        openai_service = OpenAIService()
        data = await openai_service.edit_image(request=request)

        print(f"[edit] asset_urls={data.asset_urls} | parameters={request.parameters} | model_usage={data.model_usage}")

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image edited successfully.",
            data=data,
        )
    except openai.BadRequestError as e:
        logger.error(f"OpenAI BadRequestError: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid request parameters. Please check your input.",
            data=ImageResponse(
                error=str(e), is_nsfw_detected=e.code == "moderation_blocked"
            ),
        )

    except Exception as e:
        logger.error(f"Error remixing image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while editing the image.",
            data=ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
            ),
        )


@router.post("/vton", response_model=BaseApiResponse)
async def vton_image(request: VirtualTryOnRequest):
    """
    Virtual Try-On (VTON) image generation.
    """
    try:
        openai_service = OpenAIService()

        data = await openai_service.generate_vton_image(request=request)

        print(f"[vton] asset_urls={data.asset_urls} | parameters={request.parameters} | model_usage={data.model_usage}")

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Virtual try on image generated successfully.",
            data=data,
        )

    except openai.BadRequestError as e:
        logger.error(f"OpenAI BadRequestError: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid request parameters. Please check your input.",
            data=ImageResponse(
                error=str(e), is_nsfw_detected=e.code == "moderation_blocked"
            ),
        )

    except Exception as e:
        logger.error(f"Error remixing image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while editing the image.",
            data=ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
            ),
        )
