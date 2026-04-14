import os
from logging.config import dictConfig

from app.core.config import settings


def build_logging_config() -> dict:
    log_file_path = os.path.join(settings.kv_log_dir, "kv_server.log")

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file_daily": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "standard",
                "filename": log_file_path,
                "when": "midnight",
                "interval": 1,
                "backupCount": settings.kv_log_backup_count,
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file_daily"],
        },
        "loggers": {
            "app": {
                "level": "INFO",
                "propagate": True,
            },
            "uvicorn": {
                "level": "INFO",
                "propagate": True,
            },
            "uvicorn.error": {
                "level": "INFO",
                "propagate": True,
            },
            "uvicorn.access": {
                "level": "INFO",
                "propagate": True,
            },
        },
    }


def setup_logging() -> None:
    """Configure application and Uvicorn logging before app startup."""
    os.makedirs(settings.kv_log_dir, exist_ok=True)
    dictConfig(build_logging_config())
