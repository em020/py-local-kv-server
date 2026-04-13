import secrets
import time

from app.domain.kv.exceptions import (
    KVInvalidTTLError,
    KVKeyGenerationError,
    KVKeyNotFoundError,
)
from app.domain.kv.repositories import KVRecord, KVRepository
from app.domain.kv.schemas import RetrieveResponse, SaveResponse


DEFAULT_TTL_SECONDS: int = 4 * 60 * 60


class KVService:
    def __init__(self, repository: KVRepository):
        self.repository = repository

    def load(self) -> None:
        self.repository.load()

    def save_string(self, value: str, ttl_seconds: int | None = None) -> SaveResponse:
        ttl = ttl_seconds if ttl_seconds is not None else DEFAULT_TTL_SECONDS
        if ttl <= 0:
            raise KVInvalidTTLError()

        self.repository.evict_expired()
        key = self._generate_unique_key()
        self.repository.set(
            key,
            KVRecord(value=value, expires_at=time.time() + ttl),
        )
        return SaveResponse(key=key, status="ok")

    def retrieve_string(self, key: str) -> RetrieveResponse:
        record = self.repository.get(key)
        if record is None:
            raise KVKeyNotFoundError(key)
        if record.expires_at <= time.time():
            self.repository.delete(key)
            raise KVKeyNotFoundError(key)
        return RetrieveResponse(key=key, value=record.value)

    def _generate_unique_key(self) -> str:
        for _ in range(10):
            key = secrets.token_urlsafe(8)
            if not self.repository.exists(key):
                return key
        raise KVKeyGenerationError()
