from pydantic import BaseModel


class TextSearchRequest(BaseModel):
    text: str


class TextEmbedResponse(BaseModel):
    embedding: str
