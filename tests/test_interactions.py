from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from tests.conftest import DummyNotificationService, FakeOSMClient

from app.config import settings
from app.container import session_store


@pytest.mark.asyncio
async def test_interaction_text_then_location_creates_note(
    client: AsyncClient,
    notification_service: DummyNotificationService,
) -> None:
    sent_at = datetime.now(timezone.utc)
    response = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-123",
            "sent_at": sent_at.isoformat(),
            "payload": {
                "type": "text",
                "text": "Hay una vía cerrada por obras.",
            },
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "accepted"
    assert body["detail"] == "awaiting_location"

    location_at = sent_at + timedelta(seconds=10)
    response = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-123",
            "sent_at": location_at.isoformat(),
            "payload": {
                "type": "location",
                "latitude": 4.711,
                "longitude": -74.0721,
            },
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "note_created"
    assert body["note"]["latitude"] == pytest.approx(4.711)
    assert body["note"]["longitude"] == pytest.approx(-74.0721)
    assert "Terranote Core" in body["note"]["text"]

    assert len(notification_service.notifications) == 1
    note_notification = notification_service.notifications[0]
    assert note_notification.user_id == "user-123"
    assert note_notification.channel.value == "whatsapp"


@pytest.mark.asyncio
async def test_missing_location_is_discarded_after_timeout(
    client: AsyncClient,
    notification_service: DummyNotificationService,
) -> None:
    sent_at = datetime.now(timezone.utc)
    second_at = sent_at + timedelta(seconds=21)

    first = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-456",
            "sent_at": sent_at.isoformat(),
            "payload": {"type": "text", "text": "No hay señalización."},
        },
    )
    assert first.status_code == 200

    second = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-456",
            "sent_at": second_at.isoformat(),
            "payload": {"type": "text", "text": "Sigue igual."},
        },
    )
    body = second.json()
    assert second.status_code == 200
    assert body["status"] == "discarded"
    assert body["detail"] == "missing_location_timeout"
    assert not notification_service.notifications


@pytest.mark.asyncio
async def test_location_timeout_discards_previous_session_but_keeps_location(
    client: AsyncClient,
    notification_service: DummyNotificationService,
) -> None:
    first_at = datetime.now(timezone.utc)
    first_location = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-321",
            "sent_at": first_at.isoformat(),
            "payload": {
                "type": "location",
                "latitude": 4.5,
                "longitude": -74.0,
            },
        },
    )
    first_body = first_location.json()
    assert first_location.status_code == 200
    assert first_body["status"] == "accepted"
    assert first_body["detail"] == "awaiting_text"

    second_at = first_at + timedelta(seconds=25)
    second_location = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-321",
            "sent_at": second_at.isoformat(),
            "payload": {
                "type": "location",
                "latitude": 4.6,
                "longitude": -74.1,
            },
        },
    )
    second_body = second_location.json()
    assert second_location.status_code == 200
    assert second_body["status"] == "discarded"
    assert second_body["detail"] == "missing_text_timeout"
    assert not notification_service.notifications

    session = session_store.get("whatsapp:user-321")
    assert session is not None
    assert session.has_location()
    assert session.location.latitude == pytest.approx(4.6)
    assert session.location.longitude == pytest.approx(-74.1)


@pytest.mark.asyncio
async def test_location_then_text_creates_note(
    client: AsyncClient,
    notification_service: DummyNotificationService,
) -> None:
    sent_at = datetime.now(timezone.utc)
    location = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-789",
            "sent_at": sent_at.isoformat(),
            "payload": {
                "type": "location",
                "latitude": 4.612,
                "longitude": -74.082,
            },
        },
    )
    loc_body = location.json()
    assert location.status_code == 200
    assert loc_body["status"] == "accepted"
    assert loc_body["detail"] == "awaiting_text"

    text_at = sent_at + timedelta(seconds=15)
    text_response = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-789",
            "sent_at": text_at.isoformat(),
            "payload": {"type": "text", "text": "Hueco profundo en la vía."},
        },
    )
    text_body = text_response.json()
    assert text_response.status_code == 200
    assert text_body["status"] == "note_created"
    assert "Hueco" in text_body["note"]["text"]
    assert len(notification_service.notifications) == 1


