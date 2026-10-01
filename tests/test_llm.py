import json
import pytest
import httpx
from pydantic import BaseModel, Field
from app.llm.base import LLMMessage, LLMOutputError, strip_thinking_tags
from app.llm.mock import MockProvider
from app.llm.ollama import OllamaProvider


class ResearchHypothesis(BaseModel):
    title: str = Field(..., min_length=3)
    confidence: float = Field(..., ge=0.0, le=1.0)
    key_findings: list[str]


@pytest.mark.asyncio
async def test_mock_provider_chat():
    provider = MockProvider()
    messages = [
        LLMMessage(role="system", content="You are a research agent."),
        LLMMessage(role="user", content="Analyze the problem of low-resource crop disease detection."),
    ]
    result = await provider.chat(messages)
    assert "[Mock Qwen3-8B Response]" in result.text
    assert result.prompt_tokens > 0
    assert result.completion_tokens > 0
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_mock_provider_structured():
    provider = MockProvider()
    messages = [
        LLMMessage(role="user", content="Extract structured research hypothesis."),
    ]
    hypothesis = await provider.structured(messages, ResearchHypothesis)
    assert isinstance(hypothesis, ResearchHypothesis)
    assert hypothesis.title.startswith("Mock")
    assert isinstance(hypothesis.confidence, float)
    assert isinstance(hypothesis.key_findings, list)


def test_strip_thinking_tags():
    raw = "<think>Let me reason about this problem carefully...</think>Here is the final recommendation."
    cleaned = strip_thinking_tags(raw)
    assert cleaned == "Here is the final recommendation."

    nested_or_multiline = """<think>
    Step 1: Check sources
    Step 2: Compare models
    </think>Final output."""
    assert strip_thinking_tags(nested_or_multiline) == "Final output."


@pytest.mark.asyncio
async def test_ollama_structured_repair_flow(monkeypatch):
    """Test that if the model returns invalid JSON on first attempt, repair attempt succeeds."""
    call_count = 0

    async def mock_post(client, url, json=None, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First attempt returns invalid json
            content = "Invalid non-json response <think>oops</think>"
        else:
            # Second (repair) attempt returns valid json matching ResearchHypothesis
            content = json_lib.dumps({
                "title": "Edge Vision Transformer",
                "confidence": 0.85,
                "key_findings": ["Fast inference", "Low compute footprint"]
            })
        
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            json={"message": {"content": content}, "prompt_eval_count": 10, "eval_count": 20},
            request=request,
        )

    import json as json_lib
    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    provider = OllamaProvider()
    messages = [LLMMessage(role="user", content="Generate research hypothesis.")]
    result = await provider.structured(messages, ResearchHypothesis, repair_attempts=1)
    
    assert call_count == 2
    assert result.title == "Edge Vision Transformer"
    assert result.confidence == 0.85
    assert len(result.key_findings) == 2
