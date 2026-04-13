from fastapi import FastAPI, Request

from app.core.config import settings
from app.domain.kv.repositories import FileKVRepository
from app.domain.kv.services import KVService


def create_kv_service() -> KVService:
    """Build the KV service with the local file-backed repository."""
    repository = FileKVRepository(store_file=settings.kv_store_file)
    service = KVService(repository=repository)
    service.load()
    return service


def initialize_app_state(app: FastAPI) -> None:
    """Attach long-lived application services to app state."""
    app.state.kv_service = create_kv_service()
