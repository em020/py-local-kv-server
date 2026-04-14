from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.core.schemas.base import User

router = APIRouter(prefix="/sample_module/api/v1", tags=["sample_module v1"])


@router.get("/hello", response_model=dict)
async def hello(
        user: User = Depends(get_current_user),
        # service: SampleService = Depends(get_sample_service),
) -> dict:
    return {"message": f"Hello, {user.username}!"}
