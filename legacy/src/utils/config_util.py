# src/utils/config_util.py
import json
import os
from typing import Any, Optional
from pathlib import Path


class ConfigUtil:
    _instance = None
    _config = {}
    _fetcher_config = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigUtil, cls).__new__(cls)
        return cls._instance

    def __init__(self, main_config: Optional[str] = None, fetcher_config: Optional[str] = None):
        if hasattr(self, '_initialized'):
            return

        try:
            self._load_configurations(main_config, fetcher_config)
            self._initialized = True
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in configuration file")
        except (PermissionError, OSError):
            raise ValueError("Unable to access configuration file")
        except Exception as e:
            raise ValueError(f"Configuration initialization failed: {str(e)}")

    def _load_configurations(self, main_config: Optional[str], fetcher_config: Optional[str]) -> None:
        """Load both main and fetcher configurations"""
        # Load main config
        try:
            if main_config and os.path.exists(main_config):
                with open(main_config, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                self._handle_missing_config(main_config or "app_config.json")
        except (PermissionError, OSError):
            raise ValueError("Unable to access configuration file")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in main configuration file")

        # Load fetcher config
        try:
            if fetcher_config and os.path.exists(fetcher_config):
                with open(fetcher_config, 'r', encoding='utf-8') as f:
                    self._fetcher_config = json.load(f)
            else:
                self._fetcher_config = {"fetcher": {}}
        except (PermissionError, OSError):
            raise ValueError("Unable to access configuration file")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in fetcher configuration file")

    @staticmethod
    def _get_from_env(key: str) -> Optional[str]:
        """Get value from environment variables"""
        env_key = key.upper().replace('.', '_')
        return os.getenv(env_key)

    def get(self, key: str, default=None) -> Any:

        # Handle case when key is actually a dict (for backward compatibility)
        if isinstance(key, dict):
            return key

        env_value = self._get_from_env(key)
        if env_value is not None:
            return env_value

        parts = key.split(".")
        target = self._config

        # Navigate through config
        for part in parts:
            if isinstance(target, dict) and part in target:
                target = target[part]
            else:
                # Check meta for default
                meta_key = ".".join(parts)
                if "meta" in self._config and meta_key in self._config["meta"]:
                    return self._config["meta"][meta_key].get("default", default)
                return default
        return target

    def get_fetcher(self, key: str, default=None) -> Any:
        """Get configuration value from fetcher config"""
        parts = key.split(".")
        target = self._fetcher_config
        for part in parts:
            if isinstance(target, dict) and part in target:
                target = target[part]
            else:
                return default
        return target

    def _handle_missing_config(self, file_path: str) -> None:
        """Handle missing configuration file by creating default configuration"""
        default_config = {
            "logging": {"log_dir": "logs"},
            "storage_paths": {
                "sessions_path": "data/sessions",
                "screenshots_path": "data/screenshots",
                "cache_path": "data/caches",
                "proxies_path": "data/proxies",
                "raw_data_path": "data/raw",
                "processed_data_path": "data/processed"
            }
        }
        self._config = default_config

    @property
    def session_path(self) -> str:
        return self.get("storage_paths.sessions_path", "data/sessions")

    @property
    def screenshots_path(self) -> str:
        return self.get("storage_paths.screenshots_path", "data/screenshots")

    @property
    def cache_path(self) -> str:
        return self.get("storage_paths.cache_path", "data/caches")

    @property
    def proxies_path(self) -> str:
        return self.get("storage_paths.proxies_path", "data/proxies")

    @property
    def raw_data_path(self) -> str:
        return self.get("storage_paths.raw_data_path", "data/raw")

    @property
    def processed_data_path(self) -> str:
        return self.get("storage_paths.processed_data_path", "data/processed")
