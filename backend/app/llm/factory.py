from functools import lru_cache
from app.config import get_settings
from app.llm.base import LLMProvider
from app.llm.mock import MockProvider
from app.llm.ollama import OllamaProvider
from app.llm.vllm import VLLMProvider


@lru_cache()
def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    provider_name = settings.LLM_PROVIDER.lower().strip()

    if provider_name == "ollama":
        return OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.MODEL_NAME,
            num_ctx=settings.LLM_NUM_CTX,
        )
    elif provider_name == "vllm":
        return VLLMProvider(
            base_url=settings.VLLM_BASE_URL,
            model=settings.MODEL_NAME,
        )
    else:
        return MockProvider()
