
from core.models import VideoResponse
from fastapi import APIRouter
from routes.byteplus.models import BytePlusVideoGenerationRequest
from routes.byteplus.service import BytePlusVideoGenerationService
from utils.logger import logger
from utils.utils import BaseApiResponse

router = APIRouter(prefix="/byteplus")

byte_plus_video_generation_service = BytePlusVideoGenerationService()


@router.post("/generate", response_model=BaseApiResponse[VideoResponse])
async def generate_video_via_byteplus(
    request: BytePlusVideoGenerationRequest
):
    try:
        response = await byte_plus_video_generation_service.generate_video(request)

        return BaseApiResponse(status_code=200, message="Video genration initated successfully", data=response)
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        return BaseApiResponse(status_code=500, message=str(e), data=None)
