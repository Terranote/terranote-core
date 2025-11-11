from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.interactions import NotePreview


class NoteCreateRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    text: str = Field(..., min_length=1, max_length=4096)
    created_at: datetime | None = None


class NoteCreateResponse(NotePreview):
    pass


