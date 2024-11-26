from pydantic import BaseModel, Field
from typing import List, Optional


class TextRequest(BaseModel):
    text: str = Field(..., description="The text to be requested.")
    request_id: Optional[str] = Field(
        None, description="An optional identifier for tracking the request."
    )

    class Config:
        json_schema_extra = {
            "example": {"text": "Hello, I am a simple text", "request_id": "12345"}
        }


class TextEmbedResponse(BaseModel):
    text: str = Field(..., description="The requested text for embeddings.")
    request_id: Optional[str] = Field(
        None, description="An optional request identifier for tracking."
    )
    response_id: str = Field(
        ..., description="The unique identifier for this response."
    )
    textEmbedding: List[float] = Field(
        ..., description="A list of float values representing the text embeddings."
    )
    message: str = Field(
        ..., description="The message indicating the status of the request."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, I am the requested text.",
                "request_id": "12345",
                "response_id": "resp-67890",
                "textEmbedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "message": "Success",
            }
        }
