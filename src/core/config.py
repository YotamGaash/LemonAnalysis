# src/core/config.py
import copy
from pathlib import Path
from typing import Dict, Any, Optional, Iterator, Tuple
import json
import os
from dotenv import load_dotenv
from .constants import *


class ConfigurationError(Exception):
    """Raised when there's an error in configuration"""
    pass


DEFAULT_CONFIG = {
    "app": {
        "name": "Lemonade",
        "version": "1.0.0",
        "environment": "development"
    },
    "logging": {
        "log_dir": LOGS_DIR,
        "log_file_name": DEFAULT_LOGFILE_NAME,
        "max_file_size": DEFAULT_MAX_FILE_SIZE,  # 5MB
        "backup_count": DEFAULT_BACKUP_COUNT,
        "console_level": "DEBUG",
        "file_level": "INFO"
    },
    "storage": {
        "base_dir": "data",
        "sessions": "sessions",
        "screenshots": "screenshots",
        "cache": "cache",
        "raw_data": "raw",
        "processed_data": "processed",
        "proxies": "proxies"
    },
    "fetcher": {
        "default_platform": "facebook",
        "timeout_ms": 60000,
        "stealth_mode": True,
        "screenshot_on_error": True,
        "retry": {
            "attempts": 3,
            "delay_ms": 5000
        }
    },
    "authentication": {
        "method": AuthMethod.CREDENTIAL.value,
        "session_validity_days": 7,
        "auto_renew_session": True
    },
    "stealth": {
        "user_agent_rotation": True,
        "fingerprint_spoofing": True,
        "proxy": {
            "enabled": False,
            "rotation_interval_seconds": 600
        },
        "human_behavior": {
            "enabled": True,
            "delay_ms": {
                "min": 500,
                "max": 3000
            }
        }
    },
    "platforms": {
        "facebook": {
            "base_url": "https://facebook.com",
            "login_url": "https://facebook.com/login",
            "selectors": {
                "login": {
                    "email_field": "#email",
                    "password_field": "#pass",
                    "login_button": "[data-testid='royal_login_button']",
                    "error_box": "#error_box",
                    "logged_in_indicator": "[data-testid='bookmark_nav']"
                }
            },
            "timeouts": {
                "login_ms": 30000,
                "checkpoint_ms": 20000,
                "verification_ms": 15000,
                "action_ms": 10000
            },
            "session": {
                "storage_path": "facebook",
                "max_age_days": 7
            },
            "rate_limits": {
                "requests_per_hour": 100,
                "delay_between_requests_ms": 1000
            }
        }
    }
}


