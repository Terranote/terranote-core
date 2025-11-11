from app.container import interaction_service, note_publisher, osm_client
from app.services.interaction_service import InteractionService
from app.services.note_publisher import NotePublisher
from app.services.osm_client import OSMClient


def get_interaction_service() -> InteractionService:
    return interaction_service


def get_note_publisher() -> NotePublisher:
    return note_publisher


def get_osm_client() -> OSMClient:
    return osm_client

