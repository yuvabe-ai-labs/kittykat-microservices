from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class RunPredictionRequest(BaseModel):
    model_image: str
    garment_image: str
    category: str
    nsfw_filter: Optional[bool] = True
    cover_feet: Optional[bool] = False
    adjust_hands: Optional[bool] = False
    restore_background: Optional[bool] = False
    restore_clothes: Optional[bool] = False
    garment_photo_type: Optional[str] = "auto"
    long_top: Optional[bool] = False
    mode: Optional[str] = "balanced"
    seed: Optional[int] = 42
    num_samples: Optional[int] = 1

    class Config:
        json_schema_extra = {
            "example": {
                "model_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTpl8bIURcUZOC81KSxpAKkHZuN0NCoh-Rlxw&s",
                "garment_image": "https://merchshop.in/wp-content/uploads/2019/10/React-JS-Pocket-logo-t-shirt-black-1.jpg",
                "category": "tops",
                "garment_photo_type": "flat-lay",
                "nsfw_filter": True,
                "cover_feet": False,
                "adjust_hands": False,
                "restore_background": False,
                "restore_clothes": False,
                "long_top": False,
                "mode": "balanced",
                "seed": 42,
                "num_samples": 1,
            }
        }


class RunPredictionResponse(BaseModel):
    id: str


class PredictionStatus(BaseModel):
    id: str
    status: str
    output: Optional[List[HttpUrl]] = None
