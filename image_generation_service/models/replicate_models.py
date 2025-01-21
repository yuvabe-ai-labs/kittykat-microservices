from pydantic import BaseModel


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
