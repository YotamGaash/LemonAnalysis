"""
Utility functions for platform-related operations.
"""
from typing import Dict, Any, Optional

from legacy.src.utils.config_util import ConfigUtil


def determine_platform(config: Optional[Dict[str, Any]] = None) -> str:
    """
    Determine which platform to use based on configuration.

    Args:
        config: Dictionary with configuration values

    Returns:
        String representing the platform name to use
    """
    if config is None:
        config = {}

    # First check explicit platform setting in provided config
    platform = config.get("platform")

    # Then check default platform from fetcher config
    if not platform:
        platform = ConfigUtil.get("fetcher.default_platform")

    # Fallback to a known supported platform
    if not platform or platform == "unknown":
        platforms = ConfigUtil.get("platforms", {}).keys()
        if platforms:
            platform = next(iter(platforms), "facebook")
        else:
            platform = "facebook"  # Default to facebook if nothing else available

    return platform


def get_platform_config(platform: str) -> Dict[str, Any]:
    """
    Get configuration for a specific platform.

    Args:
        platform: Platform identifier

    Returns:
        Platform-specific configuration dictionary
    """
    platforms = ConfigUtil.get("platforms", {})
    return platforms.get(platform, {})
