import os
from fastapi import APIRouter, status
from openai import OpenAI
from core.utils import BaseApiResponse
from config.logger import logger
from .models import ImageGenerationRequest
from .service import ImageService

router = APIRouter(prefix="/openai")


@router.post("/generate", response_model=BaseApiResponse)
async def generate_image(
    request: ImageGenerationRequest
):
    """
    Generate an image using OpenAI's image generation API.
    """

    try:
        client = OpenAI()

        result = client.images.generate(
            model=request.model,
            prompt=request.prompt,
            size=request.parameters.size,
            background="auto" if request.parameters.output_format == "jpeg" else request.parameters.background,
            quality=request.parameters.quality,
            output_format=request.parameters.output_format,
            moderation=request.parameters.moderation,
            output_compression=100 if request.parameters.output_format == "png" else request.parameters.output_compression,
            n=request.parameters.n
        )

        print(len(result.data))
        asset_urls = []

        for image in result.data:
            image_base64 = image.b64_json

            url = ImageService.upload_base64_image_to_bucket(
                image_base64=image_base64,
                bucket_name=request.bucket,
                prefix=request.bukcet_path,
                type=request.parameters.output_format
            )

            asset_urls.append(url)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image generated successfully.",
            data={
                "asset_urls": asset_urls
            }
        )
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while generating the image. Please try again later",
            data=None
        )
