from pydantic import BaseModel
from typing import Optional, List


class UserAccountResponse(BaseModel):
    """
    Schema for the user account response.
    """
    account_type: str
    id: str
    profile_image: Optional[str]
    website_url: Optional[str]
    username: str
    about: Optional[str]
    business_name: Optional[str]
    board_count: int
    pin_count: int
    follower_count: int
    following_count: int
    monthly_views: Optional[int]

    class Config:
        json_schema_extra = {
            "example": {
                "account_type": "PINNER",
                "id": "2783136121146311751",
                "profile_image": "https://example.com/profile.jpg",
                "website_url": "https://example.com",
                "username": "exampleuser",
                "about": "This is an example user account.",
                "business_name": "Example Business",
                "board_count": 14,
                "pin_count": 339,
                "follower_count": 10,
                "following_count": 347,
                "monthly_views": 163
            }
        }


#-------------------------------

