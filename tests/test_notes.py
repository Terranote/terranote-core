from datetime import datetime

import pytest
from httpx import AsyncClient

from tests.conftest import FakeOSMClient

from app.config import settings


@pytest.mark.asyncio
async def test_create_anonymous_note_with_fake_publisher(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/notes/anonymous",
        json={
            "latitude": 4.711,
            "longitude": -74.0721,
            "text": "Prueba manual de nota.",
            "created_at": datetime.now(datetime.UTC).isoformat(),
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
    fake_osm_client.queue_http_error(503, times=settings.osm_max_retries + 1)
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

    status_resp = await client.get("/api/v1/status")
    metrics_body = status_resp.json()["metrics"]
    attempts = settings.osm_max_retries + 1
    retries = settings.osm_max_retries
    assert metrics_body == {
        "attempts": attempts,
        "successes": 0,
        "http_errors": attempts,
        "network_errors": 0,
        "invalid_responses": 0,
        "retries": retries,
    }


@pytest.mark.asyncio
async def test_create_anonymous_note_network_error(
    client: AsyncClient, fake_osm_client: FakeOSMClient
) -> None:
    fake_osm_client.queue_request_error(times=settings.osm_max_retries + 1)
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

    status_resp = await client.get("/api/v1/status")
    metrics_body = status_resp.json()["metrics"]
    attempts = settings.osm_max_retries + 1
    retries = settings.osm_max_retries
    assert metrics_body == {
        "attempts": attempts,
        "successes": 0,
        "http_errors": 0,
        "network_errors": attempts,
        "invalid_responses": 0,
        "retries": retries,
    }


@pytest.mark.asyncio
async def test_create_anonymous_note_invalid_response(
    client: AsyncClient, fake_osm_client: FakeOSMClient
) -> None:
    fake_osm_client.queue_invalid_response()
    response = await client.post(
        "/api/v1/notes/anonymous",
        json={
            "latitude": 6.5,
            "longitude": -76.5,
            "text": "Nota inválida.",
        },
    )
    body = response.json()
    assert response.status_code == 502
    assert body["detail"] == "osm_response_invalid"

    status_resp = await client.get("/api/v1/status")
    metrics_body = status_resp.json()["metrics"]
    assert metrics_body == {
        "attempts": 1,
        "successes": 0,
        "http_errors": 0,
        "network_errors": 0,
        "invalid_responses": 1,
        "retries": 0,
    }
