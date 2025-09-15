from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseApiResponse(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: Optional[T] = None
