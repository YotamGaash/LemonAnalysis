"""
Utility for initializing configuration for the application.
"""
import os
from pathlib import Path
from typing import Optional

from legacy.src.utils.config_util import ConfigUtil
from legacy.src.utils.logging_util import setup_logger

logger = setup_logger(__name__)


def initialize_configuration(main_config: Optional[str] = None,
                             fetcher_config: Optional[str] = None) -> ConfigUtil:
    """
    Initialize the application configuration.

    Args:
        main_config: Path to main configuration file. If None, uses default path
        fetcher_config: Path to fetcher configuration file. If None, uses default path

    Returns:
        ConfigUtil instance with loaded configuration

    Raises:
        ValueError: If configuration files cannot be loaded
    """
    try:
        if main_config is None or fetcher_config is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            main_config = main_config or str(base_dir / "config" / "app_config.json")
            fetcher_config = fetcher_config or str(base_dir / "config" / "fetcher_config.json")

        # Validate paths exist
        for path in [main_config, fetcher_config]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Configuration file not found: {path}")

        # Initialize ConfigUtil with the specified paths
        config_util = ConfigUtil(main_config=main_config, fetcher_config=fetcher_config)

        # Create necessary directories based on configuration
        _ensure_directories(config_util)

        return config_util

    except Exception as e:
        logger.error(f"Failed to initialize configuration: {str(e)}")
        raise


def _ensure_directories(config_util: ConfigUtil) -> None:
    """
    Ensure all required directories exist based on configuration.

    Args:
        config_util: Initialized ConfigUtil instance
    """
    try:
        # Create logging directory first
        log_dir = config_util.get("logging.log_dir")
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)

        # Create storage directories
        storage_paths = [
            config_util.session_path,
            config_util.screenshots_path,
            config_util.cache_path,
            config_util.proxies_path,
            config_util.raw_data_path,
            config_util.processed_data_path
        ]

        for path in storage_paths:
            if path:
                Path(path).mkdir(parents=True, exist_ok=True)

    except Exception as e:
        logger.error(f"Failed to create required directories: {str(e)}")
        raise
