from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.deps import get_llm_provider
from app.api.v1.endpoints.health import check_health
from app.api.v1.router import api_router
from app.config import get_settings
from app.core.errors import setup_exception_handlers
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.seed import seed_default_user
from app.db.session import async_session_factory, engine

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting OpenResearch backend (%s mode)...", settings.APP_ENV)

    # Initialize tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default user if auth is disabled
    if settings.AUTH_MODE == "none":
        async with async_session_factory() as session:
            await seed_default_user(session)

    # Check LLM provider
    llm = get_llm_provider()
    logger.info("Configured LLM provider: %s (model: %s)", llm.name, llm.model)

    yield

    logger.info("Shutting down OpenResearch backend...")
    await engine.dispose()


app = FastAPI(
    title="OpenResearch API",
    description="Evidence-backed AI research-to-build workspace API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup RFC 7807 exception handlers
setup_exception_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root-level health endpoint matching TRD §9.1
app.add_api_route("/health", check_health, methods=["GET"], tags=["health"])

# API v1 routes
app.include_router(api_router, prefix="/api/v1")
