from typing import Dict, List, Optional, Any
import uuid
from pydantic import BaseModel, Field, HttpUrl, root_validator, validator, SecretStr
from enum import Enum
from datetime import datetime


class ImageRequest(BaseModel):
    prompt: str
    model: str = "black-forest-labs/flux-dev"
    enhance_prompt: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Create a futuristic cityscape at sunset.",
                "model": "black-forest-labs/flux-dev",
                "enhance_prompt": True,
            }
        }


# Models
class TrainingStatus(str, Enum):
    STARTING = "starting"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class WebhookEvent(str, Enum):
    START = "start"
    OUTPUT = "output"
    LOGS = "logs"
    COMPLETED = "completed"


class AutocaptionOptions(BaseModel):
    enabled: bool = Field(False, description="Automatically caption images")
    prefix: Optional[str] = Field(None, description="Text to prepend to captions")
    suffix: Optional[str] = Field(None, description="Text to routerend to captions")


class WandbConfig(BaseModel):
    api_key: SecretStr = Field(..., description="Weights & Biases API key")
    project: str = Field("flux_train_replicate", description="W&B project name")
    entity: Optional[str] = Field(None, description="W&B entity name")
    run: Optional[str] = Field(None, description="W&B run name")
    sample_prompts: Optional[str] = Field(
        None, description="Newline-separated prompts for W&B samples"
    )
    sample_interval: int = Field(
        100, description="Step interval for sampling output images"
    )
    save_interval: int = Field(
        100, description="Step interval for saving intermediate weights"
    )


class TrainingInput(BaseModel):
    destination: str = Field(
        ...,
        description="Model destination in format owner/name",
        pattern=r"^[A-Za-z0-9_\-]+/[A-Za-z0-9_\-]+$",
    )
    model_owner: str = Field(..., description="Owner of the model to train")
    model_name: str = Field(..., description="Name of the model to train")
    version_id: Optional[str] = Field(
        None, description="Version ID of the model to train"
    )  # Optional field with default None

    # Required training parameters
    input_images: HttpUrl = Field(
        ..., description="URL to zip file containing training data"
    )
    # Optional training parameters
    steps: int = Field(1000, ge=3, le=6000, description="Number of training steps")
    lora_rank: int = Field(16, ge=1, le=128, description="LoRA rank value")

    hf_repo_id: Optional[str] = Field(None, description="HuggingFace repository ID")
    hf_token: Optional[SecretStr] = Field(None, description="HuggingFace token")

    # W&B integration
    wandb: Optional[WandbConfig] = Field(
        None, description="Weights & Biases configuration"
    )

    # Autocaption settings
    autocaption: AutocaptionOptions = Field(
        default_factory=AutocaptionOptions, description="Auto-captioning configuration"
    )

    # Advanced training parameters
    learning_rate: float = Field(0.0004, description="Learning rate")
    batch_size: int = Field(1, description="Batch size")
    resolution: str = Field(
        "512,768,1024", description="Image resolutions for training"
    )
    caption_dropout_rate: float = Field(
        0.05, ge=0, le=1, description="Caption dropout rate"
    )
    optimizer: str = Field("adamw8bit", description="Optimizer to use")
    cache_latents_to_disk: bool = Field(False, description="Cache latents to disk")
    layers_to_optimize_regex: Optional[str] = Field(
        None, description="Regex for layers to optimize"
    )
    gradient_checkpointing: bool = Field(
        False, description="Enable gradient checkpointing"
    )

    # Skip training option
    skip_training_and_use_pretrained_hf_lora_url: Optional[HttpUrl] = Field(
        None, description="URL to pretrained HF LoRA to use instead of training"
    )

    # Webhook configuration
    webhook: Optional[HttpUrl] = Field(
        None, description="Webhook URL for notifications"
    )
    webhook_events_filter: Optional[List[WebhookEvent]] = Field(
        None, description="Events that trigger webhooks"
    )

    def to_replicate_payload(self) -> Dict[str, Any]:
        """Convert to Replicate API payload format"""
        # Build inputs dictionary with all the training parameters
        input_dict = {
            "input_images": str(self.input_images),
            "steps": self.steps,
            "lora_rank": self.lora_rank,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "resolution": self.resolution,
            "caption_dropout_rate": self.caption_dropout_rate,
            "optimizer": self.optimizer,
            "cache_latents_to_disk": self.cache_latents_to_disk,
            "gradient_checkpointing": self.gradient_checkpointing,
            "autocaption": self.autocaption.enabled,
        }

        # Add optional parameters if they exist
        if self.autocaption.prefix:
            input_dict["autocaption_prefix"] = self.autocaption.prefix
        if self.autocaption.suffix:
            input_dict["autocaption_suffix"] = self.autocaption.suffix
        if self.layers_to_optimize_regex:
            input_dict["layers_to_optimize_regex"] = self.layers_to_optimize_regex
        if self.hf_repo_id:
            input_dict["hf_repo_id"] = self.hf_repo_id
        if self.hf_token:
            input_dict["hf_token"] = self.hf_token.get_secret_value()
        if self.skip_training_and_use_pretrained_hf_lora_url:
            input_dict["skip_training_and_use_pretrained_hf_lora_url"] = str(
                self.skip_training_and_use_pretrained_hf_lora_url
            )

        # Handle W&B configuration
        if self.wandb:
            input_dict["wandb_api_key"] = self.wandb.api_key.get_secret_value()
            input_dict["wandb_project"] = self.wandb.project
            if self.wandb.entity:
                input_dict["wandb_entity"] = self.wandb.entity
            if self.wandb.run:
                input_dict["wandb_run"] = self.wandb.run
            if self.wandb.sample_prompts:
                input_dict["wandb_sample_prompts"] = self.wandb.sample_prompts
            input_dict["wandb_sample_interval"] = self.wandb.sample_interval
            input_dict["wandb_save_interval"] = self.wandb.save_interval

        # Build the final payload
        payload = {"destination": self.destination, "input": input_dict}

        # Add webhook configuration if present
        if self.webhook:
            payload["webhook"] = str(self.webhook)
            if self.webhook_events_filter:
                payload["webhook_events_filter"] = [
                    event.value for event in self.webhook_events_filter
                ]

        return payload


class TrainingInputExtended(TrainingInput):
    image_urls: Optional[List[HttpUrl]] = Field(
        None, description="List of image URLs to be zipped for training"
    )

    # Override the validator to allow either input_images or image_urls
    @root_validator(pre=True)
    def validate_input_source(cls, values):
        # Check if at least one of input_images or image_urls is provided
        if not values.get("input_images") and not values.get("image_urls"):
            raise ValueError("Either input_images or image_urls must be provided")
        return values


class TrainingResponse(BaseModel):
    id: str
    model: str
    version: str
    input: Dict[str, Any]
    logs: Optional[str] = None
    error: Optional[str] = None
    status: TrainingStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, float]] = None
    urls: Dict[str, str]


class PaginatedTrainings(BaseModel):
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[TrainingResponse]


class HardwareInfo(BaseModel):
    name: str
    sku: str


class ZipRequest(BaseModel):
    folder_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique ID"
    )
    image_urls: List[HttpUrl]
    caption: Optional[str] = "Describe this image"
