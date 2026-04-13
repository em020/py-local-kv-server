import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import EntityNotFoundError, PermissionDeniedError
from app.domain.kv.exceptions import KVBaseException

logger = logging.getLogger(__name__)


async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
    logger.error(
        "Entity not found on %s %s: %s",
        request.method,
        request.url.path,
        exc.message,
    )
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "code": "NOT_FOUND"}
    )


async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    logger.error(
        "Permission denied on %s %s: %s",
        request.method,
        request.url.path,
        exc.message,
    )
    return JSONResponse(
        status_code=403,
        content={"detail": "You do not have permission to perform this action.", "code": "FORBIDDEN"}
    )


async def kv_domain_exception_handler(request: Request, exc: KVBaseException):
    """
    Catches KVStorageLimitReachedError, InvalidKeyFormatError, etc.
    and returns a consistent JSON structure.
    """
    logger.error(
        "KV domain error on %s %s [%s]: %s",
        request.method,
        request.url.path,
        exc.code,
        exc.message,
    )
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


async def universal_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "INTERNAL_SERVER_ERROR"},
    )


def register_exception_handlers(app: FastAPI):
    # Core Handlers
    app.add_exception_handler(EntityNotFoundError, entity_not_found_handler)
    app.add_exception_handler(PermissionDeniedError, permission_denied_handler)

    # Domain Handlers (Catching the base catches all subclasses)
    app.add_exception_handler(KVBaseException, kv_domain_exception_handler)

    # Catch-all for unexpected internal errors.
    app.add_exception_handler(Exception, universal_exception_handler)
