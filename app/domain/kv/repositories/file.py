import json
import logging
import os
import threading
import time
from dataclasses import asdict

from app.domain.kv.repositories.base import KVRecord, KVRepository

logger = logging.getLogger(__name__)


class FileKVRepository(KVRepository):
    def __init__(self, store_file: str):
        self.store_file = store_file
        self._store: dict[str, KVRecord] = {}
        self._lock = threading.Lock()

    def load(self) -> None:
        if not os.path.exists(self.store_file):
            return
        try:
            with open(self.store_file, "r", encoding="utf-8") as fh:
                data: dict[str, dict] = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not load KV store from %s: %s", self.store_file, exc)
            return

        now = time.time()
        loaded: dict[str, KVRecord] = {}
        for key, entry in data.items():
            expires_at = entry.get("expires_at", 0)
            if expires_at > now:
                loaded[key] = KVRecord(value=entry["value"], expires_at=expires_at)

        with self._lock:
            self._store = loaded

    def get(self, key: str) -> KVRecord | None:
        with self._lock:
            return self._store.get(key)

    def set(self, key: str, record: KVRecord) -> None:
        with self._lock:
            self._store[key] = record
            self._save_locked()

    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._store:
                del self._store[key]
                self._save_locked()

    def exists(self, key: str) -> bool:
        with self._lock:
            return key in self._store

    def evict_expired(self) -> None:
        now = time.time()
        with self._lock:
            expired_keys = [key for key, value in self._store.items() if value.expires_at <= now]
            if not expired_keys:
                return
            for key in expired_keys:
                del self._store[key]
            self._save_locked()

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def snapshot(self) -> dict[str, dict[str, float | str]]:
        with self._lock:
            return {key: asdict(value) for key, value in self._store.items()}

    def _save_locked(self) -> None:
        tmp_path = self.store_file + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump({key: asdict(value) for key, value in self._store.items()}, fh)
        os.replace(tmp_path, self.store_file)
