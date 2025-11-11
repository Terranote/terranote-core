"""Gestión de sesiones para agrupar interacciones de un usuario."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from app.config import settings
from app.schemas.interactions import InteractionChannel


@dataclass
class LocationRecord:
    """Ubicación enviada por el usuario junto con el instante de recepción."""

    latitude: float
    longitude: float
    received_at: datetime


@dataclass
class SessionState:
    """Estado mutable asociado a una sesión de creación de nota."""

    user_key: str
    channel: InteractionChannel
    user_id: str
    started_at: datetime
    last_interaction_at: datetime
    texts: list[str] = field(default_factory=list)
    location: LocationRecord | None = None

    def add_text(self, text: str, timestamp: datetime) -> None:
        """Registra un texto nuevo y actualiza la última interacción."""
        self.texts.append(text)
        self.last_interaction_at = timestamp

    def set_location(
        self,
        latitude: float,
        longitude: float,
        timestamp: datetime,
    ) -> None:
        """Asocia la ubicación actual a la sesión."""
        self.location = LocationRecord(
            latitude=latitude,
            longitude=longitude,
            received_at=timestamp,
        )
        self.last_interaction_at = timestamp

    def clear(self) -> None:
        """Vacía los datos acumulados."""
        self.texts.clear()
        self.location = None

    def has_text(self) -> bool:
        """True si la sesión contiene texto pendiente."""
        return len(self.texts) > 0

    def has_location(self) -> bool:
        """True si la sesión dispone de una ubicación."""
        return self.location is not None

    def expired(self, timestamp: datetime) -> bool:
        """Verifica expiración por inactividad o duración máxima."""
        return (
            timestamp - self.started_at
            > timedelta(seconds=settings.session_max_duration_seconds)
            or timestamp - self.last_interaction_at
            > timedelta(seconds=settings.session_max_gap_seconds)
        )


class SessionStore:
    def __init__(self) -> None:
        self._store: dict[str, SessionState] = {}

    def get(self, key: str) -> SessionState | None:
        return self._store.get(key)

    def upsert(
        self,
        channel: InteractionChannel,
        user_id: str,
        timestamp: datetime,
    ) -> SessionState:
        key = self._build_key(channel, user_id)
        session = self._store.get(key)
        if session is None:
            session = SessionState(
                user_key=key,
                channel=channel,
                user_id=user_id,
                started_at=timestamp,
                last_interaction_at=timestamp,
            )
            self._store[key] = session
        return session

    def delete(self, channel: InteractionChannel, user_id: str) -> None:
        self._store.pop(self._build_key(channel, user_id), None)

    def _build_key(self, channel: InteractionChannel, user_id: str) -> str:
        return f"{channel.value}:{user_id}"

    def clear(self) -> None:
        self._store.clear()


@dataclass
class NoteCandidate:
    channel: InteractionChannel
    user_id: str
    texts: list[str]
    latitude: float
    longitude: float
    started_at: datetime
    completed_at: datetime


@dataclass
class SessionDecision:
    status: str
    detail: str | None = None
    note: NoteCandidate | None = None


class SessionManager:
    def __init__(self, store: SessionStore) -> None:
        self._store = store

    def handle_text(
        self,
        channel: InteractionChannel,
        user_id: str,
        text: str,
        timestamp: datetime,
    ) -> SessionDecision:
        session = self._store.upsert(channel, user_id, timestamp)
        pending_decision: SessionDecision | None = None
        if session.expired(timestamp):
            pending_decision = self._finalize_due_to_expiration(session, timestamp)
            session = self._store.upsert(channel, user_id, timestamp)
            session.add_text(text, timestamp)
        else:
            session.add_text(text, timestamp)

        if session.has_location():
            note = self._build_note(session, timestamp)
            self._store.delete(channel, user_id)
            return SessionDecision(status="note_ready", note=note)

        if pending_decision is not None:
            return pending_decision

        return SessionDecision(status="accepted", detail="awaiting_location")

    def handle_location(
        self,
        channel: InteractionChannel,
        user_id: str,
        latitude: float,
        longitude: float,
        timestamp: datetime,
    ) -> SessionDecision:
        session = self._store.upsert(channel, user_id, timestamp)
        pending_decision: SessionDecision | None = None
        if session.expired(timestamp):
            pending_decision = self._finalize_due_to_expiration(session, timestamp)
            session = self._store.upsert(channel, user_id, timestamp)
            session.set_location(latitude, longitude, timestamp)
            if session.has_text():
                note = self._build_note(session, timestamp)
                self._store.delete(channel, user_id)
                return SessionDecision(status="note_ready", note=note)
        else:
            if session.has_location() and session.has_text():
                note = self._build_note(session, timestamp)
                self._store.delete(channel, user_id)
                new_session = self._store.upsert(channel, user_id, timestamp)
                new_session.set_location(latitude, longitude, timestamp)
                return SessionDecision(status="note_ready", note=note)

            session.set_location(latitude, longitude, timestamp)
            if session.has_text():
                note = self._build_note(session, timestamp)
                self._store.delete(channel, user_id)
                return SessionDecision(status="note_ready", note=note)

        if pending_decision is not None:
            return pending_decision

        return SessionDecision(status="accepted", detail="awaiting_text")

    def _finalize_due_to_expiration(
        self,
        session: SessionState,
        timestamp: datetime,
    ) -> SessionDecision:
        if session.has_text() and session.has_location():
            note = self._build_note(session, timestamp)
            self._store.delete(session.channel, session.user_id)
            return SessionDecision(status="note_ready", note=note)

        detail = (
            "missing_location_timeout"
            if session.has_text()
            else "missing_text_timeout"
        )
        self._store.delete(session.channel, session.user_id)
        return SessionDecision(status="discarded", detail=detail)

    def _build_note(self, session: SessionState, timestamp: datetime) -> NoteCandidate:
        assert session.location is not None
        return NoteCandidate(
            channel=session.channel,
            user_id=session.user_id,
            texts=list(session.texts),
            latitude=session.location.latitude,
            longitude=session.location.longitude,
            started_at=session.started_at,
            completed_at=timestamp,
        )

