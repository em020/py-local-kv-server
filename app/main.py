from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.api import api_router
from app.api.exception_handlers import register_exception_handlers
from app.bootstrap import initialize_app_state
from app.core.config import settings
from app.core.logging import setup_logging
from app.domain.kv.routers.router_legacy import router as kv_legacy


setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_app_state(app)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_title, lifespan=lifespan)

    # 1. Register Exception Handlers
    register_exception_handlers(app)

    # 2. Include Routers
    app.include_router(kv_legacy)
    app.include_router(api_router)

    return app


app = create_app()
