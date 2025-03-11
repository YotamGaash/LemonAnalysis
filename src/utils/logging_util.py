import logging
import sys
import os
from logging.handlers import RotatingFileHandler


def setup_logger(logger_name: str, console_level=logging.DEBUG, file_level=logging.INFO, log_file="app.log"):
    """
    Sets up and returns a logger instance with console and rotating file handlers.

    Args:
        logger_name (str): The name of the logger (usually __name__).
        console_level (int): Logging level for the console handler.
        file_level (int): Logging level for the file handler.
        log_file (str): Name of the log file (default is 'app.log').

    Returns:
        logging.Logger: A configured logger instance.
    """
    # Set the default log directory to "logs/" in the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))  # Navigate to project root
    log_dir = os.path.join(project_root, "logs")  # Set logs/ directory
    os.makedirs(log_dir, exist_ok=True)  # Create "logs/" directory if it doesn't exist

    # Full path for the log file
    log_file_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Root logger level; handlers filter actual output

    # Reset handlers to avoid false `hasHandlers()` issues
    if logger.handlers:  # Clear existing handlers unconditionally
        logger.handlers.clear()

    # Prevent duplicate handlers
    # Console logging handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Rotating file logging handler
    file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
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
