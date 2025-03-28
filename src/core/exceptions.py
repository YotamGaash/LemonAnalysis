# src/core/exceptions.py

class FetcherException(Exception):
    """Base exception for all fetcher-related errors."""

    def __init__(self, message: str = "", details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# Configuration and Initialization
class ConfigurationException(FetcherException):
    """Raised when there's an error with configuration."""
    pass


class InitializationException(FetcherException):
    """Raised when there's an error initializing a component."""
    pass


# Browser and Network
class BrowserException(FetcherException):
    """Base class for browser-related exceptions."""
    pass


class PlaywrightException(BrowserException):
    """Raised for all playwright-specific errors."""
    pass


class SessionException(BrowserException):
    """Raised for all session-related errors."""
    pass


class NetworkException(BrowserException):
    """Raised for network-related errors."""
    pass


# Data Operations
class DataException(FetcherException):
    """Base class for data-related exceptions."""
    pass


class FetchException(DataException):
    """Raised when there's an error fetching data."""
    pass


class ExtractionException(DataException):
    """Raised when there's an error extracting data."""
    pass


class ValidationException(DataException):
    """Raised when there's an error validating data."""
    pass


# Strategy-specific
class StrategyException(FetcherException):
    """Base class for strategy-related exceptions."""
    pass


class AuthenticationException(StrategyException):
    """Raised when there's an error with authentication."""
    pass


class ScrollingException(StrategyException):
    """Raised when there's an error with page scrolling."""
    pass


class StealthException(StrategyException):
    """Raised when there's an error with stealth measures."""
    pass
