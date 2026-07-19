"""Configuration centralisée du logging."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import config
from utils.resource_path import user_data_dir


def setup_logging() -> None:
    """Configure le logging applicatif (fichier tournant + écho console en debug)."""
    log_dir = user_data_dir() / config.LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{config.APP_NAME.lower()}.log"

    level = logging.DEBUG if _debug_enabled() else getattr(logging, config.LOG_LEVEL, logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(file_handler)

    if _debug_enabled() and sys.stderr is not None:
        console = logging.StreamHandler(sys.stderr)
        console.setFormatter(formatter)
        console.setLevel(logging.DEBUG)
        root.addHandler(console)


def _debug_enabled() -> bool:
    """Vrai si la variable d'environnement MDREADER_DEBUG vaut 1."""
    return os.environ.get(f"{config.APP_NAME.upper()}_DEBUG") == "1"
