from fastapi import APIRouter, HTTPException

from app.container import osm_client
from app.schemas.health import HealthStatus, NoteMetrics
from app.services.health_check import HealthCheckService
from app.telemetry import metrics

router = APIRouter()


@router.get(
    "/status",
    response_model=HealthStatus,
    summary="Estado general del sistema",
)
async def read_status() -> HealthStatus:
    """Health check endpoint with dependency verification and metrics."""
    health_check = HealthCheckService(osm_client)
    health_data = await health_check.check_health()

    snapshot = metrics.snapshot_notes()
    note_metrics = NoteMetrics(
        attempts=snapshot.attempts,
        successes=snapshot.successes,
        http_errors=snapshot.http_errors,
        network_errors=snapshot.network_errors,
        invalid_responses=snapshot.invalid_responses,
        retries=snapshot.retries,
    )

    return HealthStatus(
        status=health_data["status"],
        uptime=health_data["uptime"],
        version=health_data["version"],
        environment=health_data["environment"],
        dependencies=health_data["dependencies"],
        metrics=note_metrics,
    )
