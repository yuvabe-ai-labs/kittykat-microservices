from pydantic import BaseModel


class TextRequest(BaseModel):
    text: str


class TextEmbedResponse(BaseModel):
    embedding: str
