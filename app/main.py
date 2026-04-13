# App initialization & exception handler registration
from fastapi import FastAPI
from app.api.api import api_router
from app.api.exception_handlers import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="My Enterprise API")

    # 1. Register Exception Handlers
    register_exception_handlers(app)

    # 2. Include Routers
    app.include_router(api_router)

    return app


app = create_app()
