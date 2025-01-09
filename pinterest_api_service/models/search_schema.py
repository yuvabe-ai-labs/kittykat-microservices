from pydantic import BaseModel
from typing import Dict, List, Optional

class Media(BaseModel):
    image_cover_url: str
    pin_thumbnail_urls: List[str]

class Owner(BaseModel):
    username: str

class Board(BaseModel):
    id: str
    created_at: str
    board_pins_modified_at: str
    name: str
    description: str
    collaborator_count: int
    pin_count: int
    follower_count: int
    media: Media
    owner: Owner
    privacy: str

class SearchBoardsResponse(BaseModel):
    items: List[Board]
    bookmark: Optional[str]

class PinMedia(BaseModel):
    media_type: str
    images: Dict[str, Dict[str, str]]  # Ensure 'url' is correctly typed as 'str'

class PinBoardOwner(BaseModel):
    username: str

class PinMetrics(BaseModel):
    pin_click: int
    impression: int
    clickthrough: int

class PinLifetimeMetrics(BaseModel):
    pin_click: int
    impression: int
    clickthrough: int
    reaction: int
    comment: int

class Pin(BaseModel):
    id: str
    created_at: str
    link: str
    title: str
    description: str
    dominant_color: Optional[str] = None
    alt_text: Optional[str] = None
    creative_type: str
    board_id: str
    board_section_id: Optional[str] = None  # Allow None
    board_owner: PinBoardOwner
    is_owner: bool
    media: PinMedia
    parent_pin_id: Optional[str] = None
    is_standard: bool
    has_been_promoted: bool
    note: Optional[str] = None
    pin_metrics: Optional[PinMetrics] = None  # Make optional
    lifetime_metrics: Optional[PinLifetimeMetrics] = None  # Make optional

class SearchPinsResponse(BaseModel):
    items: List[Pin]
    bookmark: Optional[str]

