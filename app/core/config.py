import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_from_project_root(raw_path: str, default_name: str) -> str:
    candidate = Path(raw_path) if raw_path else PROJECT_ROOT / default_name
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    return str(candidate)


@dataclass(frozen=True)
class Settings:
    app_title: str = "Big Sister"
    kv_store_file: str = os.environ.get("KV_STORE_FILE", "kv_store.json")
    kv_log_dir: str = _resolve_from_project_root(os.environ.get("KV_LOG_DIR", ""), "logs")
    kv_log_backup_count: int = int(os.environ.get("KV_LOG_BACKUP_COUNT", "30"))


settings = Settings()
