from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Union, Literal


class RunPredictionRequest(BaseModel):
    model_image: str
    garment_image: str
    category: Literal["auto", "tops", "bottoms", "one-pieces"] = "auto"
    segmentation_free: bool = True
    moderation_level: Literal["conservative", "permissive", "none"] = "permissive"
    garment_photo_type: Literal["auto", "flat-lay", "model"] = "auto"
    mode: Literal["performance", "balanced", "quality"] = "balanced"
    seed: int = 42
    num_samples: int = Field(default=1, ge=1, le=4)

    class Config:
        json_schema_extra = {
            "example": {
                "model_image": "https://images.unsplash.com/photo-1614495039368-525273956716?q=80&w=2574&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                "garment_image": "https://images.unsplash.com/photo-1633966887768-64f9a867bdba?q=80&w=2603&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                "category": "tops",
                "garment_photo_type": "flat-lay",
                "segmentation_free": True,
                "moderation_level": "permissive",
                "mode": "balanced",
                "seed": 42,
                "num_samples": 1,
            }
        }


class RunPredictionResponse(BaseModel):
    id: str
    error: Optional[str] = None


class PredictionStatus(BaseModel):
    id: str
    status: str
    output: Optional[List[str]] = None
    error: Union[str, dict, None] = None
