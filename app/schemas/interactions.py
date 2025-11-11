from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator


class InteractionChannel(str, Enum):
    whatsapp = "whatsapp"
    telegram = "telegram"
    test = "test"


class InteractionOutcomeStatus(str, Enum):
    accepted = "accepted"
    note_created = "note_created"
    discarded = "discarded"


class BasePayload(BaseModel):
    type: str


class TextPayload(BasePayload):
    type: Literal["text"]
    text: str = Field(..., min_length=1, max_length=2048)


class LocationPayload(BasePayload):
    type: Literal["location"]
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


InteractionPayload = Union[TextPayload, LocationPayload]


class InteractionRequest(BaseModel):
    channel: InteractionChannel
    user_id: str = Field(..., min_length=1)
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: InteractionPayload

    @model_validator(mode="after")
    def ensure_timezone(self) -> "InteractionRequest":
        if self.sent_at.tzinfo is None:
            self.sent_at = self.sent_at.replace(tzinfo=timezone.utc)
        return self


class NotePreview(BaseModel):
    note_id: str
    url: Optional[str] = None
    latitude: float
    longitude: float
    text: str
    created_at: datetime


class InteractionResponse(BaseModel):
    status: InteractionOutcomeStatus
    detail: Optional[str] = None
    note: Optional[NotePreview] = None


