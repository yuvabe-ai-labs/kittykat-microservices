from typing import Optional
from pydantic import BaseModel


class ImageToDescriptionRequest(BaseModel):
    image_url: str
    user_prompt: Optional[str] = "Describe this image"


class ImageToDescriptionResponse(BaseModel):
    description: str
