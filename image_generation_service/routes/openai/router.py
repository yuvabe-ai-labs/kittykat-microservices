import openai
from fastapi import APIRouter, status
from openai import NotGiven
import shortuuid
from core.utils import BaseApiResponse
from config.logger import logger
from .models import ImageEditRequest, ImageGenerationRequest, VirtualTryOnRequest
from .service import ImageService
from .config import client
from .constants import VIRTUAL_TRY_ON_BASE_PROMPT

router = APIRouter(prefix="/openai")


@router.post("/generate", response_model=BaseApiResponse)
async def generate_image(
    request: ImageGenerationRequest
):
    """
    Generate an image using OpenAI's image generation API.
    """

    try:
        # Reference images
        reference_image_files = [
            f for url in (request.reference_images or [])
            if (f := ImageService.url_to_file_safe(url)) is not None
        ]

        if len(reference_image_files) == 0:
            result = client.images.generate(
                model=request.model,
                prompt=request.prompt,
                size=request.parameters.size,
                background=request.parameters.background,
                quality=request.parameters.quality,
                output_format=request.parameters.output_format,
                moderation=request.parameters.moderation,
                output_compression=request.parameters.output_compression,
                n=request.parameters.n
            )

        else:
            # IMPORTANT: Not to use generate image function as it does not support reference images
            result = client.images.edit(
                model="gpt-image-1",
                size=request.parameters.size,
                background=request.parameters.background,
                quality=request.parameters.quality,
                n=request.parameters.n,
                prompt=request.prompt,
                image=reference_image_files,
                output_compression=request.parameters.output_compression,
                output_format=request.parameters.output_format,
            )

        asset_urls = []

        for image in result.data:
            image_base64 = image.b64_json

            if not image_base64:
                continue

            filename = f"{shortuuid.uuid()}.{request.parameters.output_format or 'webp'}"
            prefix = f"{request.bucket_path}/{filename}"

            url = ImageService.upload_base64_image_to_bucket(
                image_base64=image_base64,
                bucket_name=request.bucket,
                prefix=prefix,
                type=request.parameters.output_format
            )

            asset_urls.append(url)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image generated successfully.",
            data={
                "asset_urls": asset_urls, "usage": result.usage.model_dump()
                if result.usage else None
            }
        )
    except openai.BadRequestError as e:
        logger.error(f"OpenAI BadRequestError: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid request parameters. Please check your input.",
            data={
                "error": str(e),
                "is_nsfw_detected": e.code == "moderation_blocked"
            }
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


@router.post("/edit", response_model=BaseApiResponse)
async def edit_image(request: ImageEditRequest):
    try:
        # Mask image
        masked_image = ImageService.url_to_mask_file_safe(
            request.mask_image) if request.mask_image else NotGiven

        if request.mask_image and masked_image is None:
            raise ValueError(
                "Mask image could not be downloaded or is invalid. It must have an alpha channel.")

        # Base image
        base_image_file = ImageService.url_to_file_safe(request.base_image)
        if base_image_file is None:
            raise ValueError("Base image could not be downloaded.")

        # Reference images
        reference_image_files = [
            f for url in (request.reference_images or [])
            if (f := ImageService.url_to_file_safe(url)) is not None
        ]

        # OpenAI treates first image as base and rest as references
        image_files = [base_image_file] + reference_image_files

        # Call OpenAI image edit with explicit arguments
        result = client.images.edit(
            model="gpt-image-1",
            size=request.parameters.size,
            background=request.parameters.background,
            quality=request.parameters.quality,
            n=request.parameters.n,
            prompt=request.prompt,
            output_compression=request.parameters.output_compression,
            output_format=request.parameters.output_format,
            mask=masked_image,
            image=image_files
        )

        asset_urls = []

        for idx, image in enumerate(result.data):
            image_base64 = image.b64_json

            if not image_base64:
                continue

            filename = f"{shortuuid.uuid()}.{request.parameters.output_format or 'webp'}"
            prefix = f"{request.bucket_path}/{filename}"

            url = ImageService.upload_base64_image_to_bucket(
                image_base64=image_base64,
                bucket_name=request.bucket,
                prefix=prefix,
                type=request.parameters.output_format
            )

            asset_urls.append(url)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image edited successfully.",
            data={
                "asset_urls": asset_urls, "usage": result.usage.model_dump()
                if result.usage else None
            }
        )
    except openai.BadRequestError as e:
        logger.error(f"OpenAI BadRequestError: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid request parameters. Please check your input.",
            data={
                "error": str(e),
                "is_nsfw_detected": e.code == "moderation_blocked"
            }
        )

    except Exception as e:
        logger.error(f"Error remixing image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while editing the image.",
            data=None
        )


@router.post("/vton", response_model=BaseApiResponse)
async def vton_image(request: VirtualTryOnRequest):
    """
    Virtual Try-On (VTON) image generation.
    """
    try:

        image_files = [
            ImageService.url_to_file_safe(request.model_image),
            ImageService.url_to_file_safe(request.product_image),
        ]

        prompt = VIRTUAL_TRY_ON_BASE_PROMPT

        if request.prompt:
            prompt += f"\nAdditional instructions: {request.prompt}"

        result = client.images.edit(
            model="gpt-image-1",
            size=request.parameters.size,
            background="auto",
            quality=request.parameters.quality,
            n=request.parameters.n,
            prompt=prompt,
            image=image_files
        )

        asset_urls = []

        for idx, image in enumerate(result.data):
            image_base64 = image.b64_json

            if not image_base64:
                continue

            filename = f"{shortuuid.uuid()}.{request.parameters.output_format or 'webp'}"
            prefix = f"{request.bucket_path}/{filename}"

            url = ImageService.upload_base64_image_to_bucket(
                image_base64=image_base64,
                bucket_name=request.bucket,
                prefix=prefix,
                type=request.parameters.output_format
            )

            asset_urls.append(url)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Virtual try on image generated successfully.",
            data={
                "asset_urls": asset_urls, "usage": result.usage.model_dump()
                if result.usage else None
            }
        )

    except openai.BadRequestError as e:
        logger.error(f"OpenAI BadRequestError: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid request parameters. Please check your input.",
            data={
                "error": str(e),
                "is_nsfw_detected": e.code == "moderation_blocked"
            }
        )

    except Exception as e:
        logger.error(f"Error remixing image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while editing the image.",
            data=None
        )
