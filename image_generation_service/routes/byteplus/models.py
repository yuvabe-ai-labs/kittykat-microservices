from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator


class BaseParams(BaseModel):
    content_filter_disabled: Optional[bool] = Field(
        default=False,
        description="Whether to disable content filtering. Default is False.",
    )


class Seeddream_3_Params(BaseParams):
    model: Literal["seedream-3-0-t2i-250415"]
    prompt: str
    size: Literal[
        "1024x1024", "864x1152", "1152x864", "1280x720", "720x1280", "832x1248", "1248x832", "1512x648"
    ] = Field(
        default="1024x1024",
        description="Size of the generated image. Options are '512x512', '768x768', '1024x1024'.",
    )
    guidance_scale: float = Field(
        default=2.5,
        description="Guidance scale for image generation. Higher values result in images that are more closely aligned with the prompt.",
        ge=1.0,
        le=10.0,
    )
    seed: Optional[int] = Field(
        default=-1,
        description="Seed for random number generator. Use -1 for random seed.",
    )
    watermark: Optional[bool] = Field(
        default=False,
        description="Whether to add a watermark to the generated image.",
    )


class SeedEdit_3_Params(BaseParams):
    model: Literal["seededit-3-0-i2i-250628"]
    prompt: str
    image: str = Field(
        ...,
        description="Base64 encoded image or image URL to be edited.",
    )
    size: Literal[
        "adaptive"
    ] = Field(
        default="adaptive",
        description="Size of the generated image. Options are 'adaptive' for noe.",
    )
    guidance_scale: float = Field(
        default=2.5,
        description="Guidance scale for image generation. Higher values result in images that are more closely aligned with the prompt.",
        ge=1.0,
        le=10.0,
    )
    seed: Optional[int] = Field(
        default=-1,
        description="Seed for random number generator. Use -1 for random seed.",
    )
    watermark: Optional[bool] = Field(
        default=False,
        description="Whether to add a watermark to the generated image.",
    )


class Seedream4Params(BaseParams):
    model: Literal["seedream-4-0-250828"]
    prompt: str
    image: Optional[List[str]] = Field(
        default=None,
        description="List of base64 encoded images or image URLs to be used as references.",
        max_items=10,
    )
    size: Literal["1K", "2K", "4K", "2048x2048", "2304x1728", "1728x2304", "2560x1440", "1440x2560", "2496x1664", "1664x2496", "3024x1296"] = Field(
        default="1K",
        description="Size of the generated image. Options are '1K', '2K', '4K'.",
    )
    seed: int = Field(
        default=-1,
        description="Seed for random number generator. Use -1 for random seed.",
    )
    max_images: Optional[int] = Field(
        default=None,
        description="Maximum number of images to generate. Default is 1. Max is 15.",
        ge=1,
        le=15,
    )
    sequential_image_generation: Literal["auto", "disabled"] = Field(
        default="disabled",
        description="Whether to use sequential image generation. Options are 'auto' and 'disabled'. Default is 'auto'.",
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response. Default is False.",
    )
    watermark: bool = Field(
        default=False,
        description="Whether to add a watermark to the generated image. Default is False.",
    )
    aspect_ratio: Literal["auto", "1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"] = Field(
        "auto", description="Aspect ratio of the generated images."
    )
    optimize_prompt_options: Optional[bool] = Field(
        default=False,
        description="Whether to optimize the prompt for better generation results"
    )

    @model_validator(mode="after")
    def check_total_images(cls, values: "Seedream4Params"):
        total = len(values.image or []) + (values.max_images or 0)
        if total > 15:
            raise ValueError(
                f"Total images (references + generated) cannot exceed 15. Got {total}."
            )
        return values


class Seedream45Params(BaseParams):
    model: Literal["seedream-4-5-251128"]
    prompt: str
    image: Optional[List[str]] = Field(
        default=None,
        description="List of base64 encoded images or image URLs to be used as references.",
        max_items=14,
    )
    size: Literal["2K", "4K", "2048x2048", "2304x1728", "1728x2304", "2560x1440", "1440x2560", "2496x1664", "1664x2496", "3024x1296"] = Field(
        default="2K",
        description="Size of the generated image. Options are '1K', '2K', '4K'.",
    )
    seed: int = Field(
        default=-1,
        description="Seed for random number generator. Use -1 for random seed.",
    )
    max_images: Optional[int] = Field(
        default=None,
        description="Maximum number of images to generate. Default is 1. Max is 15.",
        ge=1,
        le=15,
    )
    sequential_image_generation: Literal["auto", "disabled"] = Field(
        default="disabled",
        description="Whether to use sequential image generation. Options are 'auto' and 'disabled'. Default is 'auto'.",
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response. Default is False.",
    )
    watermark: bool = Field(
        default=False,
        description="Whether to add a watermark to the generated image. Default is False.",
    )
    aspect_ratio: Literal["auto", "1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"] = Field(
        "auto", description="Aspect ratio of the generated images."
    )
    optimize_prompt_options: Optional[bool] = Field(
        default=False,
        description="Whether to optimize the prompt for better generation results"
    )

    @model_validator(mode="after")
    def check_total_images(cls, values: "Seedream4Params"):
        total = len(values.image or []) + (values.max_images or 0)
        if total > 15:
            raise ValueError(
                f"Total images (references + generated) cannot exceed 15. Got {total}."
            )
        return values


class Seedream_5_0_Lite_Params(BaseParams):
    model: Literal["seedream-5-0-260128"]
    prompt: str
    image: Optional[List[str]] = Field(
        default=None,
        description="List of base64 encoded images or image URLs to be used as references.",
        max_items=14,
    )
    size: Literal["2K", "3K", "2048x2048", "2304x1728", "1728x2304", "2560x1440", "1440x2560", "2496x1664", "1664x2496", "3024x1296"] = Field(
        default="2K",
        description="Size of the generated image. Options are '2K', '3K'.",
    )
    seed: int = Field(
        default=-1,
        description="Seed for random number generator. Use -1 for random seed.",
    )
    max_images: Optional[int] = Field(
        default=None,
        description="Maximum number of images to generate. Default is 1. Max is 15.",
        ge=1,
        le=15,
    )
    sequential_image_generation: Literal["auto", "disabled"] = Field(
        default="disabled",
        description="Whether to use sequential image generation. Options are 'auto' and 'disabled'. Default is 'auto'.",
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response. Default is False.",
    )
    watermark: bool = Field(
        default=False,
        description="Whether to add a watermark to the generated image. Default is False.",
    )
    aspect_ratio: Literal["auto", "1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"] = Field(
        "auto", description="Aspect ratio of the generated images."
    )
    optimize_prompt_options: Optional[bool] = Field(
        default=False,
        description="Whether to optimize the prompt for better generation results"
    )

    @model_validator(mode="after")
    def check_total_images(cls, values):
        total = len(values.image or []) + (values.max_images or 0)
        if total > 15:
            raise ValueError(
                f"Total images (references + generated) cannot exceed 15. Got {total}.")
        return values


BytePlusImageGenerationRequest = Union[Seeddream_3_Params,
                                       Seedream4Params, Seedream45Params, Seedream_5_0_Lite_Params]
BytePlusImageEditRequest = Union[SeedEdit_3_Params,
                                 Seedream4Params, Seedream45Params]
