from fastapi import APIRouter, Depends

from app.dependencies import get_interaction_service
from app.schemas.interactions import (
    InteractionBatchRequest,
    InteractionRequest,
    InteractionResponse,
)
from app.services.interaction_service import InteractionService

router = APIRouter()


@router.post(
    "/interactions",
    response_model=InteractionResponse,
    summary="Recibe interacciones desde adaptadores de mensajería",
    description=(
        "Consulta `docs/interfaces.md` para el contrato completo "
        "de entrada y salida."
    ),
)
async def receive_interaction(
    payload: InteractionRequest,
    service: InteractionService = Depends(get_interaction_service),
) -> InteractionResponse:
    return await service.process_interaction(payload)


@router.post(
    "/interactions/batch",
    response_model=list[InteractionResponse],
    summary="Procesa interacciones recibidas en lote (modo offline)",
)
async def receive_interaction_batch(
    payload: InteractionBatchRequest,
    service: InteractionService = Depends(get_interaction_service),
) -> list[InteractionResponse]:
    return await service.process_interaction_batch(payload.interactions)


