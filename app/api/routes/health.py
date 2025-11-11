from fastapi import APIRouter

from app.schemas.health import HealthStatus

router = APIRouter()


@router.get("/status", response_model=HealthStatus, summary="Estado general del sistema")
async def read_status() -> HealthStatus:
    return HealthStatus(status="ok")


