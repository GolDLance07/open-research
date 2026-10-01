from abc import ABC, abstractmethod
import re
from typing import Any, List, Literal, Optional, Type, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMResult(BaseModel):
    text: str
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    latency_ms: float = Field(default=0.0)


class LLMOutputError(Exception):
    def __init__(self, message: str, raw_output: str, details: Optional[List[Any]] = None):
        super().__init__(message)
        self.raw_output = raw_output
        self.details = details or []


def strip_thinking_tags(text: str) -> str:
    """Strip <think>...</think> blocks from output text."""
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text)
    return cleaned.strip()


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        thinking: bool = False,
        timeout_s: float = 120.0,
    ) -> LLMResult:
        """Standard chat completion."""
        pass

    @abstractmethod
    async def structured(
        self,
        messages: List[LLMMessage],
        schema: Type[T],
        *,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        thinking: bool = False,
        repair_attempts: int = 1,
    ) -> T:
        """Structured output parsed and validated into a Pydantic schema."""
        pass

    @abstractmethod
    async def health(self) -> bool:
        """Check if provider is available."""
        pass
