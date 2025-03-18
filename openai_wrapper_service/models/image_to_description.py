from typing import Optional
from pydantic import BaseModel


class ImageToDescriptionRequest(BaseModel):
    image_url: str
    user_prompt: Optional[str] = "Describe this image"
    focus_entity: Optional[str] = None
    trigger_word: Optional[str] = None
    openai_model: Optional[str] = "gpt-4o-mini"


class ImageToDescriptionResponse(BaseModel):
    description: str
