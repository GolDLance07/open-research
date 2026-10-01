import logging
from typing import List, Type, TypeVar
from pydantic import BaseModel
from app.llm.base import LLMMessage, LLMProvider, LLMResult

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class VLLMProvider(LLMProvider):
    """Stub VLLM provider implementing OpenAI-compatible completions API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8001/v1",
        model: str = "qwen3:8b",
    ):
        self.name = "vllm"
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def chat(
        self,
        messages: List[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        thinking: bool = False,
        timeout_s: float = 120.0,
    ) -> LLMResult:
        raise NotImplementedError("VLLMProvider is a stub in Phase 0. Use OllamaProvider or MockProvider.")

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
        raise NotImplementedError("VLLMProvider is a stub in Phase 0. Use OllamaProvider or MockProvider.")

    async def health(self) -> bool:
        return False
