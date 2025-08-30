
from fastapi import APIRouter

from routes.byteplus.models import BytePlusVideoGenerationRequest
from routes.byteplus.service import BytePlusVideoGenerationService
from utils.utils import BaseApiResponse
from utils.logger import logger


router = APIRouter(prefix="/byteplus")

byte_plus_video_generation_service = BytePlusVideoGenerationService()


@router.post("/generate-video", response_model=BaseApiResponse)
async def generate_video_via_byteplus(
    request: BytePlusVideoGenerationRequest
):
    try:
        task_id = await byte_plus_video_generation_service.generate_video(request)

        return BaseApiResponse(status_code=200, message="Video genration initated successfully", data={"task_id": task_id})
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        return BaseApiResponse(status_code=500, message=str(e), data=None)
