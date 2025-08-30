
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging


class BaseConfig(BaseSettings):
    STAGE_TYPE: str = Field(..., pattern="^(dev|stg|prod|beta)$")
    REPLICATE_API_KEY: str = Field(..., min_length=1)
    BYTEPLUS_API_KEY: str = Field(..., min_length=1)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")


config = BaseConfig()
logging.info(f"Loaded configuration for stage: {config.STAGE_TYPE}")
