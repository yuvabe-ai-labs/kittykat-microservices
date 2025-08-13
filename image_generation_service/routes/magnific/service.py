import base64
import os
import httpx
from .models import ImageUpscaleRequest
from ..openai.service import ImageService
from dotenv import load_dotenv

MAGNIFIC_API_URL = "https://api.freepik.com/v1/ai/image-upscaler"

load_dotenv()

FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY")


class ImageUpscaleService:
    @staticmethod
    async def call_magnific_api(request: ImageUpscaleRequest) -> dict:

        print("freepik api key", FREEPIK_API_KEY)
        # Fetch image as (filename, BytesIO, content_type)
        image_tuple = ImageService.url_to_file_safe(request.image_url)
        if not image_tuple:
            raise ValueError(
                "Unable to fetch or process the image from the provided URL.")

        _, file_content, _ = image_tuple
        image_base64 = base64.b64encode(
            file_content.getvalue()).decode("utf-8")

        print("request", request.model_dump())

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
            "x-freepik-api-key": FREEPIK_API_KEY,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(MAGNIFIC_API_URL, json=payload, headers=headers)

        if resp.status_code != 200:
            raise RuntimeError(f"Magnific API returned error: {resp.text}")

        return resp.json()
