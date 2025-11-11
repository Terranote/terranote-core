from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST

from app.telemetry import metrics

router = APIRouter()


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    include_in_schema=False,
)
async def prometheus_metrics() -> Response:
    data = metrics.export_prometheus()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

