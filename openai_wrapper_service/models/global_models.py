from typing import Any
from pydantic import BaseModel


class GeneralResponse(BaseModel):
    status_code: int
    data: Any
    message: str
