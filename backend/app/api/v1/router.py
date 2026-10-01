from fastapi import APIRouter
from app.api.v1.endpoints import debug, health, projects

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(debug.router, tags=["debug"])
api_router.include_router(projects.router, tags=["projects"])
