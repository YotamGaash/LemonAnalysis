# src/utils/logger.py

import logging
import sys  # Import sys for stderr output

def setup_logger(logger_name, level=logging.INFO):
    """
    Sets up and returns a logger instance with a console handler.

    Args:
        logger_name (str): The name of the logger (usually __name__).
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Prevent duplicate handlers (if logger is called multiple times in a module)
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler(sys.stderr) # Send output to stderr
        console_handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger

if __name__ == "__main__":
    # used for testing purposes
    test_logger = setup_logger(__name__, logging.DEBUG)
    test_logger.debug("This is a debug message.")
    test_logger.info("This is an info message.")
    test_logger.warning("This is a warning message.")
    test_logger.error("This is an error message.")
    test_logger.critical("This is a critical message.")