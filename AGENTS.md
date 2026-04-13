# Repository Guidelines

## Project Structure & Module Organization

This repository is now centered on the [`app/`](/Users/yiminsun/projects/py-local-kv-server/app) package. [`app/main.py`](/Users/yiminsun/projects/py-local-kv-server/app/main.py) creates the FastAPI app, [`app/bootstrap.py`](/Users/yiminsun/projects/py-local-kv-server/app/bootstrap.py) wires long-lived services, [`app/domain/kv/`](/Users/yiminsun/projects/py-local-kv-server/app/domain/kv) contains KV routers, schemas, services, and repositories, and [`tests/test_main.py`](/Users/yiminsun/projects/py-local-kv-server/tests/test_main.py) covers API behavior and persistence. Use [`CLAUDE.md`](/Users/yiminsun/projects/py-local-kv-server/CLAUDE.md) for the current architecture overview.

## Build, Test, and Development Commands

Install runtime dependencies with `pip install -r requirements.txt`.

Run the server in the foreground with `uvicorn app.main:app --host 127.0.0.1 --port 8000`.

Use `./start.sh` for the idempotent background launcher. Example: `./start.sh --host 0.0.0.0 --port 9000`. Use `./restart.sh` to restart the PID-managed instance and `./stop.sh` to stop it.

Install test-only dependencies with `pip install pytest httpx`, then run `pytest tests/`. For a focused check, use `pytest tests/test_main.py::test_save_string_returns_ok`.

## Coding Style & Naming Conventions

Follow the existing Python style in `app/`: 4-space indentation, type hints on public helpers and service boundaries, and short docstrings on non-trivial functions. Keep domain logic in `app/domain/kv/services`, persistence concerns in `app/domain/kv/repositories`, and FastAPI-specific glue in routers or dependency adapters.

Use `snake_case` for functions, variables, and test names. Keep endpoint paths and environment variables aligned with current names such as `save_string`, `retrieve_string`, `KV_STORE_FILE`, and the versioned `/bigsister/kv/api/v1/...` route family.

## Testing Guidelines

Tests use `pytest` with `fastapi.testclient.TestClient`. Add or update tests for any behavior change in request validation, TTL handling, persistence, or retrieval semantics. Name tests `test_<behavior>`, keep assertions specific, and isolate filesystem effects with temporary paths as the existing suite does.

## Commit & Pull Request Guidelines

Recent commits use short, imperative subjects such as `add CLAUDE.md` and `update gitignore`. Prefer concise commit titles describing the visible change.

Pull requests should explain the behavior change, list test coverage run locally, and link related issues when applicable. Include request/response examples if either the legacy root endpoints or the versioned authenticated routes change.

## Configuration & Operations

Runtime behavior depends on `KV_STORE_FILE`, `KV_LOG_DIR`, `KV_LOG_BACKUP_COUNT`, `KV_HOST`, and `KV_PORT`. Avoid committing local store data, PID files, or generated logs.
