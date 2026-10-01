from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.config import Settings, get_settings
from app.llm.base import LLMMessage, LLMProvider
from app.llm.factory import get_llm_provider
from app.schemas.debug import DebugLLMRequest, DebugLLMResponse

router = APIRouter()


class SampleStructuredOutput(BaseModel):
    summary: str
    key_points: list[str]


@router.post("/debug/llm", response_model=DebugLLMResponse)
async def debug_llm_chat(
    request: DebugLLMRequest,
    settings: Settings = Depends(get_settings),
    llm: LLMProvider = Depends(get_llm_provider),
) -> DebugLLMResponse:
    if settings.APP_ENV != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug endpoint is only available in development mode",
        )

    messages = [
        LLMMessage(role="system", content="You are a helpful research assistant."),
        LLMMessage(role="user", content=request.prompt),
    ]

    result = await llm.chat(
        messages,
        temperature=request.temperature,
        thinking=request.thinking,
    )

    return DebugLLMResponse(
        provider=llm.name,
        model=llm.model,
        response=result.text,
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
        latency_ms=result.latency_ms,
    )


@router.post("/debug/llm-structured", response_model=SampleStructuredOutput)
async def debug_llm_structured(
    request: DebugLLMRequest,
    settings: Settings = Depends(get_settings),
    llm: LLMProvider = Depends(get_llm_provider),
) -> SampleStructuredOutput:
    if settings.APP_ENV != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug endpoint is only available in development mode",
        )

    messages = [
        LLMMessage(
            role="system",
            content="Extract summary and key points from the following text.",
        ),
        LLMMessage(role="user", content=request.prompt),
    ]

    return await llm.structured(messages, SampleStructuredOutput)
