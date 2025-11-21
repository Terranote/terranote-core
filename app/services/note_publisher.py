from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime

import httpx

from app.config import settings
from app.services.exceptions import NotePublishingError
from app.services.note_builder import NoteDraft
from app.services.osm_client import OSMClient
from app.telemetry import metrics


@dataclass
class NoteCreationResult:
    note_id: str
    url: str | None
    created_at: datetime


class NotePublisher:
    """Publica notas OSM manejando reintentos, métricas y logging."""

    def __init__(self, osm_client: OSMClient) -> None:
        self._osm_client = osm_client
        self._logger = logging.getLogger(self.__class__.__name__)

    async def create_anonymous_note(self, draft: NoteDraft) -> NoteCreationResult:
        """Intenta publicar la nota anónima y retorna el resultado."""
        attempt = 0
        max_retries = settings.osm_max_retries
        backoff = settings.osm_retry_backoff_seconds

        while True:
            metrics.increment("note_publication_attempts")
            start_time = time.time()
            try:
                response = await self._osm_client.create_anonymous_note(
                    latitude=draft.latitude,
                    longitude=draft.longitude,
                    text=draft.text,
                )
                duration = time.time() - start_time
                metrics.increment("note_publication_successes")
                metrics.record_osm_api_call(status="success", duration=duration)
                if attempt > 0:
                    self._logger.info(
                        "OSM note created after retry",
                        extra={
                            "note_id": response.note_id,
                            "latitude": draft.latitude,
                            "longitude": draft.longitude,
                            "retries": attempt,
                        },
                    )
                else:
                    self._logger.info(
                        "OSM note created",
                        extra={
                            "note_id": response.note_id,
                            "latitude": draft.latitude,
                            "longitude": draft.longitude,
                        },
                    )
                return NoteCreationResult(
                    note_id=response.note_id,
                    url=response.url,
                    created_at=response.created_at,
                )
            except httpx.HTTPStatusError as exc:
                duration = time.time() - start_time
                metrics.increment("note_publication_http_errors")
                status_label = "http_error"
                if 400 <= exc.response.status_code < 500:
                    status_label = "client_error"
                elif 500 <= exc.response.status_code < 600:
                    status_label = "server_error"
                metrics.record_osm_api_call(status=status_label, duration=duration)
                if attempt < max_retries and 500 <= exc.response.status_code < 600:
                    attempt += 1
                    metrics.increment("note_publication_retries")
                    self._logger.warning(
                        "Retrying after OSM API HTTP error",
                        extra={
                            "status_code": exc.response.status_code,
                            "attempt": attempt,
                            "latitude": draft.latitude,
                            "longitude": draft.longitude,
                        },
                    )
                    await asyncio.sleep(backoff * attempt)
                    continue
                self._logger.warning(
                    "OSM API returned HTTP error",
                    extra={
                        "status_code": exc.response.status_code,
                        "latitude": draft.latitude,
                        "longitude": draft.longitude,
                    },
                )
                raise NotePublishingError(
                    message="osm_api_error",
                    status_code=exc.response.status_code,
                ) from exc
            except httpx.RequestError as exc:
                duration = time.time() - start_time
                metrics.increment("note_publication_network_errors")
                metrics.record_osm_api_call(status="network_error", duration=duration)
                if attempt < max_retries:
                    attempt += 1
                    metrics.increment("note_publication_retries")
                    self._logger.warning(
                        "Retrying after OSM API network error",
                        exc_info=exc,
                        extra={
                            "attempt": attempt,
                            "latitude": draft.latitude,
                            "longitude": draft.longitude,
                        },
                    )
                    await asyncio.sleep(backoff * attempt)
                    continue
                self._logger.error(
                    "OSM API network error",
                    exc_info=exc,
                    extra={"latitude": draft.latitude, "longitude": draft.longitude},
                )
                raise NotePublishingError(message="osm_api_unreachable") from exc
            except ValueError as exc:
                duration = time.time() - start_time
                metrics.increment("note_publication_invalid_responses")
                metrics.record_osm_api_call(status="invalid_response", duration=duration)
                self._logger.error(
                    "OSM API returned invalid response",
                    exc_info=exc,
                    extra={"latitude": draft.latitude, "longitude": draft.longitude},
                )
                raise NotePublishingError(message="osm_response_invalid") from exc

    async def close(self) -> None:
        await self._osm_client.close()
