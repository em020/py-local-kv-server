"""Tests for the local KV HTTP service."""

import json
import os
import tempfile
import time

import pytest
from fastapi.testclient import TestClient

# Point persistence file to a temp location so tests don't touch real data
os.environ["KV_STORE_FILE"] = os.path.join(tempfile.gettempdir(), "test_kv_store.json")

from main import DEFAULT_TTL_SECONDS, _store, app  # noqa: E402


@pytest.fixture(autouse=True)
def clear_store(tmp_path):
    """Reset in-memory store and remove any leftover store file before each test."""
    _store.clear()
    store_file = os.environ["KV_STORE_FILE"]
    if os.path.exists(store_file):
        os.remove(store_file)
    yield
    _store.clear()
    if os.path.exists(store_file):
        os.remove(store_file)


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# save_string
# ---------------------------------------------------------------------------


def test_save_string_returns_ok(client):
    resp = client.post("/save_string", json={"value": "bar"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert isinstance(data["key"], str)
    assert len(data["key"]) > 0


def test_save_string_stores_value(client):
    resp = client.post("/save_string", json={"value": "world"})
    key = resp.json()["key"]
    assert key in _store
    assert _store[key]["value"] == "world"


def test_save_string_custom_ttl(client):
    resp = client.post("/save_string", json={"value": "v", "ttl_seconds": 3600})
    key = resp.json()["key"]
    expires_at = _store[key]["expires_at"]
    assert abs(expires_at - (time.time() + 3600)) < 2


def test_save_string_default_ttl(client):
    resp = client.post("/save_string", json={"value": "v"})
    key = resp.json()["key"]
    expires_at = _store[key]["expires_at"]
    assert abs(expires_at - (time.time() + DEFAULT_TTL_SECONDS)) < 2


def test_save_string_invalid_ttl(client):
    resp = client.post("/save_string", json={"value": "v", "ttl_seconds": 0})
    assert resp.status_code == 400


def test_save_string_generates_unique_keys(client):
    key1 = client.post("/save_string", json={"value": "a"}).json()["key"]
    key2 = client.post("/save_string", json={"value": "b"}).json()["key"]
    assert key1 != key2
    # token_urlsafe(8) produces 11 URL-safe base64 characters
    import re
    pattern = re.compile(r'^[A-Za-z0-9_-]{11}$')
    assert pattern.match(key1)
    assert pattern.match(key2)


# ---------------------------------------------------------------------------
# retrieve_string
# ---------------------------------------------------------------------------


def test_retrieve_string_returns_value(client):
    resp = client.post("/save_string", json={"value": "hello"})
    key = resp.json()["key"]
    resp = client.get("/retrieve_string", params={"key": key})
    assert resp.status_code == 200
    assert resp.json() == {"key": key, "value": "hello"}


def test_retrieve_string_missing_key_returns_404(client):
    resp = client.get("/retrieve_string", params={"key": "nonexistent"})
    assert resp.status_code == 404


def test_retrieve_string_expired_key_returns_404(client):
    """An entry whose TTL has already elapsed should not be returned."""
    _store["expired_key"] = {"value": "old", "expires_at": time.time() - 1}
    resp = client.get("/retrieve_string", params={"key": "expired_key"})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def test_persistence_survives_reload(client):
    """Saving a key and then re-loading the store file should restore the value."""
    resp = client.post("/save_string", json={"value": "yes"})
    key = resp.json()["key"]

    # Simulate a restart by clearing memory and re-loading from disk
    _store.clear()
    from main import _load_store

    _load_store()

    assert key in _store
    assert _store[key]["value"] == "yes"


def test_persistence_expired_entries_not_loaded():
    """Expired entries written to disk should NOT be loaded on restart."""
    store_file = os.environ["KV_STORE_FILE"]
    expired_data = {
        "gone": {"value": "x", "expires_at": time.time() - 10}
    }
    with open(store_file, "w") as fh:
        json.dump(expired_data, fh)

    _store.clear()
    from main import _load_store

    _load_store()
    assert "gone" not in _store
