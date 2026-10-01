import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.db.models.user import User

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_USER_ID = "00000000-0000-0000-0000-000000000001"
DEFAULT_LOCAL_USER_EMAIL = "local@openresearch.dev"
DEFAULT_LOCAL_USER_NAME = "Local Researcher"


async def seed_default_user(session: AsyncSession) -> User:
    settings = get_settings()
    if settings.AUTH_MODE != "none":
        return None

    stmt = select(User).where(User.id == DEFAULT_LOCAL_USER_ID)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=DEFAULT_LOCAL_USER_ID,
            email=DEFAULT_LOCAL_USER_EMAIL,
            display_name=DEFAULT_LOCAL_USER_NAME,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info("Seeded default local user: %s (%s)", user.display_name, user.id)
    return user
