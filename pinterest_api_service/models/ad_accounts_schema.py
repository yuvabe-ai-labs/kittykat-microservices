from pydantic import BaseModel,Field,constr
from typing import Optional,List



# Define the Pydantic model for the request body
class AdAccountCreateRequest(BaseModel):
    country: str  # Country ID from ISO 3166-1 alpha-2
    currency: str  # Currency Code from ISO 4217
    name: str  # Ad Account name (<= 256 characters)
    owner_user_id: str  # Owner User ID (must be a number)


    class Config:
        json_schema_extra = {
            "example": {
                "country": "US",
                "currency": "USD",
                "owner_user_id": "383791336903426391",
                "name": "ACME Tools"}
        }
 
                