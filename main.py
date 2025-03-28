import pytest
from unittest.mock import Mock, patch
from playwright.sync_api import Page, Error as PlaywrightError
from legacy.src.fetch_data.base_fetcher import BaseFetcher


# Concrete implementation of BaseFetcher for testing
class TestFetcher(BaseFetcher):
    def initialize(self, page):
        super().initialize(page)

    def fetch(self, query: str, **kwargs):
        return {"data": "test_data"}

    def extract(self, element):
        return {"extracted": "test_data"}


@pytest.fixture
def mock_page():
    return Mock(spec=Page)


@pytest.fixture
def test_fetcher():
    return TestFetcher()


@pytest.fixture
def configured_fetcher(mock_config):
    config = {
        "platform": "test_platform",
        "timeout": 5000,
        "retry_attempts": 3
    }
    return TestFetcher(config)


class TestBaseFetcher:
    def test_initialization_without_config(self, test_fetcher):
        """Test fetcher initialization without config"""
        assert test_fetcher.config == {}
        assert test_fetcher.page is None
        assert not test_fetcher.is_initialized

    def test_initialization_with_config(self, configured_fetcher):
        """Test fetcher initialization with config"""
        assert configured_fetcher.platform == "test_platform"
        assert configured_fetcher.timeout == 5000
        assert configured_fetcher.retry_attempts == 3

    def test_initialize_with_page(self, test_fetcher, mock_page):
        """Test page initialization"""
        test_fetcher.initialize(mock_page)
        assert test_fetcher.page == mock_page
        assert test_fetcher.is_initialized

    def test_close(self, test_fetcher, mock_page):
        """Test resource cleanup"""
        test_fetcher.page = mock_page
        test_fetcher.close()
        mock_page.close.assert_called_once()
        assert test_fetcher.page is None
        assert not test_fetcher.is_initialized

    @patch('src.fetchers.base_fetcher.setup_logger')
    def test_logging_setup(self, mock_setup_logger, test_fetcher):
        """Test logger initialization"""
        assert test_fetcher.logger is not None
        mock_setup_logger.assert_called_once()

    def test_context_manager(self, configured_fetcher, mock_page):
        """Test context manager protocol"""
        with configured_fetcher as fetcher:
            fetcher.page = mock_page
            assert fetcher.page is not None
        assert fetcher.page is None

    @pytest.mark.parametrize("selector,timeout", [
        ("#test-id", 1000),
        (".test-class", 2000),
    ])
    def test_wait_for_selector(self, configured_fetcher, mock_page, selector,
                               timeout):
        """Test wait_for_selector with different selectors and timeouts"""
        configured_fetcher.page = mock_page
        configured_fetcher.wait_for_selector(selector, timeout)
        mock_page.wait_for_selector.assert_called_with(selector,
                                                       timeout=timeout)

    def test_retry_mechanism(self, configured_fetcher):
        """Test retry mechanism for failed operations"""
        failed_operation = Mock(
            side_effect=[PlaywrightError("Test error"), "success"])
        result = configured_fetcher._retry(failed_operation)
        assert result == "success"
        assert failed_operation.call_count == 2

    def test_retry_exhaustion(self, configured_fetcher):
        """Test retry mechanism when all attempts fail"""
        failed_operation = Mock(
            side_effect=PlaywrightError("Persistent error"))
        with pytest.raises(PlaywrightError):
            configured_fetcher._retry(failed_operation)
        assert failed_operation.call_count == configured_fetcher.retry_attempts

    @patch('src.fetchers.base_fetcher.os.path.exists')
    @patch('src.fetchers.base_fetcher.json.dump')
    def test_save_session(self, mock_dump, mock_exists, configured_fetcher,
                          mock_page):
        """Test session saving functionality"""
        mock_exists.return_value = True
        configured_fetcher.page = mock_page
        mock_page.context.storage_state = Mock(return_value={"cookies": []})

        configured_fetcher.save_session()
        mock_dump.assert_called_once()

    def test_sanitize_data(self, configured_fetcher):
        """Test data sanitization"""
        test_data = {
            "key1": " value1 ",
            "key2": "\n\tvalue2\n",
            "key3": None,
            "key4": ["  item1  ", "\nitem2\t"]
        }

        sanitized = configured_fetcher.sanitize_data(test_data)
        assert sanitized["key1"] == "value1"
        assert sanitized["key2"] == "value2"
        assert "key3" not in sanitized
        assert sanitized["key4"] == ["item1", "item2"]

    @patch('src.fetchers.base_fetcher.os.path.exists')
    def test_health_check(self, mock_exists, configured_fetcher, mock_page):
        """Test health check functionality"""
        mock_exists.return_value = True
        configured_fetcher.page = mock_page

        assert configured_fetcher.health_check()

        # Test with no page
        configured_fetcher.page = None
        assert not configured_fetcher.health_check()

    @patch('src.fetchers.base_fetcher.os.makedirs')
    def test_capture_screenshot(self, mock_makedirs, configured_fetcher,
                                mock_page):
        """Test screenshot capture functionality"""
        configured_fetcher.page = mock_page
        configured_fetcher.capture_screenshot("test_error")
        mock_page.screenshot.assert_called_once()
