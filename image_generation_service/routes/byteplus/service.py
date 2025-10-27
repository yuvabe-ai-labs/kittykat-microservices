import base64
import io

import requests
from byteplussdkarkruntime import Ark
from byteplussdkarkruntime._exceptions import ArkBadRequestError
from config.env import config
from config.logger import logger
from core.models import ImageResponse
from PIL import Image
from routes.byteplus.constants import (BYTEPLUS_NFSW_ERROR_CODES,
                                       model_content_filters)
from routes.byteplus.models import (BytePlusImageEditRequest,
                                    BytePlusImageGenerationRequest,
                                    Seedream4Params)


class BytePlusService:
    def __init__(self):
        self.byteplus_client = Ark(
            api_key=config.BYTEPLUS_API_KEY
        )

    def generate_image(self, request: BytePlusImageGenerationRequest) -> ImageResponse:
        try:
            model = request.model

            if request.content_filter_disabled:
                logger.info(
                    "Changing model configuration: content moderation disabled")

                filtered_model = model_content_filters.get(model, None)

                if filtered_model:
                    model = filtered_model
                    logger.info(f"Model changed to {model}")
                else:
                    logger.info(f"No content filter found for model {model}")

            result = self.byteplus_client.images.generate(
                model=model,
                prompt=request.prompt,
                size=request.size,
                guidance_scale=request.guidance_scale,
                seed=request.seed,
                watermark=request.watermark,
                response_format="url",
            )

            logger.info(
                f"BytePlus image generation result:  {result.model_dump()}")

            if result.data is None or len(result.data) == 0:
                return ImageResponse(
                    error=result.error.model_dump() if result.error else "Unknown error",
                    is_nsfw_detected=result.error.code in BYTEPLUS_NFSW_ERROR_CODES if result.error else False,
                    model_response=result.model_dump()
                )

            return ImageResponse(
                asset_urls=[result.data[0].url],
                model_response=result.model_dump(),
                model_usage=result.usage.model_dump() if result.usage else None
            )
        except ArkBadRequestError as e:
            logger.error(f"BytePlus BadRequestError: {e}")
            return ImageResponse(
                error=str(e),
                is_nsfw_detected=e.code in BYTEPLUS_NFSW_ERROR_CODES if e.code else False,
            )
        except Exception as e:
            logger.error(f"Error generating image using {request.model}: {e}")
            return ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
            )

    def edit_image(self, request: BytePlusImageEditRequest) -> ImageResponse:
        try:
            model = request.model
            if request.content_filter_disabled:
                logger.info(
                    "Changing model configuration: content moderation disabled")

                filtered_model = model_content_filters.get(model, None)

                if filtered_model:
                    model = filtered_model
                    logger.info(f"Model changed to {model}")
                else:
                    logger.info(f"No content filter found for model {model}")

            result = self.byteplus_client.images.generate(
                model=model,
                prompt=request.prompt,
                size=request.size,
                guidance_scale=request.guidance_scale,
                seed=request.seed,
                watermark=request.watermark,
                response_format="url",
                image=BytePlusServiceUtils.convert_url_to_base64_png(
                    request.image)
            )

            logger.info(
                f"BytePlus image edit result:  {result.model_dump()}")

            if result.data is None or len(result.data) == 0:
                return ImageResponse(
                    error=result.error.model_dump() if result.error else "Unknown error",
                    is_nsfw_detected=result.error.code in BYTEPLUS_NFSW_ERROR_CODES if result.error else False,
                    model_response=result.model_dump()
                )

            return ImageResponse(
                asset_urls=[result.data[0].url],
                model_response=result.model_dump(),
                model_usage=result.usage.model_dump() if result.usage else None
            )
        except ArkBadRequestError as e:
            logger.error(f"BytePlus BadRequestError: {e}")
            return ImageResponse(
                error=str(e),
                is_nsfw_detected=e.code in BYTEPLUS_NFSW_ERROR_CODES if e.code else False,
            )
        except Exception as e:
            logger.error(f"Error remixing image using {request.model}: {e}")
            return ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
            )

    def generate_image_with_seedream_4(self, request: Seedream4Params) -> ImageResponse:
        try:
            logger.info(
                f"Generating image with Seedream 4 model. Payload: {request.model_dump()}")
            model = request.model

            if request.content_filter_disabled:
                logger.info(
                    "Changing model configuration: content moderation disabled")

                filtered_model = model_content_filters.get(model, None)

                if filtered_model:
                    model = filtered_model
                    logger.info(f"Model changed to {model}")
                else:
                    logger.info(
                        f"No content filter found for model {model}")

            url = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.BYTEPLUS_API_KEY}"
            }

            # Handle aspect ratio in prompt
            prompt = request.prompt
            if request.aspect_ratio.lower() != "auto":
                prompt = f"{prompt} in aspect ratio {request.aspect_ratio}."

            payload = {
                "model": model,
                "prompt": prompt,
                "size": request.size,
                "seed": request.seed,
                "watermark": request.watermark,
                "response_format": "url",
                "image": [BytePlusServiceUtils.convert_url_to_base64_png(img) for img in request.image] if request.image else None,
                "sequential_image_generation": request.sequential_image_generation,
                "stream": request.stream,
                "sequential_image_generation_options": {
                    "max_images": request.max_images
                },
            }

            response = requests.post(
                url, headers=headers, json=payload, timeout=600)

            if response.status_code != 200:
                logger.error(
                    f"Error in Seedream 4 HTTP response: {response.status_code} - {response.text}")

                if response.status_code == 400:
                    response = response.json()
                    error = response.get("error", {})
                    return ImageResponse(
                        error=response,
                        is_nsfw_detected=True if error.get(
                            "code") in BYTEPLUS_NFSW_ERROR_CODES else False,
                    )
                else:
                    return ImageResponse(
                        error=f"HTTP {response.status_code}: {response.text}",
                        is_nsfw_detected=False,
                    )

            result = response.json()

            if "data" not in result or not result["data"]:
                logger.error(
                    f"Error in Seedream 4 response: {result}")
                data = result.get("data", {})
                return ImageResponse(
                    error=data.get("error", "Unknown error"),
                    is_nsfw_detected=(
                        data.get("error", {}).get(
                            "code") in BYTEPLUS_NFSW_ERROR_CODES
                        if "error" in data else False
                    ),
                )

            return ImageResponse(
                asset_urls=[item["url"] for item in result["data"]],
                model_response=result,
                model_usage=result.get("usage"),
            )

        except Exception as e:
            logger.error(f"Error generating image with Seedream 4: {e}")
            return ImageResponse(
                error=str(e),
                is_nsfw_detected=False,
                model_response=None
            )


class BytePlusServiceUtils:
    @staticmethod
    def convert_url_to_base64_png(url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Open with PIL and convert to PNG
            image = Image.open(io.BytesIO(response.content))
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)

            # Convert to base64
            b64_string = base64.b64encode(buffer.read()).decode("utf-8")
            return f"data:image/png;base64,{b64_string}"

        except Exception as e:
            logger.error(f"Error converting URL to base64 PNG: {e}")
            raise e
