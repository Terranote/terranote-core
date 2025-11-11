from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Dict


@dataclass(frozen=True)
class NotePublicationSnapshot:
    attempts: int
    successes: int
    http_errors: int
    network_errors: int
    invalid_responses: int
    retries: int


class Telemetry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: Dict[str, int] = {
            "note_publication_attempts": 0,
            "note_publication_successes": 0,
            "note_publication_http_errors": 0,
            "note_publication_network_errors": 0,
            "note_publication_invalid_responses": 0,
            "note_publication_retries": 0,
        }

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

    def reset(self) -> None:
        with self._lock:
            for key in self._counters:
                self._counters[key] = 0

    def snapshot_notes(self) -> NotePublicationSnapshot:
        with self._lock:
            return NotePublicationSnapshot(
                attempts=self._counters.get("note_publication_attempts", 0),
                successes=self._counters.get("note_publication_successes", 0),
                http_errors=self._counters.get("note_publication_http_errors", 0),
                network_errors=self._counters.get("note_publication_network_errors", 0),
                invalid_responses=self._counters.get(
                    "note_publication_invalid_responses", 0
                ),
                retries=self._counters.get("note_publication_retries", 0),
            )


metrics = Telemetry()

