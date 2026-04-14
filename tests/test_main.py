"""Tests for the local KV HTTP service."""

import importlib
import json
import os
import tempfile
import time
from pathlib import Path

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

# Point persistence file to a temp location so tests don't touch real data.
os.environ["KV_STORE_FILE"] = os.path.join(tempfile.gettempdir(), "test_kv_store.json")

from app.api.dependencies import get_current_user  # noqa: E402
from app.core import config as config_module  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.logging import build_logging_config  # noqa: E402
from app.domain.kv.repositories import FileKVRepository, KVRecord  # noqa: E402
from app.domain.kv.services import DEFAULT_TTL_SECONDS  # noqa: E402
from app.main import create_app  # noqa: E402


AUTH_HEADERS = {"Authorization": "Bearer test-token"}
SAVE_PATH = "/bigsister/kv/api/v1/save_string"
RETRIEVE_PATH = "/bigsister/kv/api/v1/retrieve_string"
LEGACY_SAVE_PATH = "/save_string"
LEGACY_RETRIEVE_PATH = "/retrieve_string"
LOG_FILE_PATH = os.path.join(settings.kv_log_dir, "kv_server.log")


@pytest.fixture(autouse=True)
def clear_store():
    """Remove any leftover store file before and after each test."""
    store_file = os.environ["KV_STORE_FILE"]
    if os.path.exists(store_file):
        os.remove(store_file)
    yield
    if os.path.exists(store_file):
        os.remove(store_file)


@pytest.fixture()
def client():
    with TestClient(create_app()) as c:
        yield c


def repo_snapshot(client: TestClient) -> dict[str, dict[str, float | str]]:
    repository = client.app.state.kv_service.repository
    assert isinstance(repository, FileKVRepository)
    return repository.snapshot()


# ---------------------------------------------------------------------------
# save_string
# ---------------------------------------------------------------------------


