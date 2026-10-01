from typing import AsyncGenerator, Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import Settings, get_settings
from app.db.models.user import User
from app.db.seed import DEFAULT_LOCAL_USER_ID, seed_default_user
from app.db.session import get_db
from app.llm.base import LLMProvider
from app.llm.factory import get_llm_provider


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Optional[User]:
    if settings.AUTH_MODE == "none":
        user = await seed_default_user(db)
        return user
    return None
