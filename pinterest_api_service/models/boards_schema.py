from pydantic import BaseModel,Field,constr
from typing import Optional,List



class CreateBoardPayload(BaseModel):
    """
    Pydantic model for the Create Board request payload.
    """
    name: str = Field(None,strip_whitespace=True, min_length=1, max_length=255, description="The name of the board.")
    description: str = Field(
        None, description="Optional description of the board."
    )
    privacy: str = Field(
        "PUBLIC",
        description='Privacy setting for the board. Options: "PUBLIC", "PROTECTED", "SECRET". Default is "PUBLIC".',
        pattern="^(PUBLIC|PROTECTED|SECRET)$",
    )


    class Config:
        json_schema_extra = {
            "example": {
                "name": "Board_Name",  # Example name following the numeric pattern
                "description": "This is a description of the board.",
                "privacy": "PUBLIC"  # Example privacy setting
            }
        }


class UpdateBoardPayload(BaseModel):
    name: Optional[str] = Field(None, example="New Summer Recipes")
    description: Optional[str] = Field(None, example="Updated summer recipes!")
    privacy: Optional[str] = Field("PUBLIC", example="SECRET")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "New Summer Recipes",
                "description": "Updated summer recipes!",
                "privacy": "PUBLIC"
            }
        }


