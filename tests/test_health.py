import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_status_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/status")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ["ok", "degraded", "down"]
    assert "uptime" in body
    assert "version" in body
    assert "environment" in body
    assert "dependencies" in body
    assert "osm" in body["dependencies"]
    assert body["metrics"] == {
        "attempts": 0,
        "successes": 0,
        "http_errors": 0,
        "network_errors": 0,
        "invalid_responses": 0,
        "retries": 0,
    }
