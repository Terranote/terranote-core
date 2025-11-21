import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient) -> None:
    response = await client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "terranote_note_publication_attempts_total" in body
    # Check for new HTTP metrics
    assert "terranote_http_requests_total" in body
    assert "terranote_http_request_duration_seconds" in body
    # Check for OSM API metrics
    assert "terranote_osm_api_calls_total" in body
    assert "terranote_osm_api_call_duration_seconds" in body
