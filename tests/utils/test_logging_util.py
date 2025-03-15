import json
import os
import pytest
import logging
from src.utils.logging_util import setup_logger
from src.utils.config_util import ConfigUtil

@pytest.fixture
def mock_config_util(tmp_path):
    """
    Provide a temporary configuration for testing logging utility.
    """
    config = {
        "logging": {
            "log_dir": str(tmp_path / "logs"),
            "log_file_name": "test_app.log",
            "max_file_size": 1000,
            "backup_count": 1,
            "log_level_console": "DEBUG",
            "log_level_file": "INFO",
            "log_format": "%(asctime)s - %(levelname)s - %(message)s"
        }
    }
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
    ConfigUtil(
        main_config=config_path)  # Initialize ConfigUtil with temp config
    return ConfigUtil()


@pytest.fixture
def valid_log_dir(tmp_path):
    """
    Fixture to provide a temporary log directory for testing.
    """
    return tmp_path / "logs"


def test_setup_logger_creates_handlers(mock_config_util):
    """
    Test that `setup_logger` creates a logger with the appropriate handlers.
    """
    logger = setup_logger("test_logger")
    handlers = logger.handlers

    # Assert correct handlers are attached
    assert any(isinstance(h, logging.StreamHandler) for h in
               handlers), "StreamHandler not attached!"
    assert any(
        isinstance(h, logging.handlers.RotatingFileHandler) for h in
        handlers), "RotatingFileHandler not attached!"



def test_logging_to_file(mock_config_util):
    """
    Test that log messages are written to the correct log file.
    """
    logger = setup_logger("file_logger")
    test_message = "This is a test log message."

    # Log the message
    logger.info(test_message)

    log_file_path = mock_config_util.get("logging.log_dir") + "/test_app.log"
    assert os.path.exists(log_file_path), "Log file was not created."

    with open(log_file_path, "r") as f:
        log_content = f.read()
    assert test_message in log_content, "Log message not found in the log file."



def test_log_rotation(valid_log_dir):
    """
    Test that log files are rotated when the size limit is exceeded.
    """
    # Prepare a mock config for small log size to trigger rotation
    ConfigUtil._config = {
        "logging": {
            "log_dir": str(valid_log_dir),
            "log_file_name": "rotation_test.log",
            "max_file_size": 100,
            "backup_count": 2,
            "log_level_console": "DEBUG",
            "log_level_file": "INFO",
            "log_format": "%(asctime)s - %(message)s",
        },
        "meta": {}
    }

    logger = setup_logger("rotation_logger")

    # Write enough log messages to exceed the file size limit and trigger rotation
    for i in range(50):
        logger.info(f"Log message {i}")

    log_file_path = os.path.join(valid_log_dir, "rotation_test.log")
    rotated_file = os.path.join(valid_log_dir, "rotation_test.log.1")

    # Verify rotation
    assert os.path.exists(log_file_path), "Main log file does not exist."
    assert os.path.exists(rotated_file), "Rotated log file .1 was not created."
