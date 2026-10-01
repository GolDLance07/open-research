from typing import Optional
from pydantic import BaseModel, Field


class DebugLLMRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    thinking: bool = Field(default=False)


class DebugLLMResponse(BaseModel):
    provider: str
    model: str
    response: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
