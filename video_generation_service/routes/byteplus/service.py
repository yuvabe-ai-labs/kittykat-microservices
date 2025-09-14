from typing import Iterable

from byteplussdkarkruntime import Ark
from byteplussdkarkruntime.types.content_generation.create_task_content_param import \
    CreateTaskContentParam
from config.env import env
from routes.byteplus.models import BytePlusVideoGenerationRequest
from utils.logger import logger

from .constants import model_content_filters
from core.models import VideoResponse


class BytePlusVideoGenerationService:
    def __init__(self):
        self.byteplus_client = Ark(
            api_key=env.BYTEPLUS_API_KEY,
        )

    async def generate_video(self, request: BytePlusVideoGenerationRequest) -> VideoResponse:
        """
        Generate a video using BytePlus SDK based on the provided request parameters.
        Returns the task ID of the created video generation task.
        Webhook will be called when the task is initiated.
        """
        try:
            content: Iterable[CreateTaskContentParam] = []

            # Add text prompt
            content.append(
                {
                    "type": "text",
                    "text": f"{request.prompt} --rs {request.resolution} --rt {request.ratio} --dur {request.duration} --fps {request.framepersecond} --wm {str(request.watermark).lower()} --seed {request.seed} --cf {str(request.camerafixed).lower()}",
                }
            )

            roles = ["first_frame", "last_frame"]

            for role, frame in zip(roles, [request.first_frame, request.last_frame if hasattr(request, "last_frame") else None]):
                if frame:
                    item = {
                        "type": "image_url",
                        "image_url": {"url": str(frame)},
                    }

                    if request.model == "seedance-1-0-lite-i2v-250428":
                        item["role"] = role if request.first_frame else "first_frame"

                    content.append(item)

            # Subtracting 1 for the text prompt
            no_of_reference_images = len(content) - 1
            model = request.model if no_of_reference_images > 0 else request.model.replace(
                "i2v", "t2v")

            if request.content_filter_disabled:
                logger.info(
                    "Changing model configuration: content moderation disabled")

                filtered_model = model_content_filters.get(model, None)

                if filtered_model:
                    model = filtered_model
                    logger.info(f"Model changed to {model}")
                else:
                    logger.info(f"No content filter found for model {model}")

            response = self.byteplus_client.content_generation.tasks.create(
                callback_url=str(request.webhook_url),
                model=model,
                content=content
            )

            res = self.byteplus_client.content_generation.tasks.get(
                task_id=response.id)
            logger.info(f"BytePlus response: {res.usage}")
            return VideoResponse(
                webhook_url=str(request.webhook_url),
                model_response={
                    "task_id": response.id,
                },
            )
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            # TODO: Improve NSFW detection
            is_nsfw = "NSFW" in str(e) or "content moderation" in str(e)

            return VideoResponse(
                error=str(e),
                is_nsfw_detected=is_nsfw,
            )
