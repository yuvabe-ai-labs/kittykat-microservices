import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging


class Config(BaseSettings):
    REPLICATE_API_KEY: str = Field(..., env="REPLICATE_API_KEY")
    FALAI_API_KEY: str = Field(..., env="FALAI_API_KEY")
    FASHN_API_KEY: str = Field(..., env="FASHN_API_KEY")
    STAGE_TYPE: str = Field("dev", env="STAGE_TYPE")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    BYTEPLUS_API_KEY: str = Field(..., env="BYTEPLUS_API_KEY")
    FREEPIK_API_KEY: str = Field(..., env="FREEPIK_API_KEY")
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    BUCKET_SA_KEY: str = Field(..., env="BUCKET_SA_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


config = Config()

logging.info(
    f"Loaded image generation microservice configuration for stage: {config.STAGE_TYPE}")
