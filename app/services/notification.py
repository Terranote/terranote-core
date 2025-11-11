from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import httpx

from app.config import settings
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
    """Servicio que notifica al adaptador cuando se crea una nota."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=5.0)

    async def notify_note_created(self, notification: NoteNotification) -> None:
        endpoint = self._resolve_endpoint(notification.channel)
        if endpoint is None:
            logger.info(
                "Notification skipped: endpoint not configured",
                extra={
                    "channel": notification.channel.value,
                    "user_id": notification.user_id,
                },
            )
            return

        payload = {
            "channel": notification.channel.value,
            "user_id": notification.user_id,
            "note_id": notification.note_id,
            "note_url": notification.note_url,
            "latitude": notification.latitude,
            "longitude": notification.longitude,
            "text": notification.text,
            "created_at": notification.created_at.isoformat(),
        }
        try:
            response = await self._client.post(endpoint, json=payload)
            response.raise_for_status()
            logger.info(
                "Notification delivered",
                extra={
                    "channel": notification.channel.value,
                    "user_id": notification.user_id,
                    "note_id": notification.note_id,
                    "status_code": response.status_code,
                },
            )
        except httpx.HTTPError as exc:  # pragma: no cover - logging
            logger.warning(
                "Notification delivery failed",
                exc_info=exc,
                extra={
                    "channel": notification.channel.value,
                    "user_id": notification.user_id,
                    "note_id": notification.note_id,
                },
            )

    async def close(self) -> None:
        await self._client.aclose()

    def _resolve_endpoint(self, channel: InteractionChannel) -> Optional[str]:
        if channel == InteractionChannel.whatsapp:
            return settings.notifier_whatsapp_endpoint
        if channel == InteractionChannel.telegram:
            return settings.notifier_telegram_endpoint
        return None

