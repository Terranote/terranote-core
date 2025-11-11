import pytest
from httpx import ASGITransport, AsyncClient

from fakes.osm_api import app, state


@pytest.mark.asyncio
async def test_fake_osm_success_scenario() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://fake-osm") as client:
        state.reset()
        response = await client.post(
            "/api/0.6/notes.json",
            params={"lat": 4.7, "lon": -74.1, "text": "Prueba"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["properties"]["status"] == "open"


@pytest.mark.asyncio
async def test_fake_osm_http_error_scenario() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://fake-osm") as client:
        await client.post(
            "/__control__/scenario",
            json={"mode": "http_error", "status_code": 429, "delay_ms": 0},
        )
        response = await client.post(
            "/api/0.6/notes.json",
            params={"lat": 4.7, "lon": -74.1, "text": "Prueba"},
        )
        assert response.status_code == 429
        await client.post("/__control__/reset")

