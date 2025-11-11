from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from pathlib import Path
import sys

import httpx
import pytest
from httpx import AsyncClient

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.container import session_store, session_manager, note_builder  # noqa: E402
from app.dependencies import (  # noqa: E402
    get_interaction_service,
    get_note_publisher,
    get_osm_client,
)
from app.main import create_app  # noqa: E402
from app.services.interaction_service import InteractionService  # noqa: E402
from app.services.note_publisher import NotePublisher  # noqa: E402
from app.services.osm_client import OSMClient, OSMNoteResponse  # noqa: E402
from app.telemetry import metrics  # noqa: E402


class FakeOSMClient(OSMClient):
    def __init__(self) -> None:
        self._counter = 0
        self._next_exception: Exception | None = None

    def queue_http_error(self, status_code: int) -> None:
        request = httpx.Request("POST", "https://api.test-osm.org/api/0.6/notes.json")
        response = httpx.Response(status_code, request=request)
        self._next_exception = httpx.HTTPStatusError(
            "HTTP error", request=request, response=response
        )

    def queue_request_error(self) -> None:
        request = httpx.Request("POST", "https://api.test-osm.org/api/0.6/notes.json")
        self._next_exception = httpx.RequestError("network error", request=request)

    def queue_invalid_response(self) -> None:
        self._next_exception = ValueError("invalid response")

    async def create_anonymous_note(
        self,
        latitude: float,
        longitude: float,
        text: str,
    ) -> OSMNoteResponse:
        if self._next_exception is not None:
            exc = self._next_exception
            self._next_exception = None
            raise exc

        self._counter += 1
        created_at = datetime.now(timezone.utc)
        return OSMNoteResponse(
            note_id=str(self._counter),
            url=f"https://example.org/note/{self._counter}",
            created_at=created_at,
        )

    async def close(self) -> None:  # pragma: no cover - no resources to close
        return None


@pytest.fixture(autouse=True)
def _reset_session_store() -> Iterator[None]:
    session_store.clear()
    metrics.reset()
    yield
    session_store.clear()
    metrics.reset()


@pytest.fixture()
def fake_osm_client() -> FakeOSMClient:
    return FakeOSMClient()


@pytest.fixture()
async def client(fake_osm_client: FakeOSMClient) -> AsyncIterator[AsyncClient]:
    app = create_app()
    note_publisher = NotePublisher(fake_osm_client)
    interaction_service = InteractionService(
        session_manager=session_manager,
        note_builder=note_builder,
        note_publisher=note_publisher,
    )

    app.dependency_overrides[get_osm_client] = lambda: fake_osm_client
    app.dependency_overrides[get_note_publisher] = lambda: note_publisher
    app.dependency_overrides[get_interaction_service] = lambda: interaction_service

    async with AsyncClient(app=app, base_url="http://testserver") as async_client:
        yield async_client

