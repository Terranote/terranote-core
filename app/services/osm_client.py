from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from app.config import settings


@dataclass
class OSMNoteResponse:
    """Respuesta simplificada del API de notas de OSM."""

    note_id: str
    url: str
    created_at: datetime


def _parse_osm_datetime(raw: str) -> datetime:
    """Convierte la marca de tiempo ISO de OSM en un `datetime` UTC."""

    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    return datetime.fromisoformat(raw).astimezone(UTC)


class OSMClient:
    """Cliente HTTP asíncrono para la API de notas de OpenStreetMap."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url or settings.osm_api_base_url,
            timeout=timeout_seconds or settings.osm_api_timeout_seconds,
            transport=transport,
        )

    async def create_anonymous_note(
        self,
        latitude: float,
        longitude: float,
        text: str,
    ) -> OSMNoteResponse:
        """Invoca `/api/0.6/notes.json` para crear una nota anónima."""

        params = {
            "lat": f"{latitude:.7f}",
            "lon": f"{longitude:.7f}",
            "text": text,
        }
        response = await self._client.post("/api/0.6/notes.json", params=params)
        response.raise_for_status()
        payload = response.json()
        return self._parse_note_response(payload)

    async def close(self) -> None:
        """Cierra el cliente HTTP subyacente."""

        await self._client.aclose()

    def _parse_note_response(self, payload: dict[str, Any]) -> OSMNoteResponse:
        properties = payload.get("properties") or {}
        note_id = str(properties.get("id"))
        url = properties.get("url")
        created_raw = properties.get("date_created") or properties.get("dateCreated")
        if not (note_id and url and created_raw):
            raise ValueError("Invalid OSM API response: missing expected fields")
        created_at = _parse_osm_datetime(str(created_raw))
        return OSMNoteResponse(note_id=note_id, url=url, created_at=created_at)




