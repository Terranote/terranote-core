from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import httpx

from app.services.exceptions import NotePublishingError
from app.services.note_builder import NoteDraft
from app.services.osm_client import OSMClient, OSMNoteResponse

@dataclass
class NoteCreationResult:
    note_id: str
    url: Optional[str]
    created_at: datetime


class NotePublisher:
    def __init__(self, osm_client: OSMClient) -> None:
        self._osm_client = osm_client

    async def create_anonymous_note(self, draft: NoteDraft) -> NoteCreationResult:
        try:
            response: OSMNoteResponse = await self._osm_client.create_anonymous_note(
                latitude=draft.latitude,
                longitude=draft.longitude,
                text=draft.text,
            )
        except httpx.HTTPStatusError as exc:
            raise NotePublishingError(
                message="osm_api_error",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise NotePublishingError(message="osm_api_unreachable") from exc
        except ValueError as exc:
            raise NotePublishingError(message="osm_response_invalid") from exc
        return NoteCreationResult(
            note_id=response.note_id,
            url=response.url,
            created_at=response.created_at,
        )


