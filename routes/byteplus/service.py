from byteplussdkarkruntime import Ark
import requests
from config.logger import logger
from core.models import ImageResponse
from config.env import config
from routes.byteplus.constants import BYTEPLUS_NFSW_ERROR_CODES
from routes.byteplus.models import BytePlusImageGenerationRequest, BytePlusImageEditRequest, Seedream4Params
from routes.byteplus.constants import model_content_filters


class BytePlusService:
    def __init__(self):
        self.byteplus_client = Ark(
            api_key=config.BYTEPLUS_API_KEY
        )

    def generate_image(self, request: BytePlusImageGenerationRequest) -> ImageResponse:
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

    def edit_image(self, request: BytePlusImageEditRequest) -> ImageResponse:
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
            image=request.image
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

    def generate_image_with_seedream_4(self, request: Seedream4Params) -> ImageResponse:
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

        url = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.BYTEPLUS_API_KEY}"
        }

        payload = {
            "model": model,
            "prompt": request.prompt,
            "size": request.size,
            "seed": request.seed,
            "watermark": request.watermark,
            "response_format": "url",
            "image": request.image,
            "sequential_image_generation": request.sequential_image_generation,
            "stream": request.stream,
            "sequential_image_generation_options": {
                "max_images": request.max_images
            },
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            return ImageResponse(
                error=f"HTTP {response.status_code}: {response.text}",
                is_nsfw_detected=False,
                model_response=response.text
            )

        result = response.json()

        if "data" not in result or not result["data"]:
            return ImageResponse(
                error=result.get("error", "Unknown error"),
                is_nsfw_detected=(
                    result.get("error", {}).get(
                        "code") in BYTEPLUS_NFSW_ERROR_CODES
                    if "error" in result else False
                ),
                model_response=result
            )

        return ImageResponse(
            asset_urls=[item["url"] for item in result["data"]],
            model_response=result,
            model_usage=result.get("usage"),
        )
