from app.core.sessions import SessionManager, SessionStore
from app.services.interaction_service import InteractionService
from app.services.note_builder import NoteBuilder
from app.services.note_publisher import NotePublisher
from app.services.osm_client import OSMClient

session_store = SessionStore()
session_manager = SessionManager(session_store)
note_builder = NoteBuilder()
osm_client = OSMClient()
note_publisher = NotePublisher(osm_client=osm_client)
interaction_service = InteractionService(
    session_manager=session_manager,
    note_builder=note_builder,
    note_publisher=note_publisher,
)


