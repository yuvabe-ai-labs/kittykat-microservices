from urllib.parse import urlparse
from fastapi import APIRouter, status
from openai import NotGiven, OpenAI
from core.utils import BaseApiResponse
from config.logger import logger
from .models import ImageEditRequest, ImageGenerationRequest, VirtualTryOnRequest
from .service import ImageService
from .config import client

router = APIRouter(prefix="/openai")


@router.post("/generate", response_model=BaseApiResponse)
async def generate_image(
    request: ImageGenerationRequest
):
    """
    Generate an image using OpenAI's image generation API.
    """

    try:
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

        asset_urls = []

        for image in result.data:
            image_base64 = image.b64_json

            url = ImageService.upload_base64_image_to_bucket(
                image_base64=image_base64,
                bucket_name=request.bucket,
                prefix=request.bucket_path,
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
            background="auto" if request.parameters.output_format == "jpeg" else request.parameters.background,
            quality=request.parameters.quality,
            n=request.parameters.n,
            prompt=request.prompt,
            mask=masked_image,
            image=image_files
        )

        asset_urls = []

        for image in result.data:
            image_base64 = image.b64_json

            url = ImageService.upload_base64_image_to_bucket(
                image_base64=image_base64,
                bucket_name=request.bucket,
                prefix=request.bucket_path,
                type=request.parameters.output_format
            )

            asset_urls.append(url)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image edited successfully.",
            data={"asset_urls": asset_urls}
        )

    except Exception as e:
        logger.error(f"Error remixing image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while editing the image.",
            data=None
        )


# @router.post("/vton", response_model=BaseApiResponse)
# async def vton_image(request: VirtualTryOnRequest):
#     """
#     Virtual Try-On (VTON) image generation.
#     """
#     try:
#         lifestyle_image_generated = None

#         if request.reference_image:
#             base_64_image = ImageService.create_lifestyle_image(
#                 reference_image=request.reference_image,
#                 model_image=request.model_image,
#             )

#             lifestyle_image_generated = ImageService.upload_base64_image_to_bucket(
#                 image_base64=base_64_image,
#                 bucket_name=request.bucket,
#                 prefix=request.bucket_path,
#                 type=request.parameters.output_format
#             )

#         image_files = [
#             ImageService.url_to_file_safe(
#                 request.reference_image)
#             if lifestyle_image_generated else ImageService.url_to_file_safe(
#                 request.model_image),
#             ImageService.url_to_file_safe(request.product_image),
#         ]

#         result = client.images.edit(
#             model="gpt-image-1",
#             size=request.parameters.size,
#             background="auto",
#             quality=request.parameters.quality,
#             n=1,
#             prompt=request.prompt,
#             image=image_files
#         )

#         asset_urls = []

#         image_base64 = result.data[0].b64_json
#         url = ImageService.upload_base64_image_to_bucket(
#             image_base64=image_base64,
#             bucket_name=request.bucket,
#             prefix=request.bucket_path,
#             type=request.parameters.output_format
#         )

#         asset_urls.append(url)

#         return BaseApiResponse(
#             status_code=status.HTTP_200_OK,
#             message="Virtual try on image generated successfully.",
#             data={"asset_urls": asset_urls}
#         )

#     except Exception as e:
#         logger.error(f"Error generating VTON image: {e}")
#         return BaseApiResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             message="An error occurred while generating the VTON image.",
#             data=None
#         )
