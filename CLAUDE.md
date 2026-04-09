# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server (foreground)
uvicorn main:app --host 127.0.0.1 --port 8000

# Run server (background, idempotent via PID file)
./start.sh
./start.sh --host 0.0.0.0 --port 9000

# Run tests
pip install pytest httpx
pytest tests/

# Run a single test
pytest tests/test_main.py::test_save_string_returns_ok
```

## Architecture

Single-file FastAPI application (`main.py`) implementing a local key-value HTTP store.

**Store model:** In-memory dict (`_store`) mapping server-generated keys (`secrets.token_urlsafe(8)`) to `{value: str, expires_at: float}` entries. Protected by a `threading.Lock` for write operations.

**Lifecycle:** FastAPI lifespan context manager loads persisted entries from JSON on startup. Expired entries are filtered out during load.

**Persistence:** Writes are atomic (write to `.tmp`, then `os.replace`). Store is saved to disk after every write operation. File path configurable via `KV_STORE_FILE` env var.

**TTL:** Default 4 hours. Expired entries are evicted on every write via `_evict_expired()`. Expired entries are also rejected on read via `_is_expired()`.

**Logging:** Daily-rotating file handler (`logs/kv_server.log`), 30-day retention. Configurable via `KV_LOG_DIR` and `KV_LOG_BACKUP_COUNT`.

**API endpoints:**
- `POST /save_string` — stores a value, returns server-generated key
- `GET /retrieve_string?key=...` — retrieves value by key, 404 if missing/expired

**Testing:** Tests use `fastapi.testclient.TestClient` with a temp file for persistence (`KV_STORE_FILE` override in `os.environ`). The `_store` dict is cleared between tests via an autouse fixture.