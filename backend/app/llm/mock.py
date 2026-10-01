import time
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel
from app.llm.base import LLMMessage, LLMOutputError, LLMProvider, LLMResult

T = TypeVar("T", bound=BaseModel)


class MockProvider(LLMProvider):
    name: str = "mock"
    model: str = "qwen3:8b-mock"

    def __init__(self, canned_responses: Optional[Dict[str, Any]] = None):
        self.canned_responses = canned_responses or {}

    async def chat(
        self,
        messages: List[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        thinking: bool = False,
        timeout_s: float = 120.0,
    ) -> LLMResult:
        start_time = time.perf_counter()
        user_prompt = messages[-1].content if messages else ""

        # Deterministic mock response
        response_text = f"[Mock Qwen3-8B Response] Received {len(messages)} messages. Last prompt: {user_prompt[:80]}"
        latency_ms = (time.perf_counter() - start_time) * 1000

        return LLMResult(
            text=response_text,
            prompt_tokens=len(user_prompt.split()),
            completion_tokens=len(response_text.split()),
            latency_ms=round(latency_ms, 2),
        )

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
        schema_name = schema.__name__
        if schema_name in self.canned_responses:
            data = self.canned_responses[schema_name]
            return schema.model_validate(data)

        # Generate a minimal valid dummy instance for any Pydantic schema
        dummy_data: Dict[str, Any] = {}
        for field_name, field_info in schema.model_fields.items():
            annotation = field_info.annotation
            origin = getattr(annotation, "__origin__", None)

            if origin in (list, List):
                dummy_data[field_name] = []
            elif origin in (dict, Dict):
                dummy_data[field_name] = {}
            elif annotation in (int, float):
                dummy_data[field_name] = 0
            elif annotation is bool:
                dummy_data[field_name] = True
            elif annotation is str:
                dummy_data[field_name] = f"Mock {field_name}"
            elif hasattr(annotation, "model_fields"):
                dummy_data[field_name] = {}
            else:
                dummy_data[field_name] = None

        try:
            return schema.model_validate(dummy_data)
        except Exception as e:
            raise LLMOutputError(
                f"Failed to generate mock structured output for {schema_name}: {e}",
                raw_output=str(dummy_data),
            )

    async def health(self) -> bool:
        return True
