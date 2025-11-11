from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.config import settings
from app.core.sessions import NoteCandidate


@dataclass
class NoteDraft:
    text: str
    latitude: float
    longitude: float
    created_at: datetime


class NoteBuilder:
    def build(self, candidate: NoteCandidate) -> NoteDraft:
        body = "\n".join(candidate.texts).strip()
        if body:
            body = f"{body}\n-- {settings.note_system_identifier}"
        else:
            body = f"-- {settings.note_system_identifier}"

        return NoteDraft(
            text=body,
            latitude=candidate.latitude,
            longitude=candidate.longitude,
            created_at=candidate.completed_at,
        )

