from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.core.schemas.base import User

router = APIRouter(prefix="/kv/api/v1", tags=["KV v1"])


@router.get("/hello")
async def hello_world(user: User = Depends(get_current_user)) -> dict:
    """Dummy endpoint that returns hello, username."""
    return {"message": f"hello, {user.username}"}
