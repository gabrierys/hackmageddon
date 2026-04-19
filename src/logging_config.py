from __future__ import annotations

import logging
from pathlib import Path

from .config import LOG_FILE_PATH, ensure_project_dirs


_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    ensure_project_dirs()
    log_file = Path(LOG_FILE_PATH)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    formatter = logging.Formatter(_FORMAT)
    has_stream = any(getattr(handler, "_hm_stream_handler", False) for handler in root_logger.handlers)
    has_file = any(getattr(handler, "_hm_file_handler", False) for handler in root_logger.handlers)

    if not has_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler._hm_stream_handler = True  # type: ignore[attr-defined]
        root_logger.addHandler(stream_handler)

    if not has_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler._hm_file_handler = True  # type: ignore[attr-defined]
        root_logger.addHandler(file_handler)