class Config:
    """Configuration manager for the application"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path: Path = config_path or PROJECT_ROOT / "config" / "config.json"
        self._config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self._load_env()
        self._load_config()
        self._validate_config()

    def _load_env(self) -> None:
        """Load environment variables from .env file"""
        load_dotenv(PROJECT_ROOT / ".env")

        # Map environment variables to config
        env_mappings = {
            "FACEBOOK_EMAIL": ("platforms.facebook.credentials.email", str),
            "FACEBOOK_PASSWORD": ("platforms.facebook.credentials.password", str),
            "PROXY_USERNAME": ("stealth.proxy.credentials.username", str),
            "PROXY_PASSWORD": ("stealth.proxy.credentials.password", str),
            "APP_ENVIRONMENT": ("app.environment", str),
            "LOG_LEVEL": ("logging.console_level", str),
            "SESSION_VALIDITY_DAYS": ("authentication.session_validity_days", int)  # Add this line
        }

        for env_var, (config_path, type_cast) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    self._set_nested_value(config_path, type_cast(value))
                except ValueError:
                    # Skip invalid type conversions
                    continue

    def _load_config(self) -> None:
        """Load configuration from JSON file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                file_config = json.load(f)
                self._merge_configs(self._config, file_config)

    def _merge_configs(self, base: Dict, update: Dict) -> None:
        """Recursively merge two configuration dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value

    def _set_nested_value(self, path: str, value: Any) -> None:
        """Set a value in nested dictionary using dot notation"""
        current = self._config
        *parts, last = path.split('.')

        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[last] = value

    def _validate_config(self) -> None:
        """Validate configuration values"""
        validations = [
            (
                MIN_SESSION_AGE_DAYS <= self._config["authentication"]["session_validity_days"] <= MAX_SESSION_AGE_DAYS,
                f"Session validity days must be between {MIN_SESSION_AGE_DAYS} and {MAX_SESSION_AGE_DAYS}"
            ),
            (
                self._config["fetcher"]["timeout_ms"] >= MIN_TIMEOUT_MS,
                f"Fetcher timeout must be at least {MIN_TIMEOUT_MS}ms"
            ),
            (
                self._config["fetcher"]["retry"]["attempts"] > 0,
                "Retry attempts must be positive"
            )
        ]

        for condition, message in validations:
            if not condition:
                raise ConfigurationError(message)

    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        current = self._config
        for part in path.split('.'):
            if isinstance(current, dict):
                current = current.get(part, default)
            else:
                return default
        return current

    def set(self, path: str, value: Any, persist: bool = False) -> None:
        """
        Set a configuration value using dot notation
        Args:
            path: Configuration path in dot notation (e.g., 'fetcher.timeout_ms')
            value: Value to set
            persist: If True, saves the change to config file
        """
        self._set_nested_value(path, value)
        self._validate_config()  # Validate after change
        if persist:
            self.save()


    def reset(self, path: Optional[str] = None) -> None:
        """
        Reset configuration to defaults
        Args:
            path: Optional path to reset specific section, resets all if None
        """
        if path is None:
            self._config = copy.deepcopy(DEFAULT_CONFIG)
        else:
            current = DEFAULT_CONFIG
            for part in path.split('.'):
                current = current[part]
            self._set_nested_value(path, copy.deepcopy(current))
        self._load_env()  # Reapply environment variables
        self._validate_config()

    def save(self) -> None:
        """Save current configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)

    def export_safe(self) -> Dict[str, Any]:
        """
        Export configuration with sensitive data masked
        Returns:
            Configuration dictionary with sensitive values masked
        """

        def _mask_sensitive(d: Dict) -> Dict:
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = _mask_sensitive(v)
                else:
                    sensitive_terms = {'password', 'token', 'secret', 'key', 'credential'}
                    result[k] = '********' if any(term in k.lower() for term in sensitive_terms) else v
            return result

        return _mask_sensitive(copy.deepcopy(self._config))

    def iter_config(self, prefix: str = "") -> Iterator[Tuple[str, Any]]:
        """
        Iterate over configuration items with their full paths
        Args:
            prefix: Starting prefix for paths
        Yields:
            Tuples of (path, value)
        """

        def _iterate(d: Dict, current_prefix: str) -> Iterator[Tuple[str, Any]]:
            for key, value in d.items():
                path = f"{current_prefix}.{key}" if current_prefix else key
                if isinstance(value, dict):
                    yield from _iterate(value, path)
                else:
                    yield path, value

        yield from _iterate(self._config, prefix)

    @staticmethod
    def get_platform_credentials(platform: str) -> Dict[str, str]:
        """
        Safely retrieve platform credentials from environment
        Args:
            platform: Platform name (e.g., 'facebook', 'Twitter')
        Returns:
            Dictionary with username/email and password
        """
        platform = platform.upper()
        return {
            "username": os.getenv(f"{platform}_USERNAME") or os.getenv(f"{platform}_EMAIL"),
            "password": os.getenv(f"{platform}_PASSWORD")
        }

    def validate_platform(self, platform: str) -> bool:
        """
        Validate if platform is properly configured
        Args:
            platform: Platform name to validate
        Returns:
            True if platform is properly configured
        Raises:
            ValueError: If platform name is empty or None
        """
        if not platform:
            raise ValueError("Platform name cannot be empty")

        if not self.get(f"platforms.{platform}"):
            return False

        credentials = self.get_platform_credentials(platform)
        return bool(credentials['username'] and credentials['password'])

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.get('app.environment', '').lower() == 'production'

    @property
    def as_dict(self) -> Dict[str, Any]:
        """
        Return complete configuration as dictionary
        Returns:
        Deep copy of the configuration dictionary
        """
        return self._config.copy()
