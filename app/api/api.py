from fastapi import APIRouter
from app.domain.kv.routers.router_v1 import router as kv_v1
# from app.domain.users.router_v1 import router as users_v1

api_router = APIRouter(prefix="/bigsister")

api_router.include_router(kv_v1)
# v1_router.include_router(users_v1, prefix="/users", tags=["Users v1"])
