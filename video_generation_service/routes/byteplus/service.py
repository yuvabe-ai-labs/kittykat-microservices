from typing import Iterable
from byteplussdkarkruntime import Ark

from byteplussdkarkruntime.types.content_generation.create_task_content_param import CreateTaskContentParam
from config.settings import config
from routes.byteplus.models import BytePlusVideoGenerationRequest
from utils.logger import logger


class BytePlusVideoGenerationService:
    def __init__(self):
        self.byteplus_client = Ark(
            api_key=config.BYTEPLUS_API_KEY,
        )

    async def generate_video(self, request: BytePlusVideoGenerationRequest) -> str:
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
            print("boomer1")
            # Add first frame image
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": str(request.first_frame),
                    },
                    "role": "first_frame",
                }
            )
            print("boomer2")

            # Add last frame image if provided
            if request.model == "seedance-1-0-lite-i2v-250428" and request.last_frame:
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": str(request.last_frame),
                        },
                        "role": "last_frame",
                    }
                )

            print("boomer3")
            response = self.byteplus_client.content_generation.tasks.create(
                callback_url=str(request.webhook_url),
                model=request.model,
                content=content
            )

            print("boomer4")

            return response.id
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            raise e
