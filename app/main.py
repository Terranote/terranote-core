from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes import metrics as metrics_router
from app.config import settings
from app.container import notification_service, osm_client


async def shutdown_event() -> None:
    await osm_client.close()
    await notification_service.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Terranote Core",
        version=settings.api_version,
        description="Central orchestrator for Terranote note creation workflows.",
    )
    app.include_router(api_router, prefix="/api")
    app.include_router(metrics_router.router)
    app.add_event_handler("shutdown", shutdown_event)
    return app


app = create_app()
