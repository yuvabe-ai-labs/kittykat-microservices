from pydantic import BaseModel, HttpUrl, conlist
from typing import List, Optional


class BrandDataRequest(BaseModel):
    url: HttpUrl


class BrandDataResponse(BaseModel):
    brand_name: Optional[str]
    brand_category: Optional[List[str]]
    brand_description: Optional[str]
    brand_logo: Optional[str]
    brand_colors: Optional[List[str]]
    brand_fonts: Optional[List[str]]
    favicon: Optional[str]
