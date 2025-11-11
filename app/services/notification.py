from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Optional

from app.schemas.interactions import InteractionChannel

logger = logging.getLogger(__name__)


@dataclass
class NoteNotification:
    """Datos que se entregan al adaptador sobre una nota creada."""

    channel: InteractionChannel
    user_id: str
    note_id: str
    note_url: Optional[str]
    latitude: float
    longitude: float
    text: str
    created_at: datetime


class NotificationService:
    """Stub que notifica al adaptador cuando se crea una nota."""

    async def notify_note_created(self, notification: NoteNotification) -> None:
        logger.info(
            "Note created notification",
            extra={
                "channel": notification.channel.value,
                "user_id": notification.user_id,
                "note_id": notification.note_id,
                "note_url": notification.note_url,
            },
        )

