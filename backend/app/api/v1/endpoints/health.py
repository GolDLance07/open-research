import logging
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.llm.base import LLMProvider
from app.llm.factory import get_llm_provider
from app.schemas.health import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def check_health(
    db: AsyncSession = Depends(get_db),
    llm: LLMProvider = Depends(get_llm_provider),
) -> HealthResponse:
    db_healthy = False
    try:
        result = await db.execute(text("SELECT 1"))
        db_healthy = result.scalar() == 1
    except Exception as e:
        logger.error("Database health check failed: %s", e)

    llm_healthy = False
    try:
        llm_healthy = await llm.health()
    except Exception as e:
        logger.error("LLM health check failed: %s", e)

    overall_status = "healthy" if (db_healthy and llm_healthy) else "degraded"

    return HealthResponse(
        status=overall_status,
        database=db_healthy,
        llm_provider=llm.name,
        llm_model=llm.model,
        llm_healthy=llm_healthy,
    )
