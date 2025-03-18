from enum import Enum
from typing import Optional, List, Any, Dict, Union
from pydantic import BaseModel, HttpUrl


class WebhookEventFilter(str, Enum):
    START = "start"
    OUTPUT = "output"
    LOGS = "logs"
    COMPLETED = "completed"


class PredictionStatus(str, Enum):
    STARTING = "starting"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class CreatePredictionRequest(BaseModel):
    version: str
    input: Dict[str, Any]
    stream: Optional[bool] = None
    webhook: Optional[str] = None
    webhook_events_filter: Optional[List[WebhookEventFilter]] = None


class CreateModelPredictionRequest(BaseModel):
    input: Dict[str, Any]
    stream: Optional[bool] = None
    webhook: Optional[str] = None
    webhook_events_filter: Optional[List[WebhookEventFilter]] = None


class PredictionUrls(BaseModel):
    get: HttpUrl
    cancel: Optional[HttpUrl] = None
    stream: Optional[HttpUrl] = None


class PredictionMetrics(BaseModel):
    predict_time: float


class PredictionResponse(BaseModel):
    id: str
    model: str
    version: str
    input: Dict[str, Any]
    logs: Optional[str] = None
    output: Optional[Union[str, Dict[str, Any], List[Any]]] = None
    error: Optional[str] = None
    status: PredictionStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    data_removed: bool = False
    metrics: Optional[PredictionMetrics] = None
    urls: PredictionUrls
    source: Optional[str] = None


class PaginatedPredictionsResponse(BaseModel):
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[PredictionResponse]
