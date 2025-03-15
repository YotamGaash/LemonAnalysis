"""
Custom exceptions used in the fetcher module.
"""


class FetcherError(Exception):
    """Base class for all fetcher-related exceptions."""
    pass


class InitializationError(FetcherError):
    """Raised when there's an error initializing a component."""
    pass


class ConfigurationError(FetcherError):
    """Raised when there's an error with configuration."""
    pass


class FetchingError(FetcherError):
    """Raised when there's an error fetching data."""
    pass


class ExtractionError(FetcherError):
    """Raised when there's an error extracting data."""
    pass


class AuthenticationError(FetcherError):
    """Raised when there's an error with authentication."""
    pass


class ScrollingError(FetcherError):
    """Raised when there's an error with page scrolling."""
    pass


class StealthError(FetcherError):
    """Raised when there's an error with stealth measures."""
    pass


class FetchError(FetcherError):
    """Raised for all fetch errors."""
    pass


class SessionError(FetcherError):
    """Raised for all session errors."""
    pass

class PlaywrightError(FetcherError):
    """Raised for all playwright errors."""
    pass