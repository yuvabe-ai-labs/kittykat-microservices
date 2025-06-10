import base64
import io
import os
from urllib.parse import urlparse
import requests  

from fastapi import APIRouter, status
from openai import OpenAI
from core.utils import BaseApiResponse
from config.logger import logger
from .models import ImageEditRequest, ImageGenerationRequest
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
async def remix_image(request: ImageEditRequest):
    try:
        request.validate()
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info(f"Received prompt: '{request.prompt}'")
        # Handle input image
        if request.image_base64_list:
            image_data = [base64.b64decode(img) for img in request.image_base64_list]
        elif request.image_base64:
            image_data = base64.b64decode(request.image_base64)
        elif request.image_url:
            response = requests.get(request.image_url)
            file_ext = os.path.splitext(urlparse(request.image_url).path)[1].lower()
            filename = f"input{file_ext or '.png'}"
            img_file = io.BytesIO(response.content)
            img_file.name = filename
            image_data = img_file
        else:
            raise ValueError("An image input (image_base64, image_base64_list, or image_url) must be provided.")

        # Prepare common arguments for OpenAI API call
        edit_args = {
            "model": request.model.value,
            "prompt": request.prompt or "",
            "image": image_data,
            "size": request.parameters.size,
            "background": request.parameters.background,
            "quality": request.parameters.quality,
            "n": request.parameters.n
        }

        # Add mask only if provided
        if request.mask_base64:
            edit_args["mask"] = base64.b64decode(request.mask_base64)

        # Call OpenAI image edit with explicit arguments
        result = client.images.edit(**edit_args)

        asset_urls = []
        for i, image in enumerate(result.data):
            image_base64 = image.b64_json
            suffix = f"_{i+1}" if request.parameters.n > 1 else ""
            path_with_suffix = request.bucket_path.replace(".webp", f"{suffix}.webp")
            url = ImageService.upload_base64_image_to_bucket(
                image_base64=image_base64,
                bucket_name=request.bucket,
                prefix=path_with_suffix,
                type=request.parameters.output_format
            )
            asset_urls.append(url)

        return BaseApiResponse(
            status_code=status.HTTP_200_OK,
            message="Image remixed successfully.",
            data={"asset_urls": asset_urls}
        )
    except ValueError as ve:
        return BaseApiResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=str(ve),
            data=None
        )
    except Exception as e:
        logger.error(f"Error remixing image: {e}")
        return BaseApiResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="An error occurred while remixing the image.",
            data=None
        )
