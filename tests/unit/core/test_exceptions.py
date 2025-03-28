# tests/core/test_exceptions.py

import pytest
from src.core.exceptions import *


def test_base_exception_functionality():
    """Test FetcherException basic functionality."""
    details = {"url": "https://example.com", "error_code": 404}
    exc = FetcherException("Test message", details)
    assert exc.message == "Test message"
    assert exc.details == details
    assert str(exc) == "Test message"


def test_exception_inheritance():
    """Test the exception inheritance hierarchy."""
    hierarchies = {
        BrowserException: [
            PlaywrightException,
            SessionException,
            NetworkException
        ],
        DataException: [
            FetchException,
            ExtractionException,
            ValidationException
        ],
        StrategyException: [
            AuthenticationException,
            ScrollingException,
            StealthException
        ]
    }

    # Test that all base classes inherit from FetcherException
    for base_class in hierarchies.keys():
        assert issubclass(base_class, FetcherException)

        # Test that all subclasses inherit from their base class
        for sub_class in hierarchies[base_class]:
            assert issubclass(sub_class, base_class)
            assert issubclass(sub_class, FetcherException)


def test_all_exceptions_instantiation():
    """Test that all exceptions maintain the FetcherException functionality."""
    exceptions = [
        FetcherException, ConfigurationException, InitializationException,
        BrowserException, PlaywrightException, SessionException, NetworkException,
        DataException, FetchException, ExtractionException, ValidationException,
        StrategyException, AuthenticationException, ScrollingException, StealthException
    ]

    test_message = "Test message"
    test_details = {"key": "value"}

    for exception_class in exceptions:
        # Test with both message and details
        exc = exception_class(test_message, test_details)
        assert exc.message == test_message
        assert exc.details == test_details

        # Test with message only
        exc = exception_class(test_message)
        assert exc.message == test_message
        assert exc.details == {}

        # Test with no arguments
        exc = exception_class()
        assert exc.message == ""
        assert exc.details == {}
