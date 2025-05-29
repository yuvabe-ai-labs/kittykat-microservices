from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from pydantic import BaseModel


class OpenAIImageGenerationParameters(BaseModel):
    size: Optional[Literal["1024x1024",
                           "1024x1536", "1536x1024"]] = "1024x1024"
    quality: Optional[Literal["high", "medium", "low"]] = "high"
    output_format: Optional[Literal["jpeg", "png", "webp"]] = "webp"
    background: Optional[Literal["auto", "opaque", "transparent"]] = "auto"
    moderation: Optional[Literal["auto", "low"]] = "auto"
    output_compression: Optional[int] = Field(
        100, ge=0, le=100)
    n: Optional[int] = Field(
        1, ge=1, le=10, description="Number of images to generate (1-10). Default is 1."
    )


class OpenAIImageGenerationModels(str, Enum):
    GPT_IMAGE_1 = "gpt-image-1"


class ImageGenerationRequest(BaseModel):
    model: OpenAIImageGenerationModels
    prompt: str
    parameters: OpenAIImageGenerationParameters
    bucket: str
    bukcet_path: str