@pytest.mark.asyncio
async def test_publisher_http_error_returns_discarded(
    client: AsyncClient,
    fake_osm_client: FakeOSMClient,
    notification_service: DummyNotificationService,
) -> None:
    fake_osm_client.queue_http_error(429)

    sent_at = datetime.now(timezone.utc)
    await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-http-error",
            "sent_at": sent_at.isoformat(),
            "payload": {"type": "text", "text": "Texto previo"},
        },
    )

    response = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-http-error",
            "sent_at": (sent_at + timedelta(seconds=5)).isoformat(),
            "payload": {
                "type": "location",
                "latitude": 4.1,
                "longitude": -73.9,
            },
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "discarded"
    assert body["detail"] == "osm_api_error"
    assert not notification_service.notifications


@pytest.mark.asyncio
async def test_publisher_retries_on_server_error(
    client: AsyncClient,
    fake_osm_client: FakeOSMClient,
    notification_service: DummyNotificationService,
) -> None:
    fake_osm_client.queue_http_error(503)

    sent_at = datetime.now(timezone.utc)
    await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-retry",
            "sent_at": sent_at.isoformat(),
            "payload": {"type": "text", "text": "Primera interacción"},
        },
    )

    response = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-retry",
            "sent_at": (sent_at + timedelta(seconds=8)).isoformat(),
            "payload": {
                "type": "location",
                "latitude": 4.2,
                "longitude": -73.95,
            },
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "note_created"
    assert len(notification_service.notifications) == 1

    status_resp = await client.get("/api/v1/status")
    metrics_body = status_resp.json()["metrics"]
    assert metrics_body == {
        "attempts": 2,
        "successes": 1,
        "http_errors": 1,
        "network_errors": 0,
        "invalid_responses": 0,
        "retries": 1,
    }


@pytest.mark.asyncio
async def test_publisher_network_error_discarded_after_retries(
    client: AsyncClient,
    fake_osm_client: FakeOSMClient,
    notification_service: DummyNotificationService,
) -> None:
    fake_osm_client.queue_request_error(times=settings.osm_max_retries + 1)

    sent_at = datetime.now(timezone.utc)
    await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-network-error",
            "sent_at": sent_at.isoformat(),
            "payload": {"type": "text", "text": "Intento con red."},
        },
    )

    response = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-network-error",
            "sent_at": (sent_at + timedelta(seconds=5)).isoformat(),
            "payload": {
                "type": "location",
                "latitude": 4.0,
                "longitude": -74.0,
            },
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "discarded"
    assert body["detail"] == "osm_api_unreachable"
    assert not notification_service.notifications

    status_resp = await client.get("/api/v1/status")
    metrics_body = status_resp.json()["metrics"]
    expected_attempts = settings.osm_max_retries + 1
    expected_retries = settings.osm_max_retries
    assert metrics_body == {
        "attempts": expected_attempts,
        "successes": 0,
        "http_errors": 0,
        "network_errors": expected_attempts,
        "invalid_responses": 0,
        "retries": expected_retries,
    }


@pytest.mark.asyncio
async def test_publisher_invalid_response_discarded(
    client: AsyncClient,
    fake_osm_client: FakeOSMClient,
    notification_service: DummyNotificationService,
) -> None:
    fake_osm_client.queue_invalid_response()

    sent_at = datetime.now(timezone.utc)
    await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-invalid",
            "sent_at": sent_at.isoformat(),
            "payload": {"type": "text", "text": "Texto de prueba."},
        },
    )

    response = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-invalid",
            "sent_at": (sent_at + timedelta(seconds=10)).isoformat(),
            "payload": {
                "type": "location",
                "latitude": 4.6,
                "longitude": -73.9,
            },
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "discarded"
    assert body["detail"] == "osm_response_invalid"
    assert not notification_service.notifications

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


@pytest.mark.asyncio
async def test_batch_offline_processing(
    client: AsyncClient,
    notification_service: DummyNotificationService,
) -> None:
    base = datetime.now(timezone.utc) - timedelta(minutes=5)
    payload = {
        "interactions": [
            {
                "channel": "whatsapp",
                "user_id": "user-batch",
                "sent_at": (base + timedelta(seconds=15)).isoformat(),
                "payload": {
                    "type": "location",
                    "latitude": 4.8,
                    "longitude": -74.05,
                },
            },
            {
                "channel": "whatsapp",
                "user_id": "user-batch",
                "sent_at": base.isoformat(),
                "payload": {
                    "type": "text",
                    "text": "Reporte enviado sin conexión.",
                },
            },
        ]
    }

    response = await client.post("/api/v1/interactions/batch", json=payload)
    body = response.json()
    assert response.status_code == 200
    assert len(body) == 2
    assert body[0]["status"] == "accepted"
    assert body[1]["status"] == "note_created"
    assert len(notification_service.notifications) == 1

