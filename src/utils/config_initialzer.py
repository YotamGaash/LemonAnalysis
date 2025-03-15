"""
Utility for initializing configuration for the application.
"""
import os
from pathlib import Path
from typing import List, Optional

from src.utils.config_util import ConfigUtil
from src.utils.logging_util import setup_logger

logger = setup_logger(__name__)

def initialize_configuration(config_paths: Optional[List[str]] = None):
    """
    Initialize the application configuration by loading all config files.

    Args:
        config_paths: List of configuration file paths to load

    Returns:
        ConfigUtil instance with loaded configuration
    """
    if config_paths is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
        config_paths = [
            str(base_dir / "config.json"),
            str(base_dir / "fetcher_config.json")
        ]

    # Load each configuration file
    for path in config_paths:
        if os.path.exists(path):
            ConfigUtil.load_config(path)
        else:
            logger = setup_logger(__name__)
            logger.warning(f"Configuration file not found: {path}")

    return ConfigUtil

