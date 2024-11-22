from pydantic import BaseModel
from typing import List


class UrlRequest(BaseModel):
    url: str


class ImageEmbedResponse(BaseModel):
    ImageEmbeddings: List[float]
