from datetime import UTC, datetime

import httpx
import pytest

from app.services.osm_client import OSMClient, OSMNoteResponse, _parse_osm_datetime


def _mock_osm_response(request: httpx.Request) -> httpx.Response:
    assert request.method == "POST"
    params = dict(request.url.params)
    assert params["lat"] == "4.7110000"
    assert params["lon"] == "-74.0721000"
    assert "text" in params
    payload = {
        "properties": {
            "id": 123456,
            "url": "https://www.openstreetmap.org/note/123456",
            "date_created": "2025-11-11T10:00:00Z",
        }
    }
    return httpx.Response(200, json=payload)


@pytest.mark.asyncio
async def test_osm_client_creates_note_with_mock_transport() -> None:
    transport = httpx.MockTransport(_mock_osm_response)
    client = OSMClient(base_url="https://api.test-osm.org", transport=transport)
    response: OSMNoteResponse = await client.create_anonymous_note(
        latitude=4.711,
        longitude=-74.0721,
        text="Testing note",
    )
    await client.close()
    assert response.note_id == "123456"
    assert response.url.endswith("/123456")
    assert response.created_at == datetime(2025, 11, 11, 10, 0, tzinfo=UTC)


def test_parse_osm_datetime_supports_z_suffix() -> None:
    parsed = _parse_osm_datetime("2025-11-11T10:00:00Z")
    assert parsed.tzinfo is not None
    assert parsed == datetime(2025, 11, 11, 10, 0, tzinfo=UTC)
