# src/core/constants.py
from enum import Enum, auto
from pathlib import Path
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
# Project Paths and Directories
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Data subdirectories
SESSIONS_DIR = DATA_DIR / "sessions"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
CACHE_DIR = DATA_DIR / "caches"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PROXIES_DIR = DATA_DIR / "proxies"


class BrowserType(Enum):
    """Supported browser types"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class FetchStatus(Enum):
    """Status codes for fetch operations"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INVALID = "invalid"
    RETRY = "retry"


class AuthMethod(Enum):
    """Authentication methods"""
    CREDENTIAL = "credential"
    COOKIE = "cookie"
    TOKEN = "token"


# Time constants (in milliseconds)
MS_PER_SECOND = 1000
MINUTE_MS = MS_PER_SECOND * 60
HOUR_MS = MINUTE_MS * 60
DAY_MS = HOUR_MS * 24

# File patterns and names
CONFIG_FILE_PATTERN = "*.json"
LOG_FILE_PATTERN = "fetcher_{timestamp}.log"
COOKIES_FILENAME = "cookies.json"
STORAGE_STATE_FILENAME = "storage.json"

# Browser configuration
DEFAULT_VIEWPORT = {
    "width": 1920,
    "height": 1080
}

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# HTTP related
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Logging defaults
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
DEFAULT_BACKUP_COUNT = 3
DEFAULT_LOGFILE_NAME = "log.app"

LOG_LEVELS = {
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARNING": WARNING,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL
}


# Limits and constraints
MAX_SESSION_AGE_DAYS = 30
MIN_SESSION_AGE_DAYS = 1
MIN_TIMEOUT_MS = 1000
MIN_RETRY_ATTEMPTS = 1
MAX_LOG_FILE_SIZE = 5 * 1024 * 1024  # 5MB
