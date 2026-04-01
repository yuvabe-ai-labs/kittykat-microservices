import asyncio
import base64
from io import BytesIO
from typing import List, Optional

import requests
from config.logger import logger
from core.models import ImageResponse
from PIL import Image, ImageOps
from services.gcp import upload_base64_to_gcp
from utils.helpers import openai_retry

from .config import client
from .constants import VIRTUAL_TRY_ON_BASE_PROMPT
from .models import (ImageEditRequest, ImageGenerationRequest,
                     VirtualTryOnRequest)


class OpenAIService:
    @staticmethod
    async def _upload_base64s(base64_list: List[str]) -> List[str]:
        return await asyncio.gather(
            *[asyncio.to_thread(upload_base64_to_gcp, b64) for b64 in base64_list]
        )

    @openai_retry
    async def generate_image(self, request: ImageGenerationRequest) -> ImageResponse:
        try:
            content = [
                {"type": "input_image", "image_url": url}
                for url in (request.reference_images or [])
            ]
            content.append({"type": "input_text", "text": request.prompt})

            tool = {
                "type": "image_generation",
                "model": "gpt-image-1",
                "size": request.parameters.size,
                "quality": request.parameters.quality,
                "background": request.parameters.background,
                "output_format": request.parameters.output_format,
                "output_compression": request.parameters.output_compression,
                "moderation": request.parameters.moderation,
            }

            result = await client.responses.create(
                model="gpt-4o",
                input=[{"role": "user", "content": content}],
                tools=[tool],
                tool_choice={"type": "image_generation"},
            )

            asset_b64s = [
                item.result
                for item in result.output
                if item.type == "image_generation_call" and item.result
            ]

            asset_urls = await self._upload_base64s(asset_b64s)

            return ImageResponse(
                asset_urls=asset_urls,
                model_response=result.model_dump(),
                model_usage=result.usage.model_dump() if result.usage else None
            )

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise e

    @openai_retry
    async def edit_image(self, request: ImageEditRequest) -> ImageResponse:
        try:
            content = [{"type": "input_image",
                        "image_url": request.base_image}]
            for url in (request.reference_images or []):
                content.append({"type": "input_image", "image_url": url})
            content.append({"type": "input_text", "text": request.prompt})

            tool = {
                "type": "image_generation",
                "model": "gpt-image-1",
                "size": request.parameters.size,
                "quality": request.parameters.quality,
                "background": request.parameters.background,
                "output_format": request.parameters.output_format,
                "output_compression": request.parameters.output_compression,
            }

            if request.mask_image:
                mask_b64 = await asyncio.to_thread(
                    OpenAIServiceUtils.url_to_mask_b64_safe, request.mask_image
                )
                if mask_b64:
                    tool["input_image_mask"] = {"image_url": mask_b64}

            result = await client.responses.create(
                model="gpt-4o",
                input=[{"role": "user", "content": content}],
                tools=[tool],
                tool_choice={"type": "image_generation"}
            )

            asset_base64s = [
                item.result
                for item in result.output
                if item.type == "image_generation_call" and item.result
            ]

            asset_urls = await self._upload_base64s(asset_base64s)

            return ImageResponse(
                asset_urls=asset_urls,
                model_response=result.model_dump(),
                model_usage=result.usage.model_dump() if result.usage else None
            )

        except Exception as e:
            logger.error(f"Error editing image: {e}")
            raise e

    @openai_retry
    async def generate_vton_image(self, request: VirtualTryOnRequest) -> ImageResponse:
        try:
            prompt = VIRTUAL_TRY_ON_BASE_PROMPT
            if request.prompt:
                prompt += f"\nAdditional instructions: {request.prompt}"

            content = [
                {"type": "input_image", "image_url": request.model_image},
                {"type": "input_image", "image_url": request.product_image},
                {"type": "input_text", "text": prompt},
            ]

            tool = {
                "type": "image_generation",
                "model": "gpt-image-1",
                "size": request.parameters.size,
                "quality": request.parameters.quality,
                "background": "auto",
                "output_format": request.parameters.output_format,
                "output_compression": request.parameters.output_compression,
            }

            result = await client.responses.create(
                model="gpt-4o",
                input=[{"role": "user", "content": content}],
                tools=[tool],
                tool_choice={"type": "image_generation"}
            )

            asset_b64s = [
                item.result
                for item in result.output
                if item.type == "image_generation_call" and item.result
            ]

            asset_urls = await self._upload_base64s(asset_b64s)

            return ImageResponse(
                asset_urls=asset_urls,
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
    def url_to_mask_b64_safe(url: str) -> Optional[str]:
        """Downloads mask, inverts it, converts to RGBA PNG, returns as base64 data URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            img = Image.open(BytesIO(response.content))
            mask = img.convert("L")
            mask_inverted = ImageOps.invert(mask)
            mask_rgba = mask_inverted.convert("RGBA")
            mask_rgba.putalpha(mask_inverted)

            buf = BytesIO()
            mask_rgba.save(buf, format="PNG")
            buf.seek(0)
            b64 = base64.b64encode(buf.read()).decode("utf-8")
            return f"data:image/png;base64,{b64}"

        except Exception as e:
            logger.info(f"Failed to process mask image: {e}")
            return None
