from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.config import settings
from app.dependencies import get_note_publisher
from app.schemas.notes import NoteCreateRequest, NoteCreateResponse
from app.services.note_builder import NoteDraft
from app.services.note_publisher import NoteCreationResult, NotePublisher

router = APIRouter()


@router.post(
    "/notes/anonymous",
    response_model=NoteCreateResponse,
    summary="Crea una nota anónima en OSM (stub fase 1)",
)
async def create_anonymous_note(
    request: NoteCreateRequest,
    publisher: NotePublisher = Depends(get_note_publisher),
) -> NoteCreateResponse:
    created_at = request.created_at or datetime.now(timezone.utc)
    draft = NoteDraft(
        text=f"{request.text}\n-- {settings.note_system_identifier}",
        latitude=request.latitude,
        longitude=request.longitude,
        created_at=created_at,
    )
    result: NoteCreationResult = await publisher.create_anonymous_note(draft)
    return NoteCreateResponse(
        note_id=result.note_id,
        url=result.url,
        latitude=draft.latitude,
        longitude=draft.longitude,
        text=draft.text,
        created_at=result.created_at,
    )

