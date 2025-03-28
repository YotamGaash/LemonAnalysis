import logging
import os
import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch
import tempfile
import colorama

from src.core.log_manager import LogManager, ColoredFormatter
from src.core.constants import LOG_LEVELS, DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging state before and after each test"""
    # Clear existing handlers and loggers
    root = logging.getLogger()
    for handler in root.handlers[:]:
        handler.close()
        root.removeHandler(handler)
    logging.Logger.manager.loggerDict.clear()

    # Reset LogManager singleton state
    LogManager._instance = None
    LogManager._initialized = False

    yield

    # Cleanup after test
    for handler in root.handlers[:]:
        handler.close()
        root.removeHandler(handler)
    logging.Logger.manager.loggerDict.clear()
    LogManager._instance = None
    LogManager._initialized = False



@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Clean up handlers before removing directory
    logging.shutdown()
    try:
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.chmod(os.path.join(root, name), 0o777)
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir)
    except (OSError, IOError):
        pass


@pytest.fixture
def mock_config():
    """Create a mock configuration with default settings"""
    config = Mock()
    config.get.side_effect = lambda key, default=None: {
        "logging.enabled": True,
        "logging.console.enabled": True,
        "logging.file.enabled": True,
        "logging.format": DEFAULT_LOG_FORMAT,
        "logging.date_format": DEFAULT_DATE_FORMAT,
        "logging.console.level": "DEBUG",
        "logging.file.level": "INFO",
        "logging.console.use_colors": True,
        "logging.errors.include_traceback": True,
        "logging.errors.traceback_level": "DEBUG",
        "logging.log_dir": "logs",
        "logging.log_file_name": "app.log",
        "logging.max_file_size": 5 * 1024 * 1024,  # 5MB
        "logging.backup_count": 3,
        "logging.encoding": "utf-8"
    }.get(key, default)
    return config


class TestColoredFormatter:
    """Tests for the ColoredFormatter class"""

    def test_format_normal_message(self):
        """Test basic message formatting with colors"""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )

        formatted = formatter.format(record)
        expected = f"{colorama.Fore.GREEN}INFO{colorama.Style.RESET_ALL}: Test message"
        assert formatted == expected

    def test_format_with_exception(self):
        """Test formatting messages that include exceptions"""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        try:
            raise ValueError("test error")
        except ValueError:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="An error occurred",
                args=(),
                exc_info=sys.exc_info()
            )

        formatted = formatter.format(record)
        assert "An error occurred" in formatted
        assert "ValueError: test error" in formatted


class TestLogManager:
    """Tests for the LogManager class"""

    def test_singleton_pattern(self):
        """Verify that LogManager implements the singleton pattern"""
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            "logging.enabled": True,
            "logging.format": "%(levelname)s: %(message)s",  # Provide a valid format string
            "logging.date_format": "%Y-%m-%d %H:%M:%S",
            "logging.console.enabled": True,
            "logging.file.enabled": False
        }.get(key, default)

        with patch('src.core.log_manager.Config', return_value=mock_config):
            manager1 = LogManager()
            manager2 = LogManager()
            assert manager1 is manager2

    def test_logger_creation(self, mock_config):
        """Test creation and retrieval of loggers"""
        with patch('src.core.log_manager.Config', return_value=mock_config):
            manager = LogManager()
            logger1 = manager.get_logger("test1")
            logger2 = manager.get_logger("test2")
            logger1_again = manager.get_logger("test1")

            assert isinstance(logger1, logging.Logger)
            assert logger1 is not logger2
            assert logger1 is logger1_again
            assert logger1.name == "test1"

    def test_console_handler_configuration(self, mock_config):
        """Test console handler setup"""
        with patch('src.core.log_manager.Config', return_value=mock_config):
            manager = LogManager()
            logger = manager.get_logger("test_console")

            console_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.StreamHandler)
                   and not isinstance(h, logging.handlers.RotatingFileHandler)
            ]

            assert len(console_handlers) == 1
            handler = console_handlers[0]
            assert isinstance(handler.formatter, ColoredFormatter)
            assert handler.level == LOG_LEVELS["DEBUG"]

    def test_file_handler_configuration(self, mock_config, temp_log_dir):
        """Test file handler setup"""
        mock_config.get.side_effect = lambda key, default=None: (
            str(temp_log_dir) if key == "logging.log_dir"
            else {"logging.log_file_name": "test.log"}.get(key, default)
        )

        with patch('src.core.log_manager.Config', return_value=mock_config):
            manager = LogManager()
            logger = manager.get_logger("test_file")

            file_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.handlers.RotatingFileHandler)
            ]

            assert len(file_handlers) == 1
            handler = file_handlers[0]
            assert isinstance(handler.formatter, logging.Formatter)
            assert handler.level == LOG_LEVELS["INFO"]

    def test_log_exception(self, mock_config):
        """Test exception logging functionality"""
        with patch('src.core.log_manager.Config', return_value=mock_config):
            manager = LogManager()
            logger = Mock(spec=logging.Logger)

            try:
                raise ValueError("test error")
            except ValueError as e:
                manager.log_exception(
                    logger=logger,
                    exc=e,
                    message="Error occurred",
                    extra={"context": "test"}
                )

            # Verify error logging
            logger.error.assert_called_once()
            call_args = logger.error.call_args[0][0]
            assert "Error occurred" in call_args
            assert "test error" in call_args

            # Verify traceback logging
            logger.debug.assert_called_once_with(
                "Exception traceback:",
                exc_info=True
            )

    def test_update_configuration(self, mock_config):
        """Test configuration update process"""
        with patch('src.core.log_manager.Config', return_value=mock_config):
            manager = LogManager()
            logger = manager.get_logger("test_update")
            initial_handlers = len(logger.handlers)

            manager.update_configuration()

            assert len(logger.handlers) == initial_handlers
            assert all(handler.formatter is not None for handler in logger.handlers)

    @pytest.mark.parametrize("level_name", [
        "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    ])
    def test_log_levels(self, mock_config, level_name):
        """Test logging at different levels"""
        with patch('src.core.log_manager.Config', return_value=mock_config):
            manager = LogManager()
            logger = manager.get_logger("test_levels")

            with patch.object(logger, '_log') as mock_log:
                log_method = getattr(logger, level_name.lower())
                log_method("Test message")

                mock_log.assert_called_once()
                assert mock_log.call_args[0][0] == LOG_LEVELS[level_name]

    def test_disabled_logging(self):
        """Test behavior when logging is disabled"""
        config = Mock()
        config.get.side_effect = lambda key, default=None: False if key == "logging.enabled" else default

        with patch('src.core.log_manager.Config', return_value=config):
            manager = LogManager()
            logger = manager.get_logger("test_disabled")
            assert not logger.handlers
