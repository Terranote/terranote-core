from fastapi import APIRouter

from app.api.routes import health, interactions, notes

api_router = APIRouter()
api_router.include_router(health.router, prefix="/v1", tags=["health"])
api_router.include_router(interactions.router, prefix="/v1", tags=["interactions"])
api_router.include_router(notes.router, prefix="/v1", tags=["notes"])
