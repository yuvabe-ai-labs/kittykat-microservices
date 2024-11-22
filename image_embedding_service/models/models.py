from pydantic import BaseModel


class Base64ImageRequest(BaseModel):
    base64_image: str


class ImageEmbedResponse(BaseModel):
    ImageEmbeddings: str
