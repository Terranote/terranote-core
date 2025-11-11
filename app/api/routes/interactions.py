from fastapi import APIRouter, Depends

from app.dependencies import get_interaction_service
from app.schemas.interactions import InteractionRequest, InteractionResponse
from app.services.interaction_service import InteractionService

router = APIRouter()


@router.post(
    "/interactions",
    response_model=InteractionResponse,
    summary="Recibe interacciones desde adaptadores de mensajería",
    description="Consulta `docs/interfaces.md` para el contrato completo de entrada y salida.",
)
async def receive_interaction(
    payload: InteractionRequest,
    service: InteractionService = Depends(get_interaction_service),
) -> InteractionResponse:
    return await service.process_interaction(payload)


