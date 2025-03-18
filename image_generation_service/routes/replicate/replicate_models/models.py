from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class HardwareOptions(str, Enum):
    CPU = "cpu"
    A100 = "gpu-a100-large"
    L40S = "gpu-l40s"
    T4 = "gpu-t4"


class VisibilityOptions(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


# Cloud options
CLOUD_OPTIONS = ["gcp-us-central1", "aws-us-east-1", "aws-us-west-2"]


class CreateModelRequest(BaseModel):
    name: str
    visibility: VisibilityOptions = VisibilityOptions.PUBLIC
    hardware: HardwareOptions = HardwareOptions.A100
    owner: str = "kittykat-ai"


class ModelVersionRequest(BaseModel):
    model: str
    owner: str = "kittykat-ai"


class DeleteModelVersionRequest(BaseModel):
    model: str
    version_id: str
    owner: str = "kittykat-ai"


class CreateDeploymentRequest(BaseModel):
    name: str
    model: str
    version: str
    hardware: HardwareOptions = HardwareOptions.A100
    min_instances: int = Field(0, ge=0, le=10)
    max_instances: int = Field(1, ge=1, le=10)
    autoscale: bool = False
    cloud: str = "gcp-us-central1"


class UpdateDeploymentRequest(BaseModel):
    name: str
    hardware: Optional[str] = None
    min_instances: Optional[int] = Field(None, ge=1, le=10)
    max_instances: Optional[int] = Field(None, ge=1, le=10)
    autoscale: Optional[bool] = None
    cloud: Optional[str] = None


# Specific response models
class ModelResponse(BaseModel):
    id: str
    owner: str
    name: str
    visibility: str
    hardware: str
    latest_version: Optional[Dict[str, Any]] = None


class VersionsResponse(BaseModel):
    results: List[Dict[str, Any]]


class DeploymentResponse(BaseModel):
    id: str
    name: str
    model: str
    version: str
    status: str
    hardware: str
    min_instances: int
    max_instances: int
    autoscale: bool
    cloud: str


class WebhookEventFilter(str, Enum):
    START = "start"
    OUTPUT = "output"
    LOGS = "logs"
    COMPLETED = "completed"


class CreateModelPredictionRequest(BaseModel):
    input: Dict[str, Any]
    stream: Optional[bool] = None
    webhook: Optional[str] = None
    webhook_events_filter: Optional[List[WebhookEventFilter]] = None


class ModelVersionResponse(BaseModel):
    id: str
    created_at: str
    cog_version: str
    openapi_schema: Dict[str, Any]
