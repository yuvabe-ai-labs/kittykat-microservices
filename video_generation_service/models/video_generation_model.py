from pydantic import BaseModel, HttpUrl, field_validator
from typing import List, Optional, Union

class RunPredictionRequest(BaseModel):
    prompt: str
    start_image: Optional[str] = None
    duration: Optional[int] = 5
    aspect_ratio: Optional[str] = "16:9"
    cfg_scale: Optional[float] = 0.5
    negative_prompt: Optional[str] = ""
    end_image: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "A futuristic city with flying cars and neon lights",
                "start_image": "https://replicate.delivery/mgxm/5de85319-a354-4178-a2b0-aab4a65fa480/start.png",
                "end_image": "https://replicate.delivery/mgxm/aebabf54-c730-4efe-857d-1182960918d4/end.png",
                "duration": 5,
                "aspect_ratio": "16:9",
                "cfg_scale": 0.5,
                "negative_prompt": "blurry, low-resolution"
            }
        }

class RunPredictionResponse(BaseModel):
    id: str

class PredictionStatus(BaseModel):
    id: str
    status: str
    logs: str
    output: Optional[Union[HttpUrl, List[HttpUrl]]] = None

    @field_validator("output", mode="before")
    def convert_to_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v
