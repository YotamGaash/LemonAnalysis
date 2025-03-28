"""
Base authentication strategy module for handling website login.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from playwright.sync_api import Page

from legacy.src.utils.logging_util import setup_logger


class BaseAuth(ABC):
    """
    Base authentication strategy class for handling login to various platforms.

    This class defines the interface for authentication strategies and provides
    common functionality for login operations.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the authentication strategy.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = setup_logger(f"{self.__class__.__name__}")
        self.page: Optional[Page] = None
        self.is_authenticated = False

    def initialize(self, page: Page) -> None:
        """
        Set the Playwright page object for this authentication strategy.

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
    async def authenticate(self) -> bool:
        """
        Authenticate the user on the platform.

        This method must be implemented by all authentication strategies.

        Returns:
            bool: True if authentication was successful, False otherwise

        Raises:
            AuthenticationError: If authentication fails
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            "Authentication strategy must implement authenticate()")

    def is_login_required(self) -> bool:
        """
        Check if login is required based on the current page state.

        Returns:
            bool: True if login is required, False if already logged in
        """
        if self.page is None:
            self.logger.error(
                "Page not initialized, cannot check login status")
            return True

        # Basic implementation, subclasses should override with specific logic
        return not self.is_authenticated

    def verify_login(self) -> bool:
        """
        Verify if the login was successful.

        Returns:
            bool: True if successfully logged in, False otherwise
        """
        # Basic implementation, subclasses should override with specific logic
        return self.is_authenticated
