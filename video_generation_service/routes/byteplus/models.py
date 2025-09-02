from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, field_serializer


class BaseParams(BaseModel):
    webhook_url: HttpUrl

    @field_serializer("webhook_url", when_used="always")
    def serialize_webhook_url(self, v: HttpUrl, _info):
        return str(v)


class Seedance_1_0_Lite_I2V_Params(BaseParams):
    prompt: str = Field(
        description="The text prompt to guide the video generation."
    )
    model: Literal["seedance-1-0-lite-i2v-250428"]
    first_frame: Optional[HttpUrl] = Field(
        default=None,
        description="The URL of the first frame image."
    )
    last_frame: Optional[HttpUrl] = Field(
        default=None,
        description="The URL of the last frame image."
    )
    resolution: Literal["480p", "720p", "1080p"] = Field(
        default="720p",
        description="The resolution of the output video."
    )
    ratio: Literal[
        "16:9",
        "4:3",
        "1:1",
        "3:4",
        "9:16",
        "21:9",
        "adaptive"
    ] = Field(
        default="adaptive",
        description="The aspect ratio of the output video."
    )
    duration: int = Field(
        default=5,
        ge=3,
        le=12,
        description="The duration of the output video"
    )
    framepersecond: Literal[24] = Field(
        default=24,
        description="The frame rate of the output video."
    )
    watermark: bool = Field(
        default=False,
        description="Whether to add a watermark to the output video."
    )
    seed: int = Field(
        default=-1,
        description="Random seed for video generation. If not provided, a random seed will be used."
    )
    camerafixed: bool = Field(
        default=False,
        description="Specifies whether to fix the camera."
    )

    @field_serializer("first_frame", when_used="always")
    def serialize_fisrt_frame(self, v: HttpUrl, _info):
        return str(v)

    @field_serializer("last_frame", when_used="always")
    def serialize_last_frame(self, v: HttpUrl, _info):
        return str(v)


class Seedance_1_0_Pro_Params(BaseParams):
    prompt: str = Field(
        description="The text prompt to guide the video generation."
    )
    model: Literal["seedance-1-0-pro-250528"]
    first_frame: Optional[HttpUrl] = Field(
        default=None,
        description="The URL of the first frame image."
    )
    resolution: Literal["480p", "720p", "1080p"] = Field(
        default="1080p",
        description="The resolution of the output video."
    )
    ratio: Literal[
        "16:9",
        "4:3",
        "1:1",
        "3:4",
        "9:16",
        "21:9",
        "adaptive"
    ] = Field(
        default="adaptive",
        description="The aspect ratio of the output video."
    )
    duration: int = Field(
        default=5,
        ge=3,
        le=12,
        description="The duration of the output video"
    )
    framepersecond: Literal[24] = Field(
        default=24,
        description="The frame rate of the output video."
    )
    watermark: bool = Field(
        default=False,
        description="Whether to add a watermark to the output video."
    )
    seed: int = Field(
        default=-1,
        description="Random seed for video generation. If not provided, a random seed will be used."
    )
    camerafixed: bool = Field(
        default=False,
        description="Specifies whether to fix the camera."
    )

    @field_serializer("first_frame", when_used="always")
    def serialize_fisrt_frame(self, v: HttpUrl, _info):
        return str(v)


BytePlusVideoGenerationRequest = Annotated[
    Union[
        Seedance_1_0_Pro_Params,
        Seedance_1_0_Lite_I2V_Params
    ],
    Field(discriminator="model")
]
