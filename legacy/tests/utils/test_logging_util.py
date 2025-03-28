import json
import pytest
import logging
import logging.handlers
from pathlib import Path
from legacy.src.utils.logging_util import setup_logger
from legacy.src.utils.config_util import ConfigUtil


@pytest.fixture
def config_with_logging(tmp_path):
    """Create a configuration with logging settings"""
    config = {
        "logging": {
            "log_dir": str(tmp_path / "logs"),
            "log_file_name": "test.log",
            "max_file_size": 1024,
            "backup_count": 3,
            "log_level_console": "DEBUG",
            "log_level_file": "INFO",
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    config_file = tmp_path / "app_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

    return ConfigUtil(main_config=str(config_file))


@pytest.fixture
def cleanup_loggers():
    """Clean up loggers after each test"""
    yield
    # Remove all handlers from the root logger
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    # Clear any loggers we created
    logging.Logger.manager.loggerDict.clear()


@pytest.fixture(autouse=True)
def setup_and_teardown(cleanup_loggers):
    """Automatically use cleanup"""
    yield


def test_logger_creation_with_valid_config(config_with_logging):
    """Test basic logger creation with valid configuration"""
    logger = setup_logger("test_logger")

    assert logger.name == "test_logger"
    assert len(logger.handlers) == 2  # Console and File handlers
    assert logger.level == logging.DEBUG  # Default level


def test_console_handler_configuration(config_with_logging):
    """Test console handler is properly configured"""
    logger = setup_logger("console_test")
    console_handler = next(h for h in logger.handlers
                           if isinstance(h, logging.StreamHandler)
                           and not isinstance(h, logging.FileHandler))

    assert console_handler.level == logging.DEBUG
    assert isinstance(console_handler.formatter, logging.Formatter)


def test_file_handler_configuration(config_with_logging):
    """Test file handler is properly configured"""
    logger = setup_logger("file_test")
    file_handler = next(h for h in logger.handlers
                        if isinstance(h, logging.handlers.RotatingFileHandler))

    assert file_handler.level == logging.INFO
    assert isinstance(file_handler.formatter, logging.Formatter)
    assert file_handler.maxBytes == 1024
    assert file_handler.backupCount == 3


def test_log_directory_creation(config_with_logging):
    """Test log directory is created if it doesn't exist"""
    logger = setup_logger("dir_test")
    log_dir = Path(config_with_logging.get("logging.log_dir"))

    assert log_dir.exists()
    assert log_dir.is_dir()


def test_log_file_creation(config_with_logging):
    """Test log file is created and writable"""
    logger = setup_logger("file_creation_test")
    log_path = Path(config_with_logging.get("logging.log_dir")) / "test.log"

    logger.info("Test message")

    assert log_path.exists()
    assert log_path.is_file()
    with open(log_path, 'r') as f:
        assert "Test message" in f.read()


def test_log_rotation(config_with_logging):
    """Test log rotation functionality"""
    logger = setup_logger("rotation_test")
    log_dir = Path(config_with_logging.get("logging.log_dir"))
    log_file = log_dir / "test.log"

    # Write enough data to trigger rotation
    large_message = "x" * 512 + "\n"
    for _ in range(3):
        logger.info(large_message)

    # Check for rotated files
    assert log_file.exists()
    assert (log_dir / "test.log.1").exists()


def test_multiple_loggers_same_name(config_with_logging):
    """Test that getting loggers with the same name returns the same instance"""
    logger1 = setup_logger("same_name")
    logger2 = setup_logger("same_name")

    assert logger1 is logger2
    assert len(logger1.handlers) == 2  # Shouldn't duplicate handlers

# def test_invalid_log_levels(tmp_path):
#     """Test logger setup with invalid log levels"""
#     with patch('src.utils.logging_util.ConfigUtil') as mock_config:
#         instance = mock_config.return_value
#         config_data = {
#             "logging.log_dir": str(tmp_path),
#             "logging.log_file_name": "test.log",
#             "logging.log_level_console": "INVALID_LEVEL",
#             "logging.log_level_file": "DEBUG",
#             "logging.max_file_size": 1024,
#             "logging.backup_count": 1
#         }
#
#         def mock_get(key, default=None):
#             return config_data.get(key, default)
#
#         instance.get.side_effect = mock_get
#
#         logger = setup_logger("invalid_level_test")
#
#         # Verify logger was created with default level
#         assert logger.getEffectiveLevel() == logging.INFO
#
#         # Verify handlers
#         console_handler = next(
#             (h for h in logger.handlers
#              if isinstance(h, logging.StreamHandler)
#              and not isinstance(h, logging.handlers.RotatingFileHandler)),
#             None
#         )
#         file_handler = next(
#             (h for h in logger.handlers
#              if isinstance(h, logging.handlers.RotatingFileHandler)),
#             None
#         )
#
#         assert console_handler is not None
#         assert console_handler.level == logging.DEBUG
#         assert file_handler is not None
#         assert file_handler.level == logging.INFO
#


def test_formatter_configuration(config_with_logging):
    """Test log formatter configuration"""
    logger = setup_logger("formatter_test")
    test_message = "Test formatting"

    # Log a message and check the format
    logger.info(test_message)

    log_file = Path(config_with_logging.get("logging.log_dir")) / "test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "formatter_test" in log_content
        assert "INFO" in log_content
        assert test_message in log_content


@pytest.mark.parametrize("log_level", [
    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
])
def test_different_log_levels(config_with_logging, log_level):
    """Test logging at different levels"""
    logger = setup_logger("level_test")
    log_method = getattr(logger, log_level.lower())
    test_message = f"Test {log_level}"

    log_method(test_message)

    log_file = Path(config_with_logging.get("logging.log_dir")) / "test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        if log_level in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
            assert test_message in log_content
        elif log_level == "DEBUG":
            # DEBUG messages might not appear in file due to INFO level
            pass


def test_exception_logging(config_with_logging):
    """Test logging of exceptions"""
    logger = setup_logger("exception_test")

    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.exception("An error occurred")

    log_file = Path(config_with_logging.get("logging.log_dir")) / "test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "An error occurred" in log_content
        assert "ValueError: Test exception" in log_content
        assert "Traceback" in log_content
