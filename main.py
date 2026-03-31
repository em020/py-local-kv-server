"""Minimalist local KV HTTP service using FastAPI."""

import json
import logging
import logging.handlers
import os
import secrets
import threading
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_TTL_SECONDS: int = 4 * 60 * 60  # 4 hours
STORE_FILE: str = os.environ.get("KV_STORE_FILE", "kv_store.json")
LOG_DIR: str = os.environ.get("KV_LOG_DIR", "logs")
LOG_BACKUP_COUNT: int = int(os.environ.get("KV_LOG_BACKUP_COUNT", "30"))

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------


def _setup_logging() -> None:
    """Add a daily-rotating file handler to the root logger.

    Rotates at midnight; keeps LOG_BACKUP_COUNT days of backups (default 30).
    Rotated files are named kv_server.log.YYYY-MM-DD.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, "kv_server.log")
    handler = logging.handlers.TimedRotatingFileHandler(
        log_path,
        when="midnight",
        interval=1,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
        utc=False,
    )
    handler.suffix = "%Y-%m-%d"
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    root = logging.getLogger()
    root.addHandler(handler)
    if root.level == logging.NOTSET:
        root.setLevel(logging.INFO)


_setup_logging()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory store  {key: {"value": str, "expires_at": float}}
# ---------------------------------------------------------------------------

_store: dict[str, dict] = {}
_store_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------


def _load_store() -> None:
    """Load persisted entries from disk, skipping expired ones."""
    if not os.path.exists(STORE_FILE):
        return
    try:
        with open(STORE_FILE, "r", encoding="utf-8") as fh:
            data: dict = json.load(fh)
        now = time.time()
        for key, entry in data.items():
            if entry.get("expires_at", 0) > now:
                _store[key] = entry
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not load KV store from %s: %s", STORE_FILE, exc)


def _save_store() -> None:
    """Persist the current in-memory store to disk atomically."""
    tmp_path = STORE_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(_store, fh)
    os.replace(tmp_path, STORE_FILE)


def _evict_expired() -> None:
    """Remove all expired entries from memory (called on writes)."""
    now = time.time()
    expired_keys = [k for k, v in _store.items() if v["expires_at"] <= now]
    for k in expired_keys:
        del _store[k]


def _is_expired(entry: dict) -> bool:
    """Return True if the given store entry has passed its expiry time."""
    return entry["expires_at"] <= time.time()


# ---------------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_store()
    yield


app = FastAPI(title="Local KV Server", lifespan=lifespan)

# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class SaveRequest(BaseModel):
    value: str
    ttl_seconds: Optional[int] = None


class SaveResponse(BaseModel):
    key: str
    status: str


class RetrieveResponse(BaseModel):
    key: str
    value: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/save_string", response_model=SaveResponse)
def save_string(req: SaveRequest) -> SaveResponse:
    """Store a string value, generate a unique key, and return it."""
    ttl = req.ttl_seconds if req.ttl_seconds is not None else DEFAULT_TTL_SECONDS
    if ttl <= 0:
        raise HTTPException(status_code=400, detail="ttl_seconds must be positive")
    with _store_lock:
        _evict_expired()
        for _ in range(10):
            key = secrets.token_urlsafe(8)
            if key not in _store:
                break
        else:
            raise HTTPException(status_code=503, detail="Could not generate a unique key")
        _store[key] = {
            "value": req.value,
            "expires_at": time.time() + ttl,
        }
    _save_store()
    return SaveResponse(key=key, status="ok")


@app.get("/retrieve_string", response_model=RetrieveResponse)
def retrieve_string(key: str) -> RetrieveResponse:
    """Retrieve the string value stored under *key*."""
    entry = _store.get(key)
    if entry is None or _is_expired(entry):
        if entry is not None:
            del _store[key]
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    return RetrieveResponse(key=key, value=entry["value"])
