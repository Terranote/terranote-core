from app.container import interaction_service, note_publisher
from app.services.interaction_service import InteractionService
from app.services.note_publisher import NotePublisher


def get_interaction_service() -> InteractionService:
    return interaction_service


def get_note_publisher() -> NotePublisher:
    return note_publisher

