"""Configure application logging and error tracking."""

import logging
from pathlib import Path

from config import LOG_FILE_PATH, LOG_LEVEL


def setup_logger(
    logger_name: str = "resume_screening",
    log_file_path: str = LOG_FILE_PATH,
    log_level: str = LOG_LEVEL,
) -> logging.Logger:
    """Create and configure the application logger."""

    logger = logging.getLogger(logger_name)

    numeric_log_level = getattr(
        logging,
        str(log_level).upper(),
        logging.INFO,
    )

    logger.setLevel(numeric_log_level)
    logger.propagate = False

    log_file = Path(log_file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    resolved_log_path = str(log_file.resolve())

    existing_file_handler = any(
        isinstance(handler, logging.FileHandler)
        and handler.baseFilename == resolved_log_path
        for handler in logger.handlers
    )

    if not existing_file_handler:
        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8",
        )

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_exception(
    logger: logging.Logger,
    message: str,
) -> None:
    """Record an exception with its traceback."""

    logger.exception(message)