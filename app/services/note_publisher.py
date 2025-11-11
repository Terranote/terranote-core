from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
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
        response: OSMNoteResponse = await self._osm_client.create_anonymous_note(
            latitude=draft.latitude,
            longitude=draft.longitude,
            text=draft.text,
        )
        return NoteCreationResult(
            note_id=response.note_id,
            url=response.url,
            created_at=response.created_at,
        )


