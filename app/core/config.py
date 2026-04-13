from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_title: str = "Big Sister"
    kv_store_file: str = os.environ.get("KV_STORE_FILE", "kv_store.json")
    kv_log_dir: str = os.environ.get("KV_LOG_DIR", "logs")
    kv_log_backup_count: int = int(os.environ.get("KV_LOG_BACKUP_COUNT", "30"))


settings = Settings()
