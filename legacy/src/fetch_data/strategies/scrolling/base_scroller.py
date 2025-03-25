"""
Base scrolling strategy module for handling page navigation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union

from playwright.sync_api import Page, Error as PlaywrightError

from src.utils.logging_util import setup_logger, log_exception
from src.fetch_data.exceptions import ScrollingError


class BaseScroller(ABC):
    """
    Base scrolling strategy class for handling page scrolling on various platforms.

    This class defines the interface for scrolling strategies and provides
    common functionality for navigation operations.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the scrolling strategy.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = setup_logger(f"{self.__class__.__name__}")
        self.page: Optional[Page] = None

        # Scrolling configuration
        self.scroll_timeout = self.config.get("scroll_timeout",
                                              30000)  # 30 seconds default
        self.scroll_delay = self.config.get("scroll_delay",
                                            1000)  # 1 second default
        self.max_scroll_attempts = self.config.get("max_scroll_attempts", 10)

    def initialize(self, page: Page) -> None:
        """
        Set the Playwright page object for this scrolling strategy.

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
    async def scroll(self, target_items: int = 0, max_time: int = 0) -> bool:
        """
        Scroll the page to load more content.

        This method must be implemented by all scrolling strategies.

        Args:
            target_items: Target number of items to load (0 for unlimited)
            max_time: Maximum time in milliseconds to scroll (0 for unlimited)

        Returns:
            bool: True if scrolling was successful or reached limits, False if error

        Raises:
            ScrollingError: If scrolling fails
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Scrolling strategy must implement scroll()")

    async def scroll_to_element(self, selector: str) -> bool:
        """
        Scroll to a specific element on the page.

        Args:
            selector: CSS selector for the target element

        Returns:
            bool: True if element was found and scrolled to, False otherwise
        """
        if self.page is None:
            self.logger.error("Page not initialized, cannot scroll to element")
            return False

        try:
            element = await self.page.wait_for_selector(selector,
                                                        timeout=self.scroll_timeout)
            if element:
                await element.scroll_into_view_if_needed()
                return True
        except PlaywrightError as e:
            log_exception(self.logger, e,
                          f"Error scrolling to element with selector '{selector}'")

        return False

    async def get_scroll_position(self) -> Dict[str, int]:
        """
        Get the current scroll position of the page.

        Returns:
            Dict containing scroll X and Y positions
        """
        if self.page is None:
            self.logger.error(
                "Page not initialized, cannot get scroll position")
            return {"x": 0, "y": 0}

        try:
            scroll_position = await self.page.evaluate("""
                () => {
                    return {
                        x: window.scrollX || window.pageXOffset,
                        y: window.scrollY || window.pageYOffset
                    }
                }
            """)
            return scroll_position
        except PlaywrightError as e:
            log_exception(self.logger, e, "Error getting scroll position")
            return {"x": 0, "y": 0}
