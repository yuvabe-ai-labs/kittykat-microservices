from pydantic import BaseModel


class TextSearchRequest(BaseModel):
    text: str
