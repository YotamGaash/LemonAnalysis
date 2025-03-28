import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from typing import Optional

from legacy.src.utils.config_util import ConfigUtil


def setup_logger(logger_name: str) -> logging.Logger:
    """
    Sets up and returns a logger instance with console and rotating file handlers.
    All settings are fetched from ConfigUtil.

    Args:
        logger_name (str): The name of the logger.

    Returns:
        logging.Logger: A configured logger instance.
    """
    # If logger already exists with handlers, return it
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger

    # Fetch logging configuration from ConfigUtil
    config_util = ConfigUtil()  # Ensure instance
    log_dir = config_util.get("logging.log_dir", "logs")
    log_file_name = config_util.get("logging.log_file_name", "app.log")
    max_file_size = config_util.get("logging.max_file_size",
                                    5242880)  # 5 MB default
    backup_count = config_util.get("logging.backup_count", 3)

    # Get log levels with safe fallbacks
    console_level_name = config_util.get("logging.log_level_console", "DEBUG")
    file_level_name = config_util.get("logging.log_level_file", "INFO")
    console_level = getattr(logging, console_level_name.upper(), logging.DEBUG)
    file_level = getattr(logging, file_level_name.upper(), logging.INFO)

    log_format = config_util.get("logging.log_format",
                                 "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Log file path
    log_file_path = os.path.join(log_dir, log_file_name)

    # Initialize the logger
    logger.setLevel(logging.DEBUG)  # Set root logger level to DEBUG

    # Clear existing handlers to avoid duplicated logs
    if logger.handlers:
        logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Rotating file handler
    file_handler = RotatingFileHandler(log_file_path, maxBytes=max_file_size,
                                       backupCount=backup_count)
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

def log_exception(logger: logging.Logger, exc: Optional[Exception],
                  message: str) -> None:
    """
    Log an exception with detailed traceback and a custom message.

    Args:
        logger: Logger instance to use
        exc: Exception object to log
        message: Custom message to add to the log
    """
    if exc is None:
        logger.error(message)
        return

    logger.error(f"{message}: {str(exc)}")
    logger.debug(f"Exception details: {traceback.format_exc()}")
