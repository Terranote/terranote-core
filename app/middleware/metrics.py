from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.telemetry import metrics


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to capture HTTP request metrics."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Get route path (use the route path if available, otherwise use the request path)
        route = request.url.path
        if request.scope.get("route"):
            route = request.scope["route"].path

        metrics.record_http_request(
            method=request.method,
            route=route,
            status=response.status_code,
            duration=duration,
        )

        return response

