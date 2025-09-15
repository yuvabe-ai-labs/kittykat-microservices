import time
import uuid
from config.env import env
from utils.logger import logger
from core.models import VideoResponse
from google import genai
from google.genai.types import GenerateVideosConfig, GenerateVideosSourceDict

from .models import GeminiVideoGenerationRequest
from .utils import GeminiServiceUtils


class GeminiVideoGenerationService:
    def __init__(self):
        self.gemini_client = genai.Client(
            api_key=env.GEMINI_API_KEY
        )

    async def generate_video(self, request: GeminiVideoGenerationRequest) -> VideoResponse:
        try:

            if request.image:
                image = GeminiServiceUtils.convert_url_to_image_bytes(
                    str(request.image))
            else:
                image = None

            operation = self.gemini_client.models.generate_videos(
                model=request.model,
                config=GenerateVideosConfig(
                    negative_prompt=getattr(request, "negative_prompt", None),
                    resolution=getattr(request, "resolution", None),
                    aspect_ratio=request.aspect_ratio,
                    duration_seconds=request.duration
                ),
                source=GenerateVideosSourceDict(
                    prompt=request.prompt,
                    image={
                        "image_bytes": image,
                        "mime_type": "image/png" if image else None,
                    } if image else None,
                )
            )

            # Poll the operation status until the video is ready.
            while not operation.done:
                print("Waiting for video generation to complete...")
                time.sleep(10)
                operation = self.gemini_client.operations.get(operation)

            video = operation.response.generated_videos[0]

            return VideoResponse(
                asset_urls=[video.video.uri],
                model_response=operation.response.model_dump(),
            )

        except Exception as e:
            logger.error(f"Error generating video via Gemini: {e}")

            return VideoResponse(
                error=str(e),
                is_nsfw_detected=False,
            )
