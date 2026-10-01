from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: bool
    llm_provider: str
    llm_model: str
    llm_healthy: bool
