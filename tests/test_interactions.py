from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_interaction_text_then_location_creates_note(client: AsyncClient) -> None:
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


@pytest.mark.asyncio
async def test_missing_location_is_discarded_after_timeout(client: AsyncClient) -> None:
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


@pytest.mark.asyncio
async def test_location_timeout_discards_previous_session_but_keeps_location(
    client: AsyncClient,
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

    text_at = second_at + timedelta(seconds=10)
    text_response = await client.post(
        "/api/v1/interactions",
        json={
            "channel": "whatsapp",
            "user_id": "user-321",
            "sent_at": text_at.isoformat(),
            "payload": {
                "type": "text",
                "text": "Nueva actualización después del timeout.",
            },
        },
    )
    text_body = text_response.json()
    assert text_response.status_code == 200
    assert text_body["status"] == "note_created"
    assert text_body["note"]["latitude"] == pytest.approx(4.6)
    assert text_body["note"]["longitude"] == pytest.approx(-74.1)
    assert "Terranote Core" in text_body["note"]["text"]


@pytest.mark.asyncio
async def test_location_then_text_creates_note(client: AsyncClient) -> None:
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

