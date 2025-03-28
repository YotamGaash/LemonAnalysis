# src/core/exceptions.py

class ScraperException(Exception):
    """Base exception for all scraper-related errors."""

    def __init__(self, message: str = "", details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class BrowserException(ScraperException):
    """Exceptions related to browser operations."""
    pass


class AuthenticationException(ScraperException):
    """Exceptions related to authentication process."""
    pass


class NetworkException(ScraperException):
    """Exceptions related to network operations."""
    pass


class DataExtractionException(ScraperException):
    """Exceptions related to data extraction process."""
    pass


class ValidationException(ScraperException):
    """Exceptions related to data validation."""
    pass
