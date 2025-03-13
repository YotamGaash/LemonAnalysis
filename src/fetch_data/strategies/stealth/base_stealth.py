"""
Base stealth strategy module for handling anti-detection measures.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union

from playwright.sync_api import Page, Error as PlaywrightError

from src.utils.logging_util import setup_logger, log_exception
from src.fetch_data.exceptions import StealthError


class BaseStealth(ABC):
    """
    Base stealth strategy class for handling anti-detection on various platforms.

    This class defines the interface for stealth strategies and provides
    common functionality for evading bot detection.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the stealth strategy.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = setup_logger(f"{self.__class__.__name__}")
        self.page: Optional[Page] = None

        # Stealth configuration
        self.user_agent = self.config.get("user_agent", "")
        self.use_proxy = self.config.get("use_proxy", False)
        self.proxy_config = self.config.get("proxy", {})

    def initialize(self, page: Page) -> None:
        """
        Set the Playwright page object for this stealth strategy.

        Args:
            page: Playwright Page object

        Raises:
            ValueError: If page is None
        """
        if page is None:
            raise ValueError("Page cannot be None")

        self.page = page
        self.logger.info(
            f"Initialized {self.__class__.__name__} with Playwright page")

    @abstractmethod
    async def apply(self) -> bool:
        """
        Apply stealth measures to the current browser session.

        This method must be implemented by all stealth strategies.

        Returns:
            bool: True if stealth measures were applied successfully, False otherwise

        Raises:
            StealthError: If applying stealth measures fails
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Stealth strategy must implement apply()")

    async def set_random_user_agent(self) -> bool:
        """
        Set a random user agent from the configured list or a default list.

        Returns:
            bool: True if user agent was set successfully, False otherwise
        """
        if self.page is None:
            self.logger.error("Page not initialized, cannot set user agent")
            return False

        try:
            # Use provided user agent or a default one
            user_agent = self.user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

            await self.page.evaluate(
                f"() => {{ Object.defineProperty(navigator, 'userAgent', {{ get: () => '{user_agent}' }}); }}")
            self.logger.debug(f"Set user agent: {user_agent}")
            return True
        except PlaywrightError as e:
            log_exception(self.logger, e, "Error setting user agent")
            return False

    async def is_detected(self) -> bool:
        """
        Check if the current session has been detected as a bot.

        Returns:
            bool: True if detected as a bot, False if not detected or cannot determine
        """
        if self.page is None:
            self.logger.error("Page not initialized, cannot check if detected")
            return True

        # Basic implementation, subclasses should implement specific detection checks
        try:
            # Check for common bot detection indicators
            has_captcha = await self.page.query_selector(
                "iframe[src*='captcha']") is not None
            has_block_message = await self.page.query_selector(
                "body:has-text('blocked')") is not None

            return has_captcha or has_block_message
        except PlaywrightError as e:
            log_exception(self.logger, e, "Error checking if detected as bot")
            return True  # Assume detected if we can't check
