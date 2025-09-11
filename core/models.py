from typing import Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field


TUsage = TypeVar("TUsage")


class ImageResponse(BaseModel, Generic[TUsage]):
    asset_urls: Optional[List[str]] = Field(
        default=None,
        description="Temporary URLs of the generated/edited image.",
    )
    asset_base64s: Optional[List[str]] = Field(
        default=None,
        description="Base64 encoded strings of the generated/edited image.",
    )
    webhook_url: Optional[str] = Field(
        default=None,
        description="If webhook is enabled, this field contains the callback URL where results will be posted.",
    )
    error: Optional[Union[str, dict]] = Field(
        default=None,
        description="Error message if the image generation/edit failed.",
    )
    is_nsfw_detected: bool = Field(
        default=False,
        description="Indicates if NSFW content was detected in the prompt or image generated.",
    )
    model_response: Optional[dict] = Field(
        default=None,
        description="Raw response from the Model API.",
    )
    model_usage: Optional[TUsage] = Field(
        default=None,
        description="Usage details from the Model API, if webhook is available it is null.",
    )
