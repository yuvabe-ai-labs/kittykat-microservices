from fastapi import APIRouter, status
from config.openai import describe_image
from models.global_models import BaseApiResponse
from models.image_to_description import (
    ImageToDescriptionRequest,
    ImageToDescriptionResponse,
)

router = APIRouter()


@router.post(
    "/openai/image-to-description",
    response_model=BaseApiResponse[ImageToDescriptionResponse],
)
async def image_to_description(request: ImageToDescriptionRequest):
    try:
        if not request.image_url:
            raise ValueError("Image URL is required")

        description = await describe_image(
            request.image_url,
            request.user_prompt,
            request.focus_entity,
            request.trigger_word,
            model=request.openai_model,
        )
        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image description generated successfully",
            data=ImageToDescriptionResponse(description=description),
        )
    except ValueError as ve:
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST, message=str(ve), data=None
        )
    except Exception as e:
        return BaseApiResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            data=None,
        )
