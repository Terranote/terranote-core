from fastapi import APIRouter

from app.schemas.health import HealthStatus, NoteMetrics
from app.telemetry import metrics

router = APIRouter()


@router.get(
    "/status",
    response_model=HealthStatus,
    summary="Estado general del sistema",
)
async def read_status() -> HealthStatus:
    snapshot = metrics.snapshot_notes()
    return HealthStatus(
        status="ok",
        metrics=NoteMetrics(
            attempts=snapshot.attempts,
            successes=snapshot.successes,
            http_errors=snapshot.http_errors,
            network_errors=snapshot.network_errors,
            invalid_responses=snapshot.invalid_responses,
            retries=snapshot.retries,
        ),
    )


