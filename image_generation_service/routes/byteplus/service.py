import os
from byteplussdkarkruntime import Ark
from config.logger import logger
from core.models import ImageResponse
from routes.byteplus.constants import BYTEPLUS_NFSW_ERROR_CODES
from routes.byteplus.models import BytePlusImageGenerationRequest, BytePlusImageEditRequest
from routes.byteplus.constants import model_content_filters


class BytePlusService:
    def __init__(self):
        self.byteplus_client = Ark(
            api_key=os.environ.get("BYTEPLUS_API_KEY")
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
            model_response=result.model_dump()
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
            model_response=result.model_dump()
        )
