from __future__ import annotations

import time
from typing import Literal

import httpx

from app.config import settings
from app.services.osm_client import OSMClient

HealthStatus = Literal["ok", "degraded", "down"]


class DependencyHealth:
    """Health status of a dependency."""

    def __init__(self, status: HealthStatus, message: str | None = None) -> None:
        self.status = status
        self.message = message


class HealthCheckService:
    """Service for checking health of the application and its dependencies."""

    def __init__(self, osm_client: OSMClient) -> None:
        self._osm_client = osm_client
        self._start_time = time.time()

    async def check_osm(self) -> DependencyHealth:
        """Check OSM API availability."""
        try:
            # Use a lightweight check: try to reach the API base URL
            async with httpx.AsyncClient(
                base_url=settings.osm_api_base_url,
                timeout=2.0,
            ) as client:
                # Try to reach the API with a HEAD request to a known endpoint
                # Using the API version endpoint which is lightweight
                response = await client.head("/api/versions", follow_redirects=True)
                if response.status_code < 500:
                    return DependencyHealth("ok")
                return DependencyHealth(
                    "degraded", f"OSM API returned status {response.status_code}"
                )
        except httpx.TimeoutException:
            return DependencyHealth("down", "OSM API timeout")
        except Exception as e:
            return DependencyHealth("down", f"OSM API unreachable: {str(e)}")

    async def check_health(self) -> dict:
        """Check overall health of the application."""
        osm_health = await self.check_osm()

        # Determine overall status
        # 'down' only if OSM is down
        # 'degraded' if OSM is degraded
        overall_status: HealthStatus = "ok"
        if osm_health.status == "down":
            overall_status = "down"
        elif osm_health.status == "degraded":
            overall_status = "degraded"

        uptime = int(time.time() - self._start_time)

        return {
            "status": overall_status,
            "uptime": uptime,
            "version": settings.api_version,
            "environment": settings.environment,
            "dependencies": {
                "osm": {
                    "status": osm_health.status,
                    "message": osm_health.message,
                }
            },
        }

