from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class GeneralResponse(BaseModel):
    status_code: int
    data: Any
    message: str


class BaseApiResponse(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: Optional[T] = None
