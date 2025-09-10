from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


class BaseImageModel(BaseModel):
    prompt: str = Field(
        ...,
        description="The text prompt to generate the image.",
    )


class Gemini_2_5_Flash_Image_Preview(BaseImageModel):
    model: Literal["gemini-2.5-flash-image-preview"] = Field(
        "gemini-2.5-flash-image-preview",
        description="The model to use for image generation.",
    )
    reference_images: Optional[List[str]] = Field(
        default=None,
        min_length=1,
        max_length=3,
        description="List of URLs of reference images to guide the image generation.",
    )


class Gemini_2_5_Flash_Image_Preview_Edit(BaseImageModel):
    model: Literal["gemini-2.5-flash-image-preview"] = Field(
        "gemini-2.5-flash-image-preview",
        description="The model to use for image generation.",
    )
    base_image: str = Field(
        ...,
        description="URL of the base image to be edited.",
    )
    reference_images: Optional[List[str]] = Field(
        default=None,
        min_length=1,
        max_length=2,
        description="List of URLs of reference images to guide the image generation.",
    )


GeminiImageGenerationRequest = Union[Gemini_2_5_Flash_Image_Preview]
GeminiImageEditRequest = Union[Gemini_2_5_Flash_Image_Preview_Edit]
