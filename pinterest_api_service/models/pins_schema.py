from pydantic import BaseModel, Field, constr
from typing import Optional, List

#---------------------- Media Item -----------------------
class MediaItem(BaseModel):
    title: str
    description: str
    link: str
    content_type: str
    data: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Image Title",
                "description": "A description of the media item",
                "link": "https://example.com/media-item",
                "content_type": "image/jpeg",
                "data": "base64encodedstring"
            }
        }

#---------------------- Media Source -----------------------
class MediaSource(BaseModel):
    source_type: str
    items: List[MediaItem]
    index: int
    content_type: str
    data: str
    is_standard: bool

    class Config:
        json_schema_extra = {
            "example": {
                "source_type": "image",
                "items": [
                    {
                        "title": "Image Title",
                        "description": "A description of the media item",
                        "link": "https://example.com/media-item",
                        "content_type": "image/jpeg",
                        "data": "base64encodedstring"
                    }
                ],
                "index": 0,
                "content_type": "image/jpeg",
                "data": "base64encodedstring",
                "is_standard": True
            }
        }

#---------------------- Create Pin Request -----------------------
class CreatePinRequest(BaseModel):
    link: Optional[str]
    title: Optional[str]
    description: Optional[str]
    dominant_color: Optional[str]
    alt_text: Optional[str]
    board_id: str
    board_section_id: Optional[str] = None
    media_source: MediaSource
    parent_pin_id: Optional[str] = None
    note: Optional[str] = None
    sponsor_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "link": "https://example.com/pin-link",
                "title": "Pin Title",
                "description": "Pin Description",
                "dominant_color": "#FFFFFF",
                "alt_text": "Alternative text for accessibility",
                "board_id": "boardId123",
                "board_section_id": "sectionId123",
                "media_source": {
                    "source_type": "image",
                    "items": [
                        {
                            "title": "Image Title",
                            "description": "A description of the media item",
                            "link": "https://example.com/media-item",
                            "content_type": "image/jpeg",
                            "data": "base64encodedstring"
                        }
                    ],
                    "index": 0,
                    "content_type": "image/jpeg",
                    "data": "base64encodedstring",
                    "is_standard": True
                },
                "parent_pin_id": "parentPin123",
                "note": "Optional note",
                "sponsor_id": "sponsor123"
            }
        }

#---------------------- Carousel Slot -----------------------
class CarouselSlot(BaseModel):
    title: str
    description: str
    link: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Carousel Slot Title",
                "description": "Carousel Slot Description",
                "link": "https://example.com/carousel-slot-link"
            }
        }

#---------------------- Update Pin Request -----------------------
class UpdatePinRequest(BaseModel):
    alt_text: Optional[str] = None
    board_id: Optional[str] = None
    board_section_id: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None
    title: Optional[str] = None
    carousel_slots: Optional[List[CarouselSlot]] = None
    note: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "alt_text": "Updated alt text",
                "board_id": "updatedBoardId123",
                "board_section_id": "updatedSectionId123",
                "description": "Updated pin description",
                "link": "https://updated-pin-link.com",
                "title": "Updated Pin Title",
                "carousel_slots": [
                    {
                        "title": "Carousel Slot 1",
                        "description": "Description for carousel slot 1",
                        "link": "https://example.com/slot1"
                    },
                    {
                        "title": "Carousel Slot 2",
                        "description": "Description for carousel slot 2",
                        "link": "https://example.com/slot2"
                    }
                ],
                "note": "Updated note"
            }
        }

#---------------------- Pin Analytics Query -----------------------
class PinAnalyticsQuery(BaseModel):
    """
    Pydantic model for Pin analytics query parameters.
    """
    start_date: str = Field(..., description="Metric report start date (UTC). Format: YYYY-MM-DD")
    end_date: str = Field(..., description="Metric report end date (UTC). Format: YYYY-MM-DD")
    metric_types: List[str] = Field(..., description="Pin metric types to get data for (e.g., VIDEO_MRC_VIEW)")
    app_types: Optional[str] = Field("ALL", description='Apps or devices to get data for. Options: "ALL", "MOBILE", "TABLET", "WEB"')
    split_field: Optional[str] = Field("NO_SPLIT", description='How to split the data. Options: "NO_SPLIT", "APP_TYPE"')
    ad_account_id: Optional[str] = Field(None, max_length=18, pattern=r"^\d+$", description="Ad account ID to use if token has business access roles")

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "metric_types": ["VIDEO_MRC_VIEW"],
                "app_types": "ALL",
                "split_field": "NO_SPLIT",
                "ad_account_id": "123456789012345678"
            }
        }
