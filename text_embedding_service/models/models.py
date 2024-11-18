from pydantic import BaseModel


class TextSearchRequest(BaseModel):
    search_query: str