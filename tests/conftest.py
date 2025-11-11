import sys
from collections.abc import AsyncIterator, Iterator
from datetime import datetime
from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport, AsyncClient, MockTransport

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app import config  # noqa: E402
from app.container import session_store, session_manager, note_builder  # noqa: E402
from app.dependencies import (  # noqa: E402
    get_interaction_service,
    get_note_publisher,
    get_osm_client,
    get_notification_service,
)
from app.main import create_app  # noqa: E402
from app.services.interaction_service import InteractionService  # noqa: E402
from app.services.note_publisher import NotePublisher  # noqa: E402
from app.services.osm_client import OSMClient, OSMNoteResponse  # noqa: E402
from app.services.notification import NotificationService, NoteNotification  # noqa: E402
from app.telemetry import metrics  # noqa: E402


class FakeOSMClient(OSMClient):
    def __init__(self) -> None:
        self._counter = 0
        self._exceptions: list[Exception] = []

    def queue_http_error(self, status_code: int, times: int = 1) -> None:
        request = httpx.Request("POST", "https://api.test-osm.org/api/0.6/notes.json")
        for _ in range(times):
            response = httpx.Response(status_code, request=request)
            self._exceptions.append(
                httpx.HTTPStatusError(
                    "HTTP error", request=request, response=response
                )
            )

    def queue_request_error(self, times: int = 1) -> None:
        request = httpx.Request("POST", "https://api.test-osm.org/api/0.6/notes.json")
        for _ in range(times):
            self._exceptions.append(httpx.RequestError("network error", request=request))

    def queue_invalid_response(self) -> None:
        self._exceptions.append(ValueError("invalid response"))

    async def create_anonymous_note(
        self,
        latitude: float,
        longitude: float,
        text: str,
    ) -> OSMNoteResponse:
        if self._exceptions:
            raise self._exceptions.pop(0)

        self._counter += 1
        created_at = datetime.now(datetime.UTC)
        return OSMNoteResponse(
            note_id=str(self._counter),
            url=f"https://example.org/note/{self._counter}",
            created_at=created_at,
        )

    async def close(self) -> None:  # pragma: no cover - no recursos
        return None


class DummyNotificationService(NotificationService):
    def __init__(self, transport: httpx.BaseTransport | None = None) -> None:
        super().__init__()
        if transport is not None:
            self._client = httpx.AsyncClient(timeout=5.0, transport=transport)
        self.notifications: list[NoteNotification] = []

    async def notify_note_created(self, notification: NoteNotification) -> None:
        await super().notify_note_created(notification)
        self.notifications.append(notification)


@pytest.fixture(autouse=True)
def _override_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "settings", config.Settings(), raising=False)


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
def notification_service(monkeypatch: pytest.MonkeyPatch) -> DummyNotificationService:
    async def _mock_endpoint(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "ok"})

    monkeypatch.setenv("NOTIFIER_WHATSAPP_ENDPOINT", "http://test-notifier/whatsapp")
    monkeypatch.setenv("NOTIFIER_TELEGRAM_ENDPOINT", "http://test-notifier/telegram")
    transport = MockTransport(_mock_endpoint)
    service = DummyNotificationService(transport=transport)
    return service


@pytest.fixture(autouse=True)
def _patch_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _noop(_: float) -> None:
        return None

    monkeypatch.setattr("app.services.note_publisher.asyncio.sleep", _noop)


@pytest.fixture()
async def client(
    fake_osm_client: FakeOSMClient,
    notification_service: DummyNotificationService,
) -> AsyncIterator[AsyncClient]:
    app = create_app()
    note_publisher = NotePublisher(fake_osm_client)
    interaction_service = InteractionService(
        session_manager=session_manager,
        note_builder=note_builder,
        note_publisher=note_publisher,
        notification_service=notification_service,
    )

    app.dependency_overrides[get_osm_client] = lambda: fake_osm_client
    app.dependency_overrides[get_note_publisher] = lambda: note_publisher
    app.dependency_overrides[get_notification_service] = lambda: notification_service
    app.dependency_overrides[get_interaction_service] = lambda: interaction_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client

