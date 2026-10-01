import json
import logging
import time
from typing import Any, Dict, List, Type, TypeVar
import httpx
from pydantic import BaseModel, ValidationError
from app.llm.base import (
    LLMMessage,
    LLMOutputError,
    LLMProvider,
    LLMResult,
    strip_thinking_tags,
)

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3:8b",
        num_ctx: int = 16384,
    ):
        self.name = "ollama"
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.num_ctx = num_ctx

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
        payload = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": self.num_ctx,
            },
        }

        async with httpx.AsyncClient(timeout=timeout_s) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

        raw_content = data.get("message", {}).get("content", "")
        cleaned_content = strip_thinking_tags(raw_content)
        latency_ms = (time.perf_counter() - start_time) * 1000

        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        return LLMResult(
            text=cleaned_content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
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
        schema_json = schema.model_json_schema()
        payload = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "format": schema_json,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": self.num_ctx,
            },
        }

        raw_text = ""
        current_messages = list(messages)

        for attempt in range(repair_attempts + 1):
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()

            raw_text = data.get("message", {}).get("content", "")
            cleaned = strip_thinking_tags(raw_text)

            try:
                parsed_json = json.loads(cleaned)
                return schema.model_validate(parsed_json)
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(
                    "Schema validation attempt %d failed for %s: %s",
                    attempt + 1,
                    schema.__name__,
                    e,
                )
                if attempt < repair_attempts:
                    # Provide feedback for repair
                    repair_msg = (
                        f"Your previous JSON output was invalid for schema {schema.__name__}.\n"
                        f"Error: {str(e)}\n"
                        f"Please output ONLY a valid JSON object matching the requested schema."
                    )
                    current_messages.append(LLMMessage(role="assistant", content=cleaned))
                    current_messages.append(LLMMessage(role="user", content=repair_msg))
                    payload["messages"] = [m.model_dump() for m in current_messages]
                else:
                    raise LLMOutputError(
                        f"Failed to produce valid structured output for {schema.__name__} after {repair_attempts + 1} attempts",
                        raw_output=raw_text,
                        details=[str(e)],
                    )

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
