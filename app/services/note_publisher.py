from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.services.note_builder import NoteDraft


@dataclass
class NoteCreationResult:
    note_id: str
    url: Optional[str]
    created_at: datetime


class NotePublisher:
    """Stub OSM publisher for fase 1."""

    async def create_anonymous_note(self, draft: NoteDraft) -> NoteCreationResult:
        note_identifier = uuid4().hex
        url = f"https://www.openstreetmap.org/note/{note_identifier}"
        return NoteCreationResult(
            note_id=note_identifier,
            url=url,
            created_at=draft.created_at,
        )


