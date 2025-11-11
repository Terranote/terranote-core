import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_status_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/status")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


