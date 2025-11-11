from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_anonymous_note_stub(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/notes/anonymous",
        json={
            "latitude": 4.711,
            "longitude": -74.0721,
            "text": "Prueba manual de nota.",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["note_id"]
    assert body["url"].startswith("https://www.openstreetmap.org/note/")
    assert "Terranote Core" in body["text"]


