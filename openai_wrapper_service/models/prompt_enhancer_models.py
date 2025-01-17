from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str


class EnhancedPromptResponse(BaseModel):
    enhanced_prompt: str
