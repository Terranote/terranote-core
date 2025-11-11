from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes import metrics
from app.container import osm_client
from app.config import settings


async def shutdown_event() -> None:
    await osm_client.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Terranote Core",
        version=settings.api_version,
        description="Central orchestrator for Terranote note creation workflows.",
    )
    app.include_router(api_router, prefix="/api")
    app.include_router(metrics.router)
    app.add_event_handler("shutdown", shutdown_event)
    return app


app = create_app()