def test_save_string_returns_ok(client):
    resp = client.post(SAVE_PATH, json={"value": "bar"}, headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert isinstance(data["key"], str)
    assert len(data["key"]) > 0


def test_save_string_stores_value(client):
    resp = client.post(SAVE_PATH, json={"value": "world"}, headers=AUTH_HEADERS)
    key = resp.json()["key"]
    store = repo_snapshot(client)
    assert key in store
    assert store[key]["value"] == "world"


def test_save_string_custom_ttl(client):
    resp = client.post(
        SAVE_PATH,
        json={"value": "v", "ttl_seconds": 3600},
        headers=AUTH_HEADERS,
    )
    key = resp.json()["key"]
    expires_at = repo_snapshot(client)[key]["expires_at"]
    assert abs(expires_at - (time.time() + 3600)) < 2


def test_save_string_default_ttl(client):
    resp = client.post(SAVE_PATH, json={"value": "v"}, headers=AUTH_HEADERS)
    key = resp.json()["key"]
    expires_at = repo_snapshot(client)[key]["expires_at"]
    assert abs(expires_at - (time.time() + DEFAULT_TTL_SECONDS)) < 2


def test_save_string_invalid_ttl(client):
    resp = client.post(
        SAVE_PATH,
        json={"value": "v", "ttl_seconds": 0},
        headers=AUTH_HEADERS,
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "KV_INVALID_TTL"


def test_save_string_requires_auth(client):
    resp = client.post(SAVE_PATH, json={"value": "bar"})
    assert resp.status_code == 401


def test_save_string_generates_unique_keys(client):
    key1 = client.post(SAVE_PATH, json={"value": "a"}, headers=AUTH_HEADERS).json()["key"]
    key2 = client.post(SAVE_PATH, json={"value": "b"}, headers=AUTH_HEADERS).json()["key"]
    assert key1 != key2

    import re

    pattern = re.compile(r"^[A-Za-z0-9_-]{11}$")
    assert pattern.match(key1)
    assert pattern.match(key2)


def test_legacy_save_string_returns_ok_without_auth(client):
    resp = client.post(LEGACY_SAVE_PATH, json={"value": "bar"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert isinstance(data["key"], str)
    assert len(data["key"]) > 0


# ---------------------------------------------------------------------------
# retrieve_string
# ---------------------------------------------------------------------------


def test_retrieve_string_returns_value(client):
    resp = client.post(SAVE_PATH, json={"value": "hello"}, headers=AUTH_HEADERS)
    key = resp.json()["key"]
    resp = client.get(RETRIEVE_PATH, params={"key": key}, headers=AUTH_HEADERS)
    assert resp.status_code == 200
    assert resp.json() == {"key": key, "value": "hello"}


def test_retrieve_string_missing_key_returns_404(client):
    resp = client.get(RETRIEVE_PATH, params={"key": "nonexistent"}, headers=AUTH_HEADERS)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "KV_KEY_NOT_FOUND"


def test_legacy_retrieve_string_returns_value_without_auth(client):
    resp = client.post(LEGACY_SAVE_PATH, json={"value": "hello"})
    key = resp.json()["key"]
    resp = client.get(LEGACY_RETRIEVE_PATH, params={"key": key})
    assert resp.status_code == 200
    assert resp.json() == {"key": key, "value": "hello"}


def test_retrieve_string_expired_key_returns_404(client):
    repository = client.app.state.kv_service.repository
    repository.set("expired_key", KVRecord(value="old", expires_at=time.time() - 1))
    resp = client.get(RETRIEVE_PATH, params={"key": "expired_key"}, headers=AUTH_HEADERS)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "KV_KEY_NOT_FOUND"
    assert "expired_key" not in repo_snapshot(client)


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def test_persistence_survives_reload(client):
    resp = client.post(SAVE_PATH, json={"value": "yes"}, headers=AUTH_HEADERS)
    key = resp.json()["key"]

    with TestClient(create_app()) as restarted_client:
        resp = restarted_client.get(RETRIEVE_PATH, params={"key": key}, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json() == {"key": key, "value": "yes"}


def test_persistence_expired_entries_not_loaded():
    store_file = os.environ["KV_STORE_FILE"]
    expired_data = {"gone": {"value": "x", "expires_at": time.time() - 10}}
    with open(store_file, "w", encoding="utf-8") as fh:
        json.dump(expired_data, fh)

    with TestClient(create_app()) as client:
        repository = client.app.state.kv_service.repository
        assert isinstance(repository, FileKVRepository)
        assert "gone" not in repository.snapshot()


def test_kv_exception_handler_logs_error(client):
    before_size = os.path.getsize(LOG_FILE_PATH) if os.path.exists(LOG_FILE_PATH) else 0
    resp = client.get(RETRIEVE_PATH, params={"key": "missing"}, headers=AUTH_HEADERS)
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as fh:
        fh.seek(before_size)
        log_output = fh.read()

    assert resp.status_code == 404
    assert "KV domain error on GET /bigsister/kv/api/v1/retrieve_string [KV_KEY_NOT_FOUND]" in log_output


def test_uncaught_exception_returns_500_and_logs_traceback():
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: None

    @app.get("/boom")
    async def boom(_: object = Depends(get_current_user)):
        raise RuntimeError("boom")

    before_size = os.path.getsize(LOG_FILE_PATH) if os.path.exists(LOG_FILE_PATH) else 0
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/boom", headers=AUTH_HEADERS)
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as fh:
        fh.seek(before_size)
        log_output = fh.read()

    assert resp.status_code == 500
    assert resp.json() == {
        "detail": "Internal server error",
        "code": "INTERNAL_SERVER_ERROR",
    }
    assert "Unhandled exception on GET /boom" in log_output
    assert "Traceback" in log_output
    assert "RuntimeError: boom" in log_output


def test_kv_log_dir_defaults_to_project_root(monkeypatch):
    monkeypatch.delenv("KV_LOG_DIR", raising=False)
    reloaded_config = importlib.reload(config_module)

    try:
        expected = str(Path(reloaded_config.__file__).resolve().parents[2] / "logs")
        assert reloaded_config.settings.kv_log_dir == expected
    finally:
        importlib.reload(config_module)


def test_kv_log_dir_relative_env_is_resolved_from_project_root(monkeypatch):
    monkeypatch.setenv("KV_LOG_DIR", "runtime_logs")
    reloaded_config = importlib.reload(config_module)

    try:
        expected = str(Path(reloaded_config.__file__).resolve().parents[2] / "runtime_logs")
        assert reloaded_config.settings.kv_log_dir == expected
    finally:
        monkeypatch.delenv("KV_LOG_DIR", raising=False)
        importlib.reload(config_module)


def test_logging_config_wires_daily_rotation_for_app_and_uvicorn():
    config = build_logging_config()

    assert config["disable_existing_loggers"] is False
    assert config["handlers"]["console"]["class"] == "logging.StreamHandler"
    assert config["handlers"]["file_daily"]["class"] == "logging.handlers.TimedRotatingFileHandler"
    assert config["handlers"]["file_daily"]["when"] == "midnight"
    assert config["handlers"]["file_daily"]["interval"] == 1
    assert config["handlers"]["file_daily"]["backupCount"] == 30
    assert config["root"]["handlers"] == ["console", "file_daily"]
    assert config["root"]["level"] == "INFO"

    for logger_name in ("app", "uvicorn", "uvicorn.error", "uvicorn.access"):
        assert config["loggers"][logger_name]["level"] == "INFO"
        assert config["loggers"][logger_name]["propagate"] is True
