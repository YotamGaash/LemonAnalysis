import os
import logging
from src.utils.logging_util import setup_logger


def close_logger_handlers(logger_name):
    """
    Helper function to close and remove handlers from a logger to prevent locking issues.
    """
    logger = logging.getLogger(logger_name)
    while logger.handlers:
        handler = logger.handlers[0]
        handler.close()
        logger.removeHandler(handler)


def test_setup_logger_creates_logger():
    """
    Test that `setup_logger` creates a valid logger instance.
    """
    logger_name = "test_logger"
    logger = setup_logger(logger_name)
    handlers = logger.handlers
    print(f"Logger handlers: {handlers}")
    # Ensure both StreamHandler and RotatingFileHandler are attached
    assert any(isinstance(h, logging.StreamHandler) for h in handlers), "StreamHandler not attached!"
    assert any(
        isinstance(h, logging.handlers.RotatingFileHandler) for h in handlers), "RotatingFileHandler not attached!"
    close_logger_handlers(logger_name)


def test_logger_logs_to_file():
    """
    Test that logs are written to the default `logs/app.log` file.
    """
    # Default log file path
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
    log_file = os.path.join(log_dir, "app.log")

    # Ensure the logs directory is clean for testing
    if os.path.exists(log_file):
        os.remove(log_file)

    logger_name = "test_file_logger"
    logger = setup_logger(logger_name, file_level=logging.INFO)

    test_message = "Test file log message"
    # Log a message
    logger.info(test_message)

    # Debugging: Verify log directory and file creation
    print(f"Log directory exists: {os.path.exists(log_dir)}, Log file exists: {os.path.exists(log_file)}")

    # Verify the log file is created
    assert os.path.exists(log_file), "Log file was not created in the expected location."

    # Check that the file contains the log message
    with open(log_file, "r") as f:
        log_content = f.read()
    assert test_message in log_content, "Log message not found in the log file!"

    # Cleanup logger and file
    close_logger_handlers(logger_name)


def test_logger_creates_logs_directory():
    """
    Test that the `logs/` directory is automatically created if it doesn't exist.
    """
    # Default logs directory
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))

    # Ensure the logs directory is clean for testing
    if os.path.exists(log_dir):
        for file in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file)
            os.remove(file_path)
        os.rmdir(log_dir)

    # Ensure directory doesn't exist before logger initialization
    assert not os.path.exists(log_dir)

    # Initialize logger
    logger_name = "test_dir_creation_logger"
    logger = setup_logger(logger_name)
    print(f"Logger initialized for directory creation test at {log_dir}")
    handlers = logger.handlers

    # Ensure handlers are attached
    assert len(handlers) > 0, "Logger handlers are not attached!"
    # Verify the logs directory was created
    assert os.path.exists(log_dir), "Logs directory was not created!"

    # Cleanup logger
    close_logger_handlers(logger_name)


def test_log_rotation():
    """
    Test that `setup_logger` correctly rotates log files when the size limit is reached.
    """
    # Default logs directory
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
    log_file = os.path.join(log_dir, "app.log")

    # Ensure the logs directory and log file are clean
    if os.path.exists(log_file):
        os.remove(log_file)

    logger_name = "test_rotation_logger"
    logger = setup_logger(logger_name, file_level=logging.INFO)
    test_message = "Rotating log message"

    # Log enough data to trigger rotation (5MB limit in logging_util.py)
    for i in range(10000):  # Write enough logs to exceed 5MB
        logger.info(f"{test_message} {i}")

    # Debugging: Verify log rotation
    print(f"Log file exists: {os.path.exists(log_file)}, Backup file exists: {os.path.exists(f'{log_file}.1')}")
    print(f"Backup file 1 exists: {os.path.exists(f'{log_file}.1')}")
    print(f"Backup file 2 exists: {os.path.exists(f'{log_file}.2')}")

    # Check the main log file and backup file rotation
    assert os.path.exists(log_file), "Main log file does not exist after logging messages."
    assert os.path.exists(f"{log_file}.1"), "Rotated log file (.1) was not created."
    assert os.path.exists(f"{log_file}.2"), "Rotated log file (.2) was not created."

    # Cleanup logger
    close_logger_handlers(logger_name)
