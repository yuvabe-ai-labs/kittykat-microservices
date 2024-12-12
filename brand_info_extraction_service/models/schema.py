from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class BrandUrlRequest(BaseModel):
    url: str = Field(..., description="The URL to analyze the brand.")
    request_id: Optional[str] = Field(
        None, description="An optional identifier for tracking the request."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.example.com/",
                "request_id": "12345",
            }
        }


class BrandAnalysisResponse(BaseModel):
    brand_name: str = Field(..., description="The name of the brand.")
    brand_category: List[str] = Field(..., description="The categories the brand belongs to.")
    brand_description: str = Field(..., description="A description of the brand.")
    brand_colors: List[str] = Field(..., description="The color codes associated with the brand.")
    brand_fonts: List[str] = Field(..., description="The font names used by the brand.")
    brand_logo: List[str] = Field(..., description="Array of logo URLs for the brand.")

    class Config:
        json_schema_extra = {
            "example": {
                "brand_name": "Example Brand",
                "brand_category": ["Technology", "Software"],
                "brand_description": "A leading provider of tech solutions.",
                "brand_colors": ["#FFFFFF", "#000000"],
                "brand_fonts": ["Roboto", "Arial"],
                "brand_logo": [
                    "https://www.example.com/logo1.png",
                    "https://www.example.com/logo2.png"
                ]
            }
        }


class UrlValidator(BaseModel):
    url: HttpUrl

    class Config:
        json_schema_extra = {
            "example": {"url": "https://www.instagram.com/p/CZf1jOlBfCy/media/?size=l"}
        }
