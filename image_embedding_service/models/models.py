from pydantic import BaseModel, HttpUrl,Field
from typing import List,Optional

class UrlRequest(BaseModel):
    url: str = Field(..., description="The URL to be requested.")
    request_id: Optional[str] = Field(None, description="An optional identifier for tracking the request.")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.instagram.com/p/CZf1jOlBfCy/media/?size=l",
                "request_id": "12345"
            }
        }



class ImageEmbedResponse(BaseModel):
    url: str = Field(..., description="The URL of the image.")
    request_id: Optional[str] = Field(None, description="An optional request identifier for tracking.")
    response_id: str = Field(..., description="The unique identifier for this response.")
    ImageEmbeddings: List[float] = Field(..., description="A list of float values representing the image embeddings.")
    Message: str = Field(..., description="The message indicating the status of the request.")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.instagram.com/p/CZf1jOlBfCy/media/?size=l",
                "request_id": "12345",
                "response_id": "resp-67890",
                "ImageEmbeddings": [0.1, 0.2, 0.3, 0.4, 0.5],
                "Message": "Success",
            }
        }


class UrlValidator(BaseModel):
    url: HttpUrl

    class Config:
        json_schema_extra = {
            "example": {"url": "https://www.instagram.com/p/CZf1jOlBfCy/media/?size=l"}
        }
