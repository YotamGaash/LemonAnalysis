# tests/unit/core/test_constants.py

import pytest
from src.core.constants import *


def test_project_directories():
    """Test that all project directories are properly defined"""
    directories = [
        PROJECT_ROOT,
        CONFIG_DIR,
        LOGS_DIR,
        DATA_DIR,
        OUTPUT_DIR,
        SESSIONS_DIR,
        SCREENSHOTS_DIR,
        CACHE_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        PROXIES_DIR
    ]

    # All paths should be Path objects
    for directory in directories:
        assert isinstance(directory, Path)

    # Test directory hierarchy
    assert SESSIONS_DIR.parent == DATA_DIR
    assert SCREENSHOTS_DIR.parent == DATA_DIR
    assert CACHE_DIR.parent == DATA_DIR


def test_time_constants():
    """Test time constant relationships"""
    assert MINUTE_MS == MS_PER_SECOND * 60
    assert HOUR_MS == MINUTE_MS * 60
    assert DAY_MS == HOUR_MS * 24


def test_auth_method_enum():
    """Test authentication method enum values"""
    assert AuthMethod.CREDENTIAL.value == "credential"
    assert AuthMethod.COOKIE.value == "cookie"
    assert AuthMethod.TOKEN.value == "token"
    assert len(AuthMethod) == 3


def test_log_levels():
    """Test log level enum values"""
    expected_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    actual_levels = {level.value for level in LogLevel}
    assert actual_levels == expected_levels


def test_constraint_values():
    """Test constraint values are within expected ranges"""
    assert MAX_SESSION_AGE_DAYS > MIN_SESSION_AGE_DAYS
    assert MIN_TIMEOUT_MS > 0
    assert MIN_RETRY_ATTEMPTS > 0
    assert MAX_LOG_FILE_SIZE > 0


def test_file_names():
    """Test file name constants"""
    assert COOKIES_FILENAME.endswith('.json')
    assert STORAGE_STATE_FILENAME.endswith('.json')
    assert '{timestamp}' in LOG_FILE_PATTERN


def test_default_viewport():
    """Test viewport configuration"""
    assert all(key in DEFAULT_VIEWPORT for key in ['width', 'height'])
    assert all(isinstance(value, int) for value in DEFAULT_VIEWPORT.values())
    assert all(value > 0 for value in DEFAULT_VIEWPORT.values())
