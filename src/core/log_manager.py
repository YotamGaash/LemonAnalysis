# src/core/logging.py
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any
import colorama

from .config import Config
from .constants import (
    DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT,
    DEFAULT_MAX_FILE_SIZE, DEFAULT_BACKUP_COUNT,
    LOG_LEVELS
)

# Initialize colorama for Windows support
colorama.init()


class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored console output"""

    COLORS = {
        'DEBUG': colorama.Fore.CYAN,
        'INFO': colorama.Fore.GREEN,
        'WARNING': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRITICAL': colorama.Fore.RED + colorama.Style.BRIGHT
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors"""
        if not record.exc_info:
            level = record.levelname
            if level in self.COLORS:
                record.levelname = f"{self.COLORS[level]}{level}{colorama.Style.RESET_ALL}"
        return super().format(record)


class LogManager:
    """
    Centralized logging management system that works tightly with Config.
    Implements singleton pattern for global logging management.
    """

    _instance: Optional[LogManager] = None
    _initialized: bool = False

    def __new__(cls) -> LogManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize LogManager if not already initialized."""
        if self._initialized:
            return

        self.config = Config()
        self._loggers: Dict[str, logging.Logger] = {}
        self._handlers: Dict[str, logging.Handler] = {}
        self._formatter: Optional[logging.Formatter] = None

        self._setup_logging()
        LogManager._initialized = True

    def _setup_logging(self) -> None:
        """Initialize the logging system based on configuration."""
        if not self.config.get("logging.enabled", True):
            return

        self._setup_formatter()
        self._setup_handlers()

    def _setup_formatter(self) -> None:
        """Set up the default formatter based on config."""
        log_format = self.config.get("logging.format", DEFAULT_LOG_FORMAT)
        date_format = self.config.get("logging.date_format", DEFAULT_DATE_FORMAT)
        self._formatter = logging.Formatter(log_format, date_format)

    def _create_console_handler(self) -> logging.StreamHandler:
        """Create and configure console handler."""
        handler = logging.StreamHandler(sys.stdout)

        console_format = self.config.get(
            "logging.console.format",
            self.config.get("logging.format", DEFAULT_LOG_FORMAT)
        )

        if self.config.get("logging.console.use_colors", True):
            handler.setFormatter(ColoredFormatter(console_format))
        else:
            handler.setFormatter(logging.Formatter(console_format))

        level_name = self.config.get("logging.console.level", "DEBUG").upper()
        handler.setLevel(LOG_LEVELS[level_name])

        return handler

    def _create_file_handler(self) -> RotatingFileHandler:
        """Create and configure rotating file handler."""
        log_dir = Path(self.config.get("logging.log_dir", "logs"))
        log_file = log_dir / self.config.get("logging.log_file_name", "app.log")
        log_dir.mkdir(parents=True, exist_ok=True)

        handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.get("logging.max_file_size", DEFAULT_MAX_FILE_SIZE),
            backupCount=self.config.get("logging.backup_count", DEFAULT_BACKUP_COUNT),
            encoding=self.config.get("logging.encoding", "utf-8")
        )

        file_format = self.config.get(
            "logging.file.format",
            self.config.get("logging.format", DEFAULT_LOG_FORMAT)
        )
        handler.setFormatter(logging.Formatter(file_format))

        level_name = self.config.get("logging.file.level", "INFO").upper()
        handler.setLevel(LOG_LEVELS[level_name])

        return handler

    def _setup_handlers(self) -> None:
        """Set up logging handlers based on configuration."""
        # Console handler
        if self.config.get("logging.console.enabled", True):
            self._handlers["console"] = self._create_console_handler()

        # File handler
        if self.config.get("logging.file.enabled", True):
            self._handlers["file"] = self._create_file_handler()

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the specified name."""
        if name in self._loggers:
            return self._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Clear any existing handlers
        logger.handlers.clear()

        # Add all configured handlers
        for handler in self._handlers.values():
            logger.addHandler(handler)

        self._loggers[name] = logger
        return logger

    def log_exception(
            self,
            logger: logging.Logger,
            exc: Optional[Exception],
            message: str,
            extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Enhanced exception logging with configurable behavior."""
        if exc is None:
            logger.error(message, extra=extra)
            return

        error_context = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)
        }
        if extra:
            error_context.update(extra)

        logger.error(f"{message}: {str(exc)}", extra=error_context)

        if self.config.get("logging.errors.include_traceback", True):
            traceback_level = self.config.get("logging.errors.traceback_level", "DEBUG")
            level_func = getattr(logger, traceback_level.lower(), logger.debug)
            level_func("Exception traceback:", exc_info=True)

    def update_configuration(self) -> None:
        """Update logging configuration based on current config values."""
        # Clear existing handlers
        for logger in self._loggers.values():
            logger.handlers.clear()
        self._handlers.clear()

        # Reinitialize with new configuration
        self._setup_logging()

        # Reattach handlers to existing loggers
        for logger in self._loggers.values():
            for handler in self._handlers.values():
                logger.addHandler(handler)
