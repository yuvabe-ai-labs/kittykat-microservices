import os
from byteplussdkarkruntime import Ark
from config.logger import logger
from routes.byteplus.constants import BYTEPLUS_NFSW_ERROR_CODES
from routes.byteplus.models import BytePlusImageGenerationRequest, BytePlusImageGenerationResponse


class BytePlusService:
    def __init__(self):
        self.byteplus_client = Ark(
            api_key=os.environ.get("BYTEPLUS_API_KEY")
        )

    def generate_image(self, request: BytePlusImageGenerationRequest) -> BytePlusImageGenerationResponse:
        result = self.byteplus_client.images.generate(
            model=request.model,
            prompt=request.prompt,
            size=request.size,
            guidance_scale=request.guidance_scale,
            seed=request.seed,
            watermark=request.watermark,
            response_format="url",
        )

        logger.info(f"BytePlus image generation result: {result.model_dump()}")

        if result.data is None or len(result.data) == 0:
            return BytePlusImageGenerationResponse(
                asset_urls=None,
                error=result.error.model_dump() if result.error else "Unknown error",
                is_nsfw_detected=result.error.code in BYTEPLUS_NFSW_ERROR_CODES if result.error else False,
                model_response=result.model_dump()
            )

        return BytePlusImageGenerationResponse(
            asset_urls=[result.data[0].url],
            error=None,
            is_nsfw_detected=False,
            model_response=result.model_dump()
        )
