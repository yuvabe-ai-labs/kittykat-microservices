from enum import Enum
from typing import Optional, List, Any, Dict, Union
from pydantic import BaseModel, HttpUrl


class WebhookEventFilter(str, Enum):
    START = "start"
    OUTPUT = "output"
    LOGS = "logs"
    COMPLETED = "completed"


class CreatePredictionRequest(BaseModel):
    version: str
    input: Dict[str, Any]
    stream: Optional[bool] = None
    webhook: Optional[str] = None
    webhook_events_filter: Optional[List[WebhookEventFilter]] = None
