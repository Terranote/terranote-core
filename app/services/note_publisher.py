from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Optional

import httpx

from app.services.exceptions import NotePublishingError
from app.services.note_builder import NoteDraft
from app.services.osm_client import OSMClient, OSMNoteResponse
from app.telemetry import metrics


@dataclass
class NoteCreationResult:
    note_id: str
    url: Optional[str]
    created_at: datetime


class NotePublisher:
    def __init__(self, osm_client: OSMClient) -> None:
        self._osm_client = osm_client
        self._logger = logging.getLogger(self.__class__.__name__)

    async def create_anonymous_note(self, draft: NoteDraft) -> NoteCreationResult:
        metrics.increment("note_publication_attempts")
        try:
            response: OSMNoteResponse = await self._osm_client.create_anonymous_note(
                latitude=draft.latitude,
                longitude=draft.longitude,
                text=draft.text,
            )
            metrics.increment("note_publication_successes")
            self._logger.info(
                "OSM note created",
                extra={
                    "note_id": response.note_id,
                    "latitude": draft.latitude,
                    "longitude": draft.longitude,
                },
            )
        except httpx.HTTPStatusError as exc:
            metrics.increment("note_publication_http_errors")
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
            metrics.increment("note_publication_network_errors")
            self._logger.error(
                "OSM API network error",
                exc_info=exc,
                extra={"latitude": draft.latitude, "longitude": draft.longitude},
            )
            raise NotePublishingError(message="osm_api_unreachable") from exc
        except ValueError as exc:
            metrics.increment("note_publication_invalid_responses")
            self._logger.error(
                "OSM API returned invalid response",
                exc_info=exc,
                extra={"latitude": draft.latitude, "longitude": draft.longitude},
            )
            raise NotePublishingError(message="osm_response_invalid") from exc
        return NoteCreationResult(
            note_id=response.note_id,
            url=response.url,
            created_at=response.created_at,
        )
