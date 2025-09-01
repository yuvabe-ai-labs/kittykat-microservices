from typing import Literal, Optional, Union
from pydantic import BaseModel, Field


class Seeddream_3_Params(BaseModel):
    model: Literal["seeddream-3"]
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
    seed = Optional[int] = Field(
        default=-1,
        description="Seed for random number generator. Use -1 for random seed.",
    )
    watermark: Optional[bool] = Field(
        default=False,
        description="Whether to add a watermark to the generated image.",
    )


BytePlusImageGenerationRequest = Union[Seeddream_3_Params]


class BytePlusImageGenerationResponse(BaseModel):
    image_url: Optional[str] = Field(
        default=None,
        description="URL of the generated image.",
    )
    error: Optional[Union[str, dict]] = Field(
        default=None,
        description="Error message if the image generation failed.",
    )
    is_nsfw_detected: bool = Field(
        default=False,
        description="Indicates if NSFW content was detected in the prompt.",
    )
    model_response: Optional[dict] = Field(
        default=None,
        description="Raw response from the BytePlus API.",
    )
