from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Dict

from prometheus_client import CollectorRegistry, Counter, generate_latest


@dataclass(frozen=True)
class NotePublicationSnapshot:
    attempts: int
    successes: int
    http_errors: int
    network_errors: int
    invalid_responses: int
    retries: int


_COUNTER_DEFINITIONS: Dict[str, Dict[str, str]] = {
    "note_publication_attempts": {
        "metric": "terranote_note_publication_attempts_total",
        "description": "Total note publication attempts",
    },
    "note_publication_successes": {
        "metric": "terranote_note_publication_successes_total",
        "description": "Total successful note publications",
    },
    "note_publication_http_errors": {
        "metric": "terranote_note_publication_http_errors_total",
        "description": "Total note publication HTTP errors",
    },
    "note_publication_network_errors": {
        "metric": "terranote_note_publication_network_errors_total",
        "description": "Total note publication network errors",
    },
    "note_publication_invalid_responses": {
        "metric": "terranote_note_publication_invalid_responses_total",
        "description": "Total invalid responses from OSM API",
    },
    "note_publication_retries": {
        "metric": "terranote_note_publication_retries_total",
        "description": "Total note publication retries",
    },
}


class Telemetry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._initialize_counters()

    def _initialize_counters(self) -> None:
        self._registry = CollectorRegistry()
        self._counters: Dict[str, int] = {}
        self._prom_counters: Dict[str, Counter] = {}
        for name, definition in _COUNTER_DEFINITIONS.items():
            self._counters[name] = 0
            self._prom_counters[name] = Counter(
                definition["metric"],
                definition["description"],
                registry=self._registry,
            )

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value
            counter = self._prom_counters.get(name)
            if counter is not None:
                counter.inc(value)

    def reset(self) -> None:
        with self._lock:
            self._initialize_counters()

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

    def export_prometheus(self) -> bytes:
        with self._lock:
            return generate_latest(self._registry)


metrics = Telemetry()
