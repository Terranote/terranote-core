from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.config import settings


@dataclass
class OSMNoteResponse:
    note_id: str
    url: str
    created_at: datetime


def _parse_osm_datetime(raw: str) -> datetime:
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    return datetime.fromisoformat(raw).astimezone(timezone.utc)


class OSMClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        transport: Optional[httpx.AsyncBaseTransport] = None,
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



