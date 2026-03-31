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
    resp = client.post("/save_string", json={"key": "foo", "value": "bar"})
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_save_string_stores_value(client):
    client.post("/save_string", json={"key": "hello", "value": "world"})
    assert "hello" in _store
    assert _store["hello"]["value"] == "world"


def test_save_string_custom_ttl(client):
    client.post("/save_string", json={"key": "k", "value": "v", "ttl_seconds": 3600})
    expires_at = _store["k"]["expires_at"]
    assert abs(expires_at - (time.time() + 3600)) < 2


def test_save_string_default_ttl(client):
    client.post("/save_string", json={"key": "k", "value": "v"})
    expires_at = _store["k"]["expires_at"]
    assert abs(expires_at - (time.time() + DEFAULT_TTL_SECONDS)) < 2


def test_save_string_invalid_ttl(client):
    resp = client.post("/save_string", json={"key": "k", "value": "v", "ttl_seconds": 0})
    assert resp.status_code == 400


def test_save_string_overwrites_existing_key(client):
    client.post("/save_string", json={"key": "dup", "value": "first"})
    client.post("/save_string", json={"key": "dup", "value": "second"})
    assert _store["dup"]["value"] == "second"


# ---------------------------------------------------------------------------
# retrieve_string
# ---------------------------------------------------------------------------


def test_retrieve_string_returns_value(client):
    client.post("/save_string", json={"key": "msg", "value": "hello"})
    resp = client.get("/retrieve_string", params={"key": "msg"})
    assert resp.status_code == 200
    assert resp.json() == {"key": "msg", "value": "hello"}


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
    client.post("/save_string", json={"key": "persist", "value": "yes"})

    # Simulate a restart by clearing memory and re-loading from disk
    _store.clear()
    from main import _load_store

    _load_store()

    assert "persist" in _store
    assert _store["persist"]["value"] == "yes"


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
