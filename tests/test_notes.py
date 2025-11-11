from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from tests.conftest import FakeOSMClient


@pytest.mark.asyncio
async def test_create_anonymous_note_with_fake_publisher(client: AsyncClient) -> None:
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
    assert body["url"].startswith("https://example.org/note/")
    assert "Terranote Core" in body["text"]


@pytest.mark.asyncio
async def test_create_anonymous_note_http_error(
    client: AsyncClient, fake_osm_client: FakeOSMClient
) -> None:
    fake_osm_client.queue_http_error(503)
    response = await client.post(
        "/api/v1/notes/anonymous",
        json={
            "latitude": 5.0,
            "longitude": -75.0,
            "text": "Servicio no disponible.",
        },
    )
    body = response.json()
    assert response.status_code == 503
    assert body["detail"] == "osm_api_error"


@pytest.mark.asyncio
async def test_create_anonymous_note_network_error(
    client: AsyncClient, fake_osm_client: FakeOSMClient
) -> None:
    fake_osm_client.queue_request_error()
    response = await client.post(
        "/api/v1/notes/anonymous",
        json={
            "latitude": 6.0,
            "longitude": -76.0,
            "text": "Nota de prueba.",
        },
    )
    body = response.json()
    assert response.status_code == 502
    assert body["detail"] == "osm_api_unreachable"
