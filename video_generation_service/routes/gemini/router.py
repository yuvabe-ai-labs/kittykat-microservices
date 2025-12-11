
from typing import Optional

from core.models import VideoResponse
from fastapi import APIRouter
from utils.logger import logger
from utils.utils import BaseApiResponse
from .service import GeminiVideoGenerationService
from .models import GeminiVideoGenerationRequest


router = APIRouter(prefix="/gemini")

gemini_video_generation_service = GeminiVideoGenerationService()


@router.post("/generate", response_model=BaseApiResponse[VideoResponse])
async def generate_via_gemini(request: GeminiVideoGenerationRequest):
    try:
        if request.model in ['veo-3.1-generate-preview', 'veo-3.1-fast-generate-preview']:
            response = await gemini_video_generation_service.generate_video_veo3_1_suite_models(request)
        else:
            response = await gemini_video_generation_service.generate_video(request)

        return BaseApiResponse(status_code=200, message="Video genration initated successfully", data=response)
    except Exception as e:
        logger.error(f"Error in /gemini/generate: {str(e)}")
        return BaseApiResponse(status_code=500, message=str(e), data=None)
