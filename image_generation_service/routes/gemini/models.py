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
        max_length=2,
        description="List of URLs of reference images to guide the image generation.",
    )


class Imagen4GenerateParams(BaseModel):
    model: Literal["imagen-4.0-generate-001"]
    prompt: str = Field(...,
                        description="The text prompt to generate the image.", max_length=1900)
    n: int = Field(
        1, ge=1, le=4, description="Number of images to generate.")
    image_size: Literal["1K", "2K"] = Field(
        "1K", description="Size of the generated images.")
    aspect_ratio: Literal["1:1", "3:4", "4:3", "9:16", "16:9"] = Field(
        "1:1", description="Aspect ratio of the generated images."
    )


class Imagen4UltraGenerateParams(BaseModel):
    model: Literal["imagen-4.0-ultra-generate-001"]
    prompt: str = Field(...,
                        description="The text prompt to generate the image.", max_length=1900)
    n: int = Field(
        1, ge=1, le=4, description="Number of images to generate.")
    image_size: Literal["1K", "2K"] = Field(
        "1K", description="Size of the generated images.")
    aspect_ratio: Literal["1:1", "3:4", "4:3", "9:16", "16:9"] = Field(
        "1:1", description="Aspect ratio of the generated images."
    )


class Imagen4FastGenerateParams(BaseModel):
    model: Literal["imagen-4.0-fast-generate-001"]
    prompt: str = Field(...,
                        description="The text prompt to generate the image.", max_length=1900)
    n: int = Field(
        1, ge=1, le=4, description="Number of images to generate.")
    aspect_ratio: Literal["1:1", "3:4", "4:3", "9:16", "16:9"] = Field(
        "1:1", description="Aspect ratio of the generated images."
    )


GeminiImageGenerationRequest = Union[Gemini_2_5_Flash_Image_Preview,
                                     Imagen4GenerateParams,
                                     Imagen4UltraGenerateParams,
                                     Imagen4FastGenerateParams]
GeminiImageEditRequest = Union[Gemini_2_5_Flash_Image_Preview_Edit]


class GeminiVirtualTryOnRequest(BaseModel):
    model: Literal["gemini-2.5-flash-image-preview"]
    prompt: Optional[str] = None
    model_image: str
    product_image: str
