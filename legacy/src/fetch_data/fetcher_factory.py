from typing import Dict, Type
from .base_fetcher import BaseFetcher

class FetcherFactory:
    """Factory for creating appropriate fetchers."""

    _fetchers: Dict[str, Type[BaseFetcher]] = {}

    @classmethod
    def register(cls, fetcher_type: str, fetcher_class: Type[BaseFetcher]):
        """Register a fetcher class with a type identifier."""
        cls._fetchers[fetcher_type] = fetcher_class

    @classmethod
    def create(cls, fetcher_type: str, config=None):
        """Create a fetcher of the specified type."""
        if fetcher_type not in cls._fetchers:
            raise ValueError(f"Unknown fetcher type: {fetcher_type}")

        return cls._fetchers[fetcher_type](config)
