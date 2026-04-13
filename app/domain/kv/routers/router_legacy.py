from fastapi import APIRouter, Depends

from app.domain.kv.dependencies import get_kv_service
from app.domain.kv.schemas import RetrieveResponse, SaveRequest, SaveResponse
from app.domain.kv.services import KVService

router = APIRouter(tags=["KV legacy"])


@router.post("/save_string", response_model=SaveResponse)
async def save_string(
    req: SaveRequest,
    service: KVService = Depends(get_kv_service),
) -> SaveResponse:
    """Legacy unauthenticated save endpoint."""
    return service.save_string(req.value, req.ttl_seconds)


@router.get("/retrieve_string", response_model=RetrieveResponse)
async def retrieve_string(
    key: str,
    service: KVService = Depends(get_kv_service),
) -> RetrieveResponse:
    """Legacy unauthenticated retrieve endpoint."""
    return service.retrieve_string(key)
