from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_ENV: str = "development"
    AUTH_MODE: str = "none"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    LOG_LEVEL: str = "INFO"

    # LLM
    LLM_PROVIDER: str = "mock"  # "ollama" | "vllm" | "mock"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    VLLM_BASE_URL: str = "http://localhost:8001/v1"
    MODEL_NAME: str = "qwen3:8b"
    LLM_NUM_CTX: int = 16384
    LLM_TIMEOUT_S: float = 120.0

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./openresearch.db"

    # External APIs
    GITHUB_TOKEN: str = ""
    SEMANTIC_SCHOLAR_API_KEY: str = ""
    SEARCH_PROVIDER: str = "tavily"
    SEARCH_API_KEY: str = ""
    HF_TOKEN: str = ""

    # Research budgets
    MAX_CRITIC_CYCLES: int = 2
    MAX_TOOL_CALLS: int = 60
    MAX_SOURCES: int = 60
    MAX_DEEP_READ_SOURCES: int = 25
    RUN_TIMEOUT_S: int = 900

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
