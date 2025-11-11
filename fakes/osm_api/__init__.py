from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import count
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

NOTE_COUNTER = count(1)


@dataclass
class ScenarioState:
    mode: Literal[
        "success",
        "http_error",
        "network_error",
        "invalid_response",
    ] = "success"
    status_code: int = 503
    delay_ms: int = 0

    def reset(self) -> None:
        self.mode = "success"
        self.status_code = 503
        self.delay_ms = 0


state = ScenarioState()


class ScenarioPayload(BaseModel):
    mode: Literal["success", "http_error", "network_error", "invalid_response"] = Field(
        default="success"
    )
    status_code: int = Field(default=503, ge=100, le=599)
    delay_ms: int = Field(default=0, ge=0, le=60_000)


def _note_payload(lat: float, lon: float, text: str) -> dict:
    note_id = next(NOTE_COUNTER)
    created_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return {
        "type": "Feature",
        "properties": {
            "id": note_id,
            "url": f"https://www.openstreetmap.org/note/{note_id}",
            "date_created": created_at,
            "text": text,
            "status": "open",
        },
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
    }


def create_app() -> FastAPI:
    """Crea una aplicación FastAPI que simula la API OSM de creación de notas."""
    app = FastAPI(title="Fake OSM API", version="0.1.0")

    @app.post("/__control__/scenario", summary="Configura el escenario del fake OSM")
    async def configure_scenario(payload: ScenarioPayload) -> ScenarioPayload:
        """Permite definir el escenario actual de respuesta del fake."""
        state.mode = payload.mode
        state.status_code = payload.status_code
        state.delay_ms = payload.delay_ms
        return payload

    @app.post("/__control__/reset", summary="Reinicia el escenario por defecto")
    async def reset_scenario() -> dict[str, str]:
        """Restablece el comportamiento por defecto (modo success, sin delay)."""
        state.reset()
        return {"detail": "reset"}

    @app.post(
        "/api/0.6/notes.json",
        summary="Endpoint de creación de notas OSM (fake)",
    )
    async def create_note(lat: float, lon: float, text: str) -> dict:
        """Simula la creación de una nota, aplicando el escenario configurado."""
        if state.delay_ms:
            await asyncio.sleep(state.delay_ms / 1000)

        if state.mode == "http_error":
            raise HTTPException(status_code=state.status_code, detail="Simulated error")

        if state.mode == "network_error":
            raise ConnectionResetError("Simulated network failure")

        if state.mode == "invalid_response":
            return {"detail": "invalid"}

        return _note_payload(lat=lat, lon=lon, text=text)

    return app


app = create_app()

