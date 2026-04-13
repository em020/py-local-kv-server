import logging
import logging.handlers
import os

from app.core.config import settings

LOG_FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")


def setup_logging() -> None:
    """Attach a daily rotating file handler to the root logger once."""
    os.makedirs(settings.kv_log_dir, exist_ok=True)
    log_path = os.path.join(settings.kv_log_dir, "kv_server.log")
    root = logging.getLogger()

    if any(
        isinstance(handler, logging.handlers.TimedRotatingFileHandler)
        and getattr(handler, "baseFilename", None) == os.path.abspath(log_path)
        for handler in root.handlers
    ):
        return

    handler = logging.handlers.TimedRotatingFileHandler(
        log_path,
        when="midnight",
        interval=1,
        backupCount=settings.kv_log_backup_count,
        encoding="utf-8",
        utc=False,
    )
    handler.suffix = "%Y-%m-%d"
    handler.setFormatter(LOG_FORMATTER)
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def apply_timestamp_formatter_to_uvicorn() -> None:
    """Apply the shared formatter to uvicorn's handlers after startup."""
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        for handler in logging.getLogger(name).handlers:
            handler.setFormatter(LOG_FORMATTER)
