from pydantic import BaseModel
from typing import Optional, List



class MediaQueryParams(BaseModel):
    bookmark: Optional[str] = None
    page_size: Optional[int] = 25  # Default to 25, max is 250

    class Config:
        json_schema_extra = {
            "example": {
                "bookmark": "next_page_cursor",
                "page_size": 50
            }
        }


class MediaItem(BaseModel):
    media_id: str
    media_type: str
    status: str


class MediaResponse(BaseModel):
    items: List[MediaItem]
    bookmark: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "media_id": "12345",
                        "media_type": "video",
                        "status": "succeeded"
                    }
                ],
                "bookmark": "next_page_cursor"
            }
        }

#-----------------------------------

class MediaUploadRequest(BaseModel):
    """
    Schema for media upload request.
    """
    media_type: str  # The type of media to upload, e.g., "video"

    class Config:
        json_schema_extra = {
            "example": {
                "media_type": "video"
            }
        }


class MediaUploadResponse(BaseModel):
    """
    Schema for media upload response.
    """
    media_id: str
    media_type: str
    upload_url: str
    upload_parameters: dict

    class Config:
        json_schema_extra = {
            "example": {
                "media_id": "12345",
                "media_type": "video",
                "upload_url": "https://pinterest-media-upload.s3-accelerate.amazonaws.com/",
                "upload_parameters": {
                    "x-amz-data": "20220127T185143Z",
                    "x-amz-signature": "fcd6309a6aaee213348666a72abed8b44552a43acb6b340e8e1b288d21a5fe92",
                    "key": "uploads/11/aa/22/3:video:203014033110991560:5212123920968240771",
                    "policy": "eyJleHBpcmF0aW9uIjoiMj..==",
                    "x-amz-credential": "ASIA6QZJ64OPIKV7FRVX/20220127/us-east-1/s3/aws4_request",
                    "x-amz-security-token": "IQoJb3JpZ2luX2VjEJr...==",
                    "x-amz-algorithm": "AWS4-HMAC-SHA256",
                    "Content-Type": "multipart/form-data"
                }
            }
        }

#---------------------------

class MediaDetailsResponse(BaseModel):
    """
    Schema for media upload details response.
    """
    media_id: str
    media_type: str
    status: str  # Status of the media upload (e.g., "succeeded", "in_progress", etc.)

    class Config:
        json_schema_extra = {
            "example": {
                "media_id": "12345",
                "media_type": "video",
                "status": "succeeded"
            }
        }

