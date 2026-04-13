from fastapi import Request

from app.domain.kv.services import KVService


def get_kv_service(request: Request) -> KVService:
    # The singleton service is attached during startup in app.bootstrap.initialize_app_state.
    return request.app.state.kv_service
