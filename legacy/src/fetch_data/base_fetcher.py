import json
import os
import time
from abc import abstractmethod
from contextlib import AbstractContextManager
from typing import Optional, Dict, Any

from playwright.sync_api import Page, Error as PlaywrightError

from legacy.src.utils.config_util import ConfigUtil
from legacy.src.utils.logging_util import log_exception
from legacy.src.fetch_data.exceptions import (
    InitializationError, FetchingError
)

class BaseFetcher(AbstractContextManager):
    """
    Base class for all data fetchers.

    This abstract class defines the interface and common functionality for all platform-specific
    data fetchers. It handles configuration management, logging, error handling, and resource
    management.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base fetcher.

        Args:
            config: Optional custom configuration that overrides default settings.
        """
        # Setup logger
        from legacy.src.utils.logging_util import setup_logger
        self.logger = setup_logger(f"{self.__class__.__name__}")
        self.logger.info(f"Initializing {self.__class__.__name__}")

        # Initialize with empty config (will be populated in _load_config)
        self.config = {}

        # Determine platform early (needed for _load_config)
        if config and "platform" in config:
            self.platform = config["platform"]
        else:
            from legacy.src.utils.platform_util import determine_platform
            self.platform = determine_platform(config)

        # Load configuration
        self._load_config(config)

        # Initialize core attributes
        self.page: Optional[Page] = None
        self.is_initialized = False

        # Timeout settings
        self.timeout = self.config.get("timeout",
                                       ConfigUtil.get("fetcher.timeout",
                                                      60000))
        self.retry_attempts = self.config.get(
            "retry_attempts",
            ConfigUtil.get("constants.retrieval_attempts", 3)
        )

    def _load_config(self,
                     custom_config: Optional[Dict[str, Any]] = None) -> None:
        """Load configuration settings from ConfigUtil and custom overrides."""
        try:
            # Merge with platform-specific configuration
            platform_config = ConfigUtil.get("platforms", {})
            if self.platform in platform_config:
                self.config.update(platform_config.get(self.platform, {}))

            # Merge with fetcher general config
            fetcher_config = ConfigUtil.get("fetcher", {})
            self.config.update(fetcher_config)

            # Apply any custom configuration (highest priority)
            if custom_config:
                self.config.update(custom_config)

            self.logger.debug(
                f"Configuration loaded for {self.__class__.__name__}")
        except Exception as e:
            from legacy.src.fetch_data.exceptions import ConfigurationError
            from legacy.src.utils.logging_util import log_exception

            error_msg = f"Error loading configuration: {str(e)}"
            log_exception(self.logger, e, "Error loading configuration")
            raise ConfigurationError(error_msg) from e

    @abstractmethod
    def initialize(self, page: Page) -> None:
        """
        Initialize the fetcher with a Playwright page.

        Args:
            page: Playwright page object to use for web interactions

        Raises:
            InitializationError: If page is None
        """
        if page is None:
            raise InitializationError("Page cannot be None")

        self.page = page
        self.is_initialized = True
        self.logger.info(
            f"Initialized {self.__class__.__name__} with Playwright page")

    @abstractmethod
    def fetch(self, query: str, **kwargs) -> Any:
        """
        Main method to fetch data from the source.

        This method should be implemented by subclasses to perform the actual data fetching.

        Args:
            query: The search query or identifier for the data to fetch
            **kwargs: Additional parameters specific to the fetcher implementation

        Returns:
            The fetched data in a format specific to the implementation

        Raises:
            FetchingError: If fetcher not initialized
            NotImplementedError: If not implemented by subclass
        """
        if not self.is_initialized:
            raise FetchingError(
                "Fetcher must be initialized before fetching data")

    @abstractmethod
    def extract(self, element) -> Dict[str, Any]:
        """
        Extract structured data from elements.

        Args:
            element: The element to extract data from (type depends on implementation)

        Returns:
            Dictionary containing the extracted data

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    def close(self) -> None:
        """
        Clean up resources used by the fetcher.
        """
        try:
            if self.page:
                self.logger.debug("Closing Playwright page")
                self.page.close()
        except PlaywrightError as e:
            self.logger.warning(f"Error while closing page: {str(e)}")
        finally:
            self.page = None
            self.is_initialized = False
            self.logger.info(f"Closed {self.__class__.__name__} resources")

    def _retry(self, func, attempts=None, exceptions=(Exception,), delay=2,
               *args,
               **kwargs):
        """Generic retry mechanism for safe operations."""
        attempts = attempts or self.retry_attempts
        for attempt in range(1, attempts + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if attempt < attempts:
                    self.logger.warning(
                        f"[{self.platform}] Attempt {attempt}/{attempts} failed: {e}, retrying...")
                    time.sleep(delay)
                else:
                    log_exception(self.logger, e,
                                  f"All {attempts} retry attempts failed for operation")
                    raise FetchingError(
                        f"Operation failed after {attempts} attempts") from e

    @staticmethod
    def sanitize_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizes or formats common types of data fields from raw extraction."""
        sanitized_data = {}
        for key, value in raw_data.items():
            if isinstance(value, str):
                sanitized_data[key] = value.strip()
            else:
                sanitized_data[key] = value
        return sanitized_data

    def handle_exception(self, exc: Exception, message: str):
        """Logs and raises formatted exceptions."""
        log_exception(self.logger, exc, message)
        raise FetchingError(message) from exc

    def save_session(self, session_data: Dict[str, Any], path: str):
        """Saves session data (cookies/tokens) to a file to reuse later sessions."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as file:
                json.dump(session_data, file, indent=2)
            self.logger.debug(f"Session data saved successfully: {path}")
        except Exception as e:
            self.handle_exception(e, f"Failed saving session data: {path}")

    def load_session(self, path: str) -> dict[Any, Any] | None | Any:
        """Loads session data (cookies/tokens) from a file."""
        if not os.path.exists(path):
            self.logger.warning(f"Session file does not exist: {path}")
            return {}

        try:
            with open(path, 'r') as file:
                data = json.load(file)
            self.logger.debug(f"Session data loaded successfully: {path}")
            return data
        except Exception as e:
            self.handle_exception(e, f"Failed loading session data: {path}")

    def health_check(self):
        """Validates fetcher readiness."""
        if not self.is_initialized or not self.page:
            raise InitializationError(
                f"{self.platform} fetcher not properly initialized.")

        try:
            _ = self.page.title()
            self.logger.debug(f"{self.platform} fetcher health check passed.")
        except Exception as e:
            self.handle_exception(e,
                                  f"{self.platform} fetcher health check failed.")

    def capture_screenshot(self, path: str):
        """Captures a screenshot and saves it to the provided path."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.page.screenshot(path=path)
            self.logger.info(f"Captured screenshot: {path}")
        except Exception as e:
            self.handle_exception(e, "Screenshot capturing failed")

    def wait_for_selector(self, selector: str, timeout=None):
        """Wait for specified selector to be visible."""
        timeout = timeout or self.timeout

        def _wait():
            self.page.wait_for_selector(selector, timeout=timeout)
            self.logger.debug(
                f"{self.platform}: Selector '{selector}' is visible")

        self._retry(_wait, exceptions=(PlaywrightError,))

    def __enter__(self):
        """
        Context manager entry point.

        Returns:
            Self
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point that ensures resources are properly cleaned up.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised

        Returns:
            False to propagate exceptions
        """
        if exc_type is not None:
            log_exception(self.logger, exc_val,
                          f"Error in {self.__class__.__name__}")

        self.close()
        return False  # Propagate any exceptions
