from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class KVRecord:
    value: str
    expires_at: float


class KVRepository(ABC):
    @abstractmethod
    def load(self) -> None:
        """Load persisted state into memory."""

    @abstractmethod
    def get(self, key: str) -> KVRecord | None:
        """Return the record for *key* if it exists."""

    @abstractmethod
    def set(self, key: str, record: KVRecord) -> None:
        """Store or replace a record and persist it."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a record if present and persist it."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Return whether a key currently exists."""

    @abstractmethod
    def evict_expired(self) -> None:
        """Remove expired entries and persist if changes were made."""
