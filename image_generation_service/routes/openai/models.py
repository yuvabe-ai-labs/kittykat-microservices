from enum import Enum
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class OpenAIImageGenerationParameters(BaseModel):
    size: Optional[Literal["1024x1024", "1024x1536", "1536x1024"]] = "1024x1024"
    quality: Optional[Literal["high", "medium", "low"]] = "high"
    output_format: Optional[Literal["jpeg", "png", "webp"]] = "webp"
    background: Optional[Literal["auto", "opaque", "transparent"]] = "auto"
    moderation: Optional[Literal["auto", "low"]] = "auto"  # Only used in generate, not edit
    output_compression: Optional[int] = Field(100, ge=0, le=100)
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
    bucket_path: str  


class ImageEditRequest(BaseModel):
    model: OpenAIImageGenerationModels
    prompt: str
    image_base64: Optional[str] = None
    image_base64_list: Optional[List[str]] = None
    image_url: Optional[str] = None
    mask_base64: Optional[str] = None
    parameters: OpenAIImageGenerationParameters
    bucket: str
    bucket_path: str

    def validate(self):
      if self.prompt is None and not self.image_base64 and not self.image_base64_list and not self.image_url:
        raise ValueError(
            "At least one of 'prompt', 'image_base64', 'image_base64_list', or 'image_url' must be provided."
        )

