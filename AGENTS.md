# Repository Guidelines

## Project Structure & Module Organization

This repository is intentionally small. [`main.py`](/Users/yiminsun/projects/py-local-kv-server/main.py) contains the FastAPI app, request/response models, in-memory store, persistence helpers, and logging setup. [`tests/test_main.py`](/Users/yiminsun/projects/py-local-kv-server/tests/test_main.py) covers API behavior and persistence. [`start.sh`](/Users/yiminsun/projects/py-local-kv-server/start.sh) launches the server in the background, and [`README.md`](/Users/yiminsun/projects/py-local-kv-server/README.md) documents runtime usage. Refer to [`CLAUDE.md`](/Users/yiminsun/projects/py-local-kv-server/CLAUDE.md) for the current architecture overview and core implementation notes.

## Build, Test, and Development Commands

Install runtime dependencies with `pip install -r requirements.txt`.

Run the server in the foreground with `uvicorn main:app --host 127.0.0.1 --port 8000`.

Use `./start.sh` for the idempotent background launcher. Example: `./start.sh --host 0.0.0.0 --port 9000`. Use `./restart.sh` to stop the PID-managed instance and start it again with the same optional flags.

Install test-only dependencies with `pip install pytest httpx`, then run `pytest tests/`. For a focused check, use `pytest tests/test_main.py::test_save_string_returns_ok`.

## Coding Style & Naming Conventions

Follow the existing Python style in `main.py`: 4-space indentation, type hints on module-level constants and public helpers, and short docstrings on non-trivial functions. Keep the service simple and local; avoid splitting files unless the single-module layout becomes a clear maintenance problem.

Use `snake_case` for functions, variables, and test names. Keep endpoint paths and environment variables aligned with current names such as `save_string`, `retrieve_string`, and `KV_STORE_FILE`.

## Testing Guidelines

Tests use `pytest` with `fastapi.testclient.TestClient`. Add or update tests for any behavior change in request validation, TTL handling, persistence, or retrieval semantics. Name tests `test_<behavior>`, keep assertions specific, and isolate filesystem effects with temporary paths as the existing suite does.

## Commit & Pull Request Guidelines

Recent commits use short, imperative subjects such as `add CLAUDE.md` and `update gitignore`. Prefer concise commit titles describing the visible change.

Pull requests should explain the behavior change, list test coverage run locally, and link related issues when applicable. Include request/response examples if an API contract changes.

## Configuration & Operations

Runtime behavior depends on `KV_STORE_FILE`, `KV_LOG_DIR`, `KV_LOG_BACKUP_COUNT`, `KV_HOST`, and `KV_PORT`. Avoid committing local store data, PID files, or generated logs.
