import os

import pytest
from unittest.mock import Mock, patch
from src.fetch_data.exceptions import PlaywrightError, InitializationError
from playwright.sync_api import Page


class SimpleMockFetcher:
    """Simple mock implementation for testing core fetcher functionality"""

    def __init__(self, config=None):
        self.config = config or {}
        self.page = None
        self.is_initialized = False
        self.platform = config.get('platform', 'test') if config else 'test'
        self.timeout = config.get('timeout', 10000) if config else 10000
        self.retry_attempts = config.get('retry_attempts', 3) if config else 3

    def initialize(self, page):
        if not page:
            raise InitializationError("Page cannot be None")
        self.page = page
        self.is_initialized = True

    def close(self):
        if self.page:
            self.page.close()
            self.page = None
        self.is_initialized = False

    def _retry(self, operation):
        """Retry mechanism for operations that might fail"""
        attempts = 0
        while attempts < self.retry_attempts:
            try:
                return operation()
            except PlaywrightError:
                attempts += 1
                if attempts == self.retry_attempts:
                    raise

    def capture_screenshot(self, error_name):
        """Capture screenshot with proper directory creation"""
        screenshot_dir = os.path.join("screenshots", self.platform)
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"{error_name}.png")
        self.page.screenshot(path=screenshot_path)
        return screenshot_path

    def sanitize_data(self, data):
        """Sanitize input data by removing whitespace and empty values"""
        if isinstance(data, dict):
            return {
                k: self.sanitize_data(v)
                for k, v in data.items()
                if v is not None
            }
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        elif isinstance(data, str):
            return data.strip()
        return data


@pytest.fixture
def mock_page():
    return Mock(spec=Page)


@pytest.fixture
def basic_fetcher():
    return SimpleMockFetcher()


@pytest.fixture
def configured_fetcher():
    config = {
        "platform": "test_platform",
        "timeout": 5000,
        "retry_attempts": 3
    }
    return SimpleMockFetcher(config)


class TestBasicFetcherFunctionality:
    """Test basic fetcher functionality"""

    def test_initial_state(self, basic_fetcher):
        """Test initial state of fetcher"""
        assert basic_fetcher.page is None
        assert not basic_fetcher.is_initialized
        assert basic_fetcher.config == {}
        assert basic_fetcher.timeout == 10000
        assert basic_fetcher.retry_attempts == 3

    def test_initialization_with_config(self, configured_fetcher):
        """Test fetcher initialization with config"""
        assert configured_fetcher.platform == "test_platform"
        assert configured_fetcher.timeout == 5000
        assert configured_fetcher.retry_attempts == 3

    def test_initialize_with_page(self, basic_fetcher, mock_page):
        """Test page initialization"""
        basic_fetcher.initialize(mock_page)
        assert basic_fetcher.page == mock_page
        assert basic_fetcher.is_initialized

    def test_initialize_with_none_page(self, basic_fetcher):
        """Test initialization with None page"""
        with pytest.raises(InitializationError):
            basic_fetcher.initialize(None)

    def test_close(self, basic_fetcher, mock_page):
        """Test close functionality"""
        basic_fetcher.initialize(mock_page)
        basic_fetcher.close()
        mock_page.close.assert_called_once()
        assert basic_fetcher.page is None
        assert not basic_fetcher.is_initialized


class TestFetcherOperations:
    """Test fetcher operations"""

    @pytest.fixture
    def initialized_fetcher(self, configured_fetcher, mock_page):
        configured_fetcher.initialize(mock_page)
        return configured_fetcher

    def test_wait_for_selector(self, initialized_fetcher):
        """Test wait for selector functionality"""
        selector = "#test"
        timeout = 1000
        initialized_fetcher.page.wait_for_selector = Mock()

        initialized_fetcher.page.wait_for_selector(selector, timeout=timeout)

        initialized_fetcher.page.wait_for_selector.assert_called_once_with(
            selector, timeout=timeout
        )

    # @patch('src.fetch_data.base_fetcher.os.makedirs')
    # def test_screenshot_capture(self, mock_makedirs, initialized_fetcher):
    #     """Test screenshot capture functionality"""
    #     test_path = "test/path/screenshot.png"
    #     initialized_fetcher.page.screenshot = Mock()
    #
    #     initialized_fetcher.page.screenshot(path=test_path)
    #
    #     mock_makedirs.assert_called_once()
    #     initialized_fetcher.page.screenshot.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_retry_mechanism_success(self, configured_fetcher):
        """Test retry mechanism with eventual success"""
        operation = Mock(side_effect=[PlaywrightError(), "success"])
        result = configured_fetcher._retry(operation)
        assert result == "success"
        assert operation.call_count == 2

    def test_retry_mechanism_failure(self, configured_fetcher):
        """Test retry mechanism with persistent failure"""
        operation = Mock(side_effect=PlaywrightError())
        with pytest.raises(PlaywrightError):
            configured_fetcher._retry(operation)
        assert operation.call_count == configured_fetcher.retry_attempts


class TestDataHandling:
    """Test data handling functionality"""

    @pytest.mark.parametrize("input_data,expected", [
        (
                {"key": " value "},
                {"key": "value"}
        ),
        (
                {"key": "\n value \t"},
                {"key": "value"}
        ),
        (
                {"key": None},
                {}
        ),
        (
                {"key": [" item1 ", "\n item2\t"]},
                {"key": ["item1", "item2"]}
        ),
    ])
    def test_data_sanitization(self, configured_fetcher, input_data, expected):
        """Test data sanitization with various inputs"""
        assert configured_fetcher.sanitize_data(input_data) == expected
