from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

import pytest
from httpx import AsyncClient

from app.container import session_store, session_manager, note_builder
from app.dependencies import (
    get_interaction_service,
    get_note_publisher,
    get_osm_client,
)
from app.services.interaction_service import InteractionService
from app.services.note_publisher import NotePublisher
from app.services.osm_client import OSMClient, OSMNoteResponse


class FakeOSMClient(OSMClient):
    def __init__(self) -> None:
        self._counter = 0

    async def create_anonymous_note(
        self,
        latitude: float,
        longitude: float,
        text: str,
    ) -> OSMNoteResponse:
        self._counter += 1
        created_at = datetime.now(timezone.utc)
        return OSMNoteResponse(
            note_id=str(self._counter),
            url=f"https://example.org/note/{self._counter}",
            created_at=created_at,
        )

    async def close(self) -> None:  # pragma: no cover - no resources to close
        return None
from app.main import create_app


@pytest.fixture(autouse=True)
def _reset_session_store() -> Iterator[None]:
    session_store.clear()
    yield
    session_store.clear()


@pytest.fixture()
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app()
    fake_client = FakeOSMClient()
    note_publisher = NotePublisher(fake_client)
    interaction_service = InteractionService(
        session_manager=session_manager,
        note_builder=note_builder,
        note_publisher=note_publisher,
    )

    app.dependency_overrides[get_osm_client] = lambda: fake_client
    app.dependency_overrides[get_note_publisher] = lambda: note_publisher
    app.dependency_overrides[get_interaction_service] = lambda: interaction_service

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

