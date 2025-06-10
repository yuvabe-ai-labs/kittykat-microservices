from enum import Enum
from typing import Annotated, List, Literal, Optional
from pydantic import BaseModel, Field, StringConstraints, conlist, field_validator


class OpenAIImageGenerationParameters(BaseModel):
    size: Optional[Literal["1024x1024",
                           "1024x1536", "1536x1024"]] = "1024x1024"
    quality: Optional[Literal["high", "medium", "low"]] = "high"
    output_format: Optional[Literal["jpeg", "png", "webp"]] = "webp"
    background: Optional[Literal["auto", "opaque", "transparent"]] = "auto"
    # Only used in generate, not edit
    moderation: Optional[Literal["auto", "low"]] = "auto"
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
    base_image: str
    reference_images: Optional[List[str]] = None
    mask_image: Optional[str] = None
    parameters: OpenAIImageGenerationParameters
    bucket: str
    bucket_path: str

    @field_validator("reference_images")
    def validate_reference_images_max_length(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError("reference_images can contain at most 10 URLs")
        return v
