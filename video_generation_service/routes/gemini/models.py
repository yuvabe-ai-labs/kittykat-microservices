from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, field_serializer, model_validator


class BaseParams(BaseModel):
    webhook_url: Optional[HttpUrl] = Field(
        default=None,
        description="The URL to which the video generation results will be sent upon completion.",
    )

    @field_serializer("webhook_url", when_used="always")
    def serialize_webhook_url(self, v: HttpUrl, _info):
        return str(v)


class Veo3Params(BaseParams):
    model: Literal["veo-3.0-generate-001"]
    prompt: str = Field(
        description="The text prompt to guide the video generation."
    )
    duration: int = Field(
        default=8,
        ge=8,
        le=8,
        description="The duration of the output video in seconds."
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        description="The negative text prompt to guide the video generation."
    )
    image: Optional[HttpUrl] = Field(
        default=None,
        description="The URL of the reference image."
    )
    resolution: Literal["720p", "1080p"] = Field(
        default="720p",
        description="The resolution of the output video."
    )
    aspect_ratio: Literal[
        "16:9",
        "9:16",
    ] = Field(
        default="16:9",
        description="The aspect ratio of the output video."
    )

    @field_serializer("image", when_used="always")
    def serialize_image(self, v: HttpUrl, _info):
        return str(v)

    @model_validator(mode="after")
    def check_resolution_aspect_ratio(self):
        if self.resolution == "1080p" and self.aspect_ratio != "16:9":
            raise ValueError(
                "1080p resolution only supports 16:9 aspect ratio.")
        return self


class Veo2Params(BaseParams):
    model: Literal["veo-2.0-generate-001"]
    prompt: str = Field(
        description="The text prompt to guide the video generation."
    )
    duration: int = Field(
        default=5,
        ge=8,
        le=5,
        description="The duration of the output video in seconds."
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        description="The negative text prompt to guide the video generation."
    )
    image: Optional[HttpUrl] = Field(
        default=None,
        description="The URL of the reference image."
    )
    aspect_ratio: Literal[
        "16:9",
        "9:16",
    ] = Field(
        default="16:9",
        description="The aspect ratio of the output video."
    )

    @field_serializer("image", when_used="always")
    def serialize_image(self, v: HttpUrl, _info):
        return str(v)


GeminiVideoGenerationRequest = Annotated[
    Union[
        Veo3Params,
        Veo2Params
    ],
    Field(discriminator="model")
]
