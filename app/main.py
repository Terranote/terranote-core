from fastapi import FastAPI

from app.api.router import api_router
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Terranote Core",
        version=settings.api_version,
        description="Central orchestrator for Terranote note creation workflows.",
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()


