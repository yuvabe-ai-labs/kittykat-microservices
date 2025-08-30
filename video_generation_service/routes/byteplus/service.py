from typing import Iterable
from byteplussdkarkruntime import Ark

from byteplussdkarkruntime.types.content_generation.create_task_content_param import CreateTaskContentParam
from video_generation_service.config.settings import config
from video_generation_service.routes.byteplus.models import BytePlusVideoGenerationRequest
from video_generation_service.utils.logger import logger


class BytePlusVideoGenerationService:
    def __init__(self):
        self.byteplus_client = Ark(
            api_key=config.BYTEPLUS_API_KEY,
        )

    def generate_video(self, request: BytePlusVideoGenerationRequest) -> str:
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

            # Add first frame image
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": request.first_frame,
                    },
                    "role": "first_frame",
                }
            )

            # Add last frame image if provided
            if request.last_frame:
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": request.last_frame,
                        },
                        "role": "last_frame",
                    }
                )

            response = self.byteplus_client.content_generation.tasks.create(
                callback_url=str(request.webhook_url),
                model=request.model,
                content=content
            )

            return response.id
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            raise e
