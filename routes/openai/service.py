import os
from io import BytesIO
from typing import Optional
from urllib.parse import urlparse

import requests
from config.logger import logger
from core.models import ImageResponse
from openai import NotGiven
from PIL import Image, ImageOps

from utils.helpers import safe_log_dict

from .config import client
from .constants import VIRTUAL_TRY_ON_BASE_PROMPT
from .models import (ImageEditRequest, ImageGenerationRequest,
                     VirtualTryOnRequest)


class OpenAIService:
    def generate_image(self, request: ImageGenerationRequest) -> ImageResponse:
        try:
            # Reference images
            reference_image_files = [
                f for url in (request.reference_images or [])
                if (f := OpenAIServiceUtils.url_to_file_safe(url)) is not None
            ]

            logger.info(
                request.model_dump_json(
                    indent=2
                )
            )

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
                    model=request.model,
                    size=request.parameters.size,
                    background=request.parameters.background,
                    quality=request.parameters.quality,
                    n=request.parameters.n,
                    prompt=request.prompt,
                    image=reference_image_files,
                    output_compression=request.parameters.output_compression,
                    output_format=request.parameters.output_format,
                )

            asset_b64s = []

            for image in result.data:
                image_base64 = image.b64_json

                if not image_base64:
                    continue

                asset_b64s.append(image_base64)

            return ImageResponse(
                asset_base64s=asset_b64s,
                model_response=result.model_dump(),
                model_usage=result.usage.model_dump() if result.usage else None

            )

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise e

    def edit_image(self, request: ImageEditRequest) -> ImageResponse:
        try:
            # Mask image
            masked_image = OpenAIServiceUtils.url_to_mask_file_safe(
                request.mask_image) if request.mask_image else None

            # if request.mask_image and masked_image is None:
            #     raise ValueError(
            #         "Mask image could not be downloaded or is invalid. It must have an alpha channel.")

            # Base image
            base_image_file = OpenAIServiceUtils.url_to_file_safe(
                request.base_image)
            if base_image_file is None:
                raise ValueError("Base image could not be downloaded.")

            # Reference images
            reference_image_files = [
                f for url in (request.reference_images or [])
                if (f := OpenAIServiceUtils.url_to_file_safe(url)) is not None
            ]

            # OpenAI treates first image as base and rest as references
            image_files = [base_image_file] + reference_image_files

            edit_args = {
                "model": "gpt-image-1",
                "size": request.parameters.size,
                "background": request.parameters.background,
                "quality": request.parameters.quality,
                "n": request.parameters.n,
                "prompt": request.prompt,
                "output_compression": request.parameters.output_compression,
                "output_format": request.parameters.output_format,
                "image": image_files,
            }

            # Only include mask if it exists
            if masked_image is not None:
                edit_args["mask"] = masked_image

            # Call OpenAI image edit
            result = client.images.edit(**edit_args)

            asset_base64s = []

            for image in result.data:
                image_base64 = image.b64_json

                if not image_base64:
                    continue

                asset_base64s.append(image_base64)

            return ImageResponse(
                asset_base64s=asset_base64s,
                model_response=result.model_dump(),
                model_usage=result.usage.model_dump() if result.usage else None

            )

        except Exception as e:
            logger.error(f"Error editing image: {e}")
            raise e

    def generate_vton_image(self, request: VirtualTryOnRequest) -> ImageResponse:
        try:
            print(request.product_image)
            image_files = [
                OpenAIServiceUtils.url_to_file_safe(request.model_image),
                OpenAIServiceUtils.url_to_file_safe(request.product_image),
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

            asset_b64s = []

            for image in result.data:
                image_base64 = image.b64_json
                if not image_base64:
                    continue
                asset_b64s.append(image_base64)

            return ImageResponse(
                asset_base64s=asset_b64s,
                model_response=result.model_dump(),
                model_usage=result.usage.model_dump() if result.usage else None

            )

        except Exception as e:
            logger.error(f"Error generating virtual try-on image: {e}")
            raise e


class OpenAIServiceUtils:
    @staticmethod
    def url_to_file_safe(url: str):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            file_content = BytesIO(response.content)
            img = Image.open(file_content)
            img_format = img.format.lower()
            print(img_format)

            if img_format not in ["png", "jpeg", "webp"]:
                logger.warning(
                    f"Invalid file format. Converting to image/png"
                )
                # Convert to PNG using Pillow
                try:
                    img = Image.open(file_content).convert("RGBA")
                    converted_content = BytesIO()
                    img.save(converted_content, format="PNG")
                    converted_content.seek(0)
                    file_content = converted_content
                    file_content_type = "image/png"
                    filename = "file.png"
                except Exception as e:
                    logger.error(f"Failed to convert image: {e}")
                    raise
            else:
                ext = img_format.lower()
                file_content_type = f"image/{ext}"
                filename = f"file.{ext}"

            file = (
                filename,
                file_content,
                file_content_type
            )
            return file

        except requests.RequestException as e:
            logger.info(f"Failed to download {url}: {e}")
            return None

    @staticmethod
    def url_to_mask_file_safe(url: str) -> Optional[BytesIO]:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            img = Image.open(BytesIO(response.content))

            # 1. Load your black & white mask as a grayscale image
            mask = img.convert("L")

            mask_inverted = ImageOps.invert(mask)

            # 2. Convert it to RGBA so it has space for an alpha channel
            mask_rgba = mask_inverted.convert("RGBA")

            # 3. Then use the mask itself to fill that alpha channel
            mask_rgba.putalpha(mask_inverted)

            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            buf.name = "mask.png"
            return buf

        except Exception as e:
            logger.info(f"Failed to validate or convert mask image: {e}")
            return None
