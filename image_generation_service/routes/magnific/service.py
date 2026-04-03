from core.service import ImageUtilsService
from config.env import config
import httpx
from .models import ImageUpscaleRequest
from core.models import ImageResponse

MAGNIFIC_API_URL = "https://api.freepik.com/v1/ai/image-upscaler"


class ImageUpscaleService:
    def __init__(self):
        pass

    async def call_magnific_api(self, request: ImageUpscaleRequest):

        image_base64 = ImageUtilsService.convert_url_to_base64(
            url=request.image_url)

        payload = {
            "image": image_base64,
            "scale_factor": request.scale_factor,
            "optimized_for": request.optimized_for,
            "webhook_url": request.webhook_url,
            "prompt": request.prompt,
            "creativity": request.creativity,
            "hdr": request.hdr,
            "resemblance": request.resemblance,
            "fractality": request.fractality,
            "engine": request.engine
        }

        headers = {
            "x-freepik-api-key": config.FREEPIK_API_KEY,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=600) as client:
            resp = await client.post(MAGNIFIC_API_URL, json=payload, headers=headers)

        if resp.status_code != 200:
            raise RuntimeError(f"Magnific API returned error: {resp.text}")

        return ImageResponse(
            webhook_url=request.webhook_url,
            model_response=resp.json()
        )
