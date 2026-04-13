from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import EntityNotFoundError, PermissionDeniedError
from app.domain.kv.exceptions import KVBaseException


async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "code": "NOT_FOUND"}
    )


async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code=403,
        content={"detail": "You do not have permission to perform this action.", "code": "FORBIDDEN"}
    )


async def kv_domain_exception_handler(request: Request, exc: KVBaseException):
    """
    Catches KVStorageLimitReachedError, InvalidKeyFormatError, etc.
    and returns a consistent JSON structure.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,  # e.g., "KV_LIMIT_EXCEEDED"
                "message": exc.message,  # The human-readable string
                "domain": "kv_store"  # Helps frontend route the error
            }
        }
    )


def register_exception_handlers(app: FastAPI):
    # Core Handlers
    app.add_exception_handler(EntityNotFoundError, entity_not_found_handler)
    app.add_exception_handler(PermissionDeniedError, permission_denied_handler)

    # Domain Handlers (Catching the base catches all subclasses)
    app.add_exception_handler(KVBaseException, kv_domain_exception_handler)

    # Optional: Catch-all for unexpected internal errors
    # app.add_exception_handler(Exception, universal_exception_handler)
