"""Tests for the application logging module."""

import logging

from modules.logger import log_exception, setup_logger


def test_setup_logger_creates_log_file(tmp_path):
    """Logger setup must create the log file."""

    log_file = tmp_path / "test.log"

    logger = setup_logger(
        logger_name="test_file_creation",
        log_file_path=str(log_file),
    )

    logger.info("Test message")

    for handler in logger.handlers:
        handler.flush()

    assert log_file.exists()


def test_logger_writes_message(tmp_path):
    """Log messages must be written to the file."""

    log_file = tmp_path / "test.log"

    logger = setup_logger(
        logger_name="test_message_writing",
        log_file_path=str(log_file),
    )

    logger.info("Candidate processed successfully")

    for handler in logger.handlers:
        handler.flush()

    content = log_file.read_text(encoding="utf-8")

    assert "Candidate processed successfully" in content
    assert "INFO" in content


def test_log_directory_created(tmp_path):
    """A missing log directory must be created automatically."""

    log_file = tmp_path / "new_logs" / "test.log"

    setup_logger(
        logger_name="test_directory_creation",
        log_file_path=str(log_file),
    )

    assert log_file.parent.exists()


def test_duplicate_handler_prevention(tmp_path):
    """Repeated setup must not add duplicate file handlers."""

    log_file = tmp_path / "test.log"

    logger = setup_logger(
        logger_name="test_duplicate_handlers",
        log_file_path=str(log_file),
    )

    setup_logger(
        logger_name="test_duplicate_handlers",
        log_file_path=str(log_file),
    )

    file_handlers = [
        handler
        for handler in logger.handlers
        if isinstance(handler, logging.FileHandler)
    ]

    assert len(file_handlers) == 1


def test_invalid_log_level_defaults_to_info(tmp_path):
    """An invalid log level must safely default to INFO."""

    log_file = tmp_path / "test.log"

    logger = setup_logger(
        logger_name="test_invalid_level",
        log_file_path=str(log_file),
        log_level="INVALID",
    )

    assert logger.level == logging.INFO


def test_exception_logging(tmp_path):
    """Exceptions and tracebacks must be written to the log file."""

    log_file = tmp_path / "test.log"

    logger = setup_logger(
        logger_name="test_exception",
        log_file_path=str(log_file),
    )

    try:
        raise ValueError("Sample failure")
    except ValueError:
        log_exception(logger, "Candidate processing failed")

    for handler in logger.handlers:
        handler.flush()

    content = log_file.read_text(encoding="utf-8")

    assert "Candidate processing failed" in content
    assert "ValueError: Sample failure" in content