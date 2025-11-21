from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, Security, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from prometheus_client import CONTENT_TYPE_LATEST

from app.config import settings
from app.telemetry import metrics

router = APIRouter()
security = HTTPBasic()


def verify_metrics_auth(
    credentials: Annotated[HTTPBasicCredentials, Security(security)],
) -> None:
    """Verify basic auth credentials for metrics endpoint if configured."""
    if not settings.metrics_username or not settings.metrics_password:
        # No auth required if credentials are not configured
        return

    is_correct_username = credentials.username == settings.metrics_username
    is_correct_password = credentials.password == settings.metrics_password

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    include_in_schema=False,
)
async def prometheus_metrics(
    _: Annotated[None, Depends(verify_metrics_auth)],
) -> Response:
    """Prometheus metrics endpoint with optional basic authentication."""
    data = metrics.export_prometheus()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
