from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.dependencies import get_note_publisher
from app.schemas.notes import NoteCreateRequest, NoteCreateResponse
from app.services.exceptions import NotePublishingError
from app.services.note_builder import NoteDraft
from app.services.note_publisher import NoteCreationResult, NotePublisher

router = APIRouter()


@router.post(
    "/notes/anonymous",
    response_model=NoteCreateResponse,
    summary="Crea una nota anónima en OSM",
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
    try:
        result: NoteCreationResult = await publisher.create_anonymous_note(draft)
    except NotePublishingError as exc:
        status_code = (
            exc.status_code
            if exc.status_code is not None
            else status.HTTP_502_BAD_GATEWAY
        )
        raise HTTPException(status_code=status_code, detail=exc.args[0]) from exc

    return NoteCreateResponse(
        note_id=result.note_id,
        url=result.url,
        latitude=draft.latitude,
        longitude=draft.longitude,
        text=draft.text,
        created_at=result.created_at,
    )
