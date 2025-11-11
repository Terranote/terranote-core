from collections.abc import AsyncIterator, Iterator
from pathlib import Path
import sys

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

import pytest
from httpx import AsyncClient

from app.container import session_store
from app.main import create_app


@pytest.fixture(autouse=True)
def _reset_session_store() -> Iterator[None]:
    session_store.clear()
    yield
    session_store.clear()


@pytest.fixture()
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app()
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

