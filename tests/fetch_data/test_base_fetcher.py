import pytest
from unittest.mock import MagicMock, patch
from playwright.sync_api import Page

from src.fetch_data.base_fetcher import BaseFetcher
from src.fetch_data.exceptions import FetcherError


# Sample concrete implementation for testing
class TestFetcher(BaseFetcher):
    def initialize(self, page):
        super().initialize(page)

    def fetch(self, query, **kwargs):
        if not self.is_initialized:
            raise RuntimeError("Not initialized")
        return {"query": query, "data": "test data"}

    def extract(self, element):
        return {"text": "Extracted data"}


class TestBaseFetcher:

    @pytest.fixture
    def mock_page(self):
        return MagicMock(spec=Page)

    @pytest.fixture
    def fetcher(self):
        with patch('src.fetch_data.base_fetcher.ConfigUtil') as mock_config:
            # Mock config returns
            mock_config.get.return_value = {
                "fetcher": {"timeout": 30000, "default_platform": "test"},
                "platforms": {"test": {"base_url": "https://test.com"}},
                "constants": {"retrieval_attempts": 3}
            }
            return TestFetcher()

    def test_initialization(self, fetcher, mock_page):
        # Test initialization process
        fetcher.initialize(mock_page)
        assert fetcher.is_initialized
        assert fetcher.page == mock_page

    def test_fetch_requires_initialization(self, fetcher):
        # Test that fetch requires initialization
        with pytest.raises(RuntimeError):
            fetcher.fetch("test")

    def test_context_manager(self, fetcher, mock_page):
        # Test context manager
        fetcher.initialize(mock_page)
        with fetcher as f:
            assert f is fetcher
            assert f.is_initialized

        # After context exit, resources should be cleaned up
        assert not fetcher.is_initialized
        assert fetcher.page is None
        mock_page.close.assert_called_once()

    def test_custom_config(self):
        # Test with custom config
        custom_config = {"timeout": 5000, "platform": "custom"}
        with patch('src.fetch_data.base_fetcher.ConfigUtil'):
            fetcher = TestFetcher(custom_config)
            assert fetcher.timeout == 5000
            assert fetcher.platform == "custom"
