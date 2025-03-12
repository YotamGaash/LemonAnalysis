import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from src.utils.config_util import ConfigUtil


def setup_logger(logger_name: str) -> logging.Logger:
    """
    Sets up and returns a logger instance with console and rotating file handlers.
    All settings are fetched from the ConfigUtil.

    Args:
        logger_name (str): The name of the logger.

    Returns:
        logging.Logger: A configured logger instance.
    """
    # Fetch logging configuration from ConfigUtil
    log_dir = ConfigUtil.get("logging.log_dir")
    log_file_name = ConfigUtil.get("logging.log_file_name")
    max_file_size = ConfigUtil.get("logging.max_file_size")
    backup_count = ConfigUtil.get("logging.backup_count")
    console_level = getattr(logging, ConfigUtil.get("logging.log_level_console"))
    file_level = getattr(logging, ConfigUtil.get("logging.log_level_file"))
    log_format = ConfigUtil.get("logging.log_format")

    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Log file path
    log_file_path = os.path.join(log_dir, log_file_name)

    # Initialize the logger
    logger = logging.getLogger(logger_name)
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
    file_handler = RotatingFileHandler(log_file_path, maxBytes=max_file_size, backupCount=backup_count)
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def log_exception(logger: logging.Logger, ex: Exception, message: str = "An error occurred"):
    """
    Logs an exception with traceback.

    Args:
        logger (logging.Logger): Logger instance to log with.
        ex (Exception): Exception instance to log.
        message (str): Optional message to provide context (default is "An error occurred").
    """
    logger.error(message, exc_info=True)
