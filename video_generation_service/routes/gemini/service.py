import asyncio
import uuid
from config.env import env
from utils.logger import logger
from core.models import VideoResponse
from google import genai
from google.genai.types import GenerateVideosConfig, GenerateVideosSourceDict, VideoGenerationReferenceImage, VideoGenerationReferenceType, Image

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
                image = await GeminiServiceUtils.convert_url_to_image_bytes(
                    str(request.image))
            else:
                image = None

            operation = await self.gemini_client.aio.models.generate_videos(
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
                logger.info("Waiting for video generation to complete...")
                await asyncio.sleep(10)
                operation = await self.gemini_client.aio.operations.get(operation)

            if operation.error or operation.response.rai_media_filtered_reasons:
                return VideoResponse(
                    error=operation.error,
                    # Assuming NSFW detection is not applicable in case of an error
                    is_nsfw_detected=True,
                )

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

    async def generate_video_veo3_1_suite_models(self, request: GeminiVideoGenerationRequest) -> VideoResponse:
        try:
            first_frame = {
                "image_bytes": await GeminiServiceUtils.convert_url_to_image_bytes(
                    str(request.first_frame)),
                "mime_type": "image/png",
            } if request.first_frame else None

            last_frame = {
                "image_bytes": await GeminiServiceUtils.convert_url_to_image_bytes(
                    str(request.last_frame)),
                "mime_type": "image/png",
            } if request.last_frame else None

            # If only last_frame is provided, use it as first_frame as well
            if last_frame and not first_frame:
                first_frame = last_frame
                last_frame = None

            reference_images = [
                VideoGenerationReferenceImage(
                    image=Image(
                        image_bytes=await GeminiServiceUtils.convert_url_to_image_bytes(
                            str(url)
                        ),
                        mime_type="image/png",
                    ),
                    reference_type="ASSET"
                )
                for url in request.reference_images
            ] if request.reference_images else None

            operation = await self.gemini_client.aio.models.generate_videos(
                model=request.model,
                config=GenerateVideosConfig(
                    last_frame=last_frame,
                    reference_images=reference_images,
                    negative_prompt=getattr(
                        request, "negative_prompt", None),
                    resolution=getattr(request, "resolution", None),
                    aspect_ratio=request.aspect_ratio,
                    duration_seconds=request.duration
                ),
                image=first_frame,
                prompt=request.prompt,
            )

            # Poll the operation status until the video is ready.
            while not operation.done:
                logger.info("Waiting for video generation to complete...")
                await asyncio.sleep(10)
                operation = await self.gemini_client.aio.operations.get(operation)

            if operation.error or operation.response.rai_media_filtered_reasons:
                return VideoResponse(
                    error=operation.error,
                    # Assuming NSFW detection is not applicable in case of an error
                    is_nsfw_detected=True,
                )

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
