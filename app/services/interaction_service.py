from __future__ import annotations

from app.core.sessions import SessionDecision, SessionManager
from app.schemas.interactions import (
    InteractionOutcomeStatus,
    InteractionRequest,
    InteractionResponse,
    NotePreview,
)
from app.services.note_builder import NoteBuilder
from app.services.note_publisher import NotePublisher


class InteractionService:
    def __init__(
        self,
        session_manager: SessionManager,
        note_builder: NoteBuilder,
        note_publisher: NotePublisher,
    ) -> None:
        self._session_manager = session_manager
        self._note_builder = note_builder
        self._note_publisher = note_publisher

    async def process_interaction(
        self,
        request: InteractionRequest,
    ) -> InteractionResponse:
        payload_type = request.payload.type
        if payload_type == "text":
            decision = self._session_manager.handle_text(
                channel=request.channel,
                user_id=request.user_id,
                text=request.payload.text,  # type: ignore[attr-defined]
                timestamp=request.sent_at,
            )
        elif payload_type == "location":
            decision = self._session_manager.handle_location(
                channel=request.channel,
                user_id=request.user_id,
                latitude=request.payload.latitude,  # type: ignore[attr-defined]
                longitude=request.payload.longitude,  # type: ignore[attr-defined]
                timestamp=request.sent_at,
            )
        else:
            return InteractionResponse(
                status=InteractionOutcomeStatus.discarded,
                detail="unsupported_payload",
            )

        return await self._map_decision(decision)

    async def _map_decision(self, decision: SessionDecision) -> InteractionResponse:
        if decision.status == "note_ready" and decision.note is not None:
            draft = self._note_builder.build(decision.note)
            result = await self._note_publisher.create_anonymous_note(draft)
            return InteractionResponse(
                status=InteractionOutcomeStatus.note_created,
                note=NotePreview(
                    note_id=result.note_id,
                    url=result.url,
                    latitude=draft.latitude,
                    longitude=draft.longitude,
                    text=draft.text,
                    created_at=result.created_at,
                ),
            )

        if decision.status == "discarded":
            return InteractionResponse(
                status=InteractionOutcomeStatus.discarded,
                detail=decision.detail,
            )

        return InteractionResponse(
            status=InteractionOutcomeStatus.accepted,
            detail=decision.detail,
        )


