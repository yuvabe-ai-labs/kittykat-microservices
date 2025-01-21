from enum import Enum
from pydantic import BaseModel


class CategoryEnum(str, Enum):
    tops = "tops"
    bottoms = "bottoms"
    one_pieces = "one-pieces"


class GarmentPhotoTypeEnum(str, Enum):
    auto = "auto"
    model = "model"
    flat_lay = "flat-lay"


class TryOnInput(BaseModel):
    model_image: str
    garment_image: str
    category: CategoryEnum
    garment_photo_type: GarmentPhotoTypeEnum = GarmentPhotoTypeEnum.auto
    nsfw_filter: bool = True
    guidance_scale: float = 2
    timesteps: int = 50
    seed: int = 42
    num_samples: int = 1

    class Config:
        json_schema_extra = {
            "example": {
                "model_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTpl8bIURcUZOC81KSxpAKkHZuN0NCoh-Rlxw&s",
                "garment_image": "https://merchshop.in/wp-content/uploads/2019/10/React-JS-Pocket-logo-t-shirt-black-1.jpg",
                "category": "tops",
                "garment_photo_type": "flat-lay",
                "nsfw_filter": True,
                "guidance_scale": 2.0,
                "timesteps": 50,
                "seed": 42,
                "num_samples": 1,
            }
        }
