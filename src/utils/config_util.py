import json
from typing import Any, Dict


class ConfigUtil:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigUtil, cls).__new__(cls)
        return cls._instance

    def __init__(self, main_config="config/config.json",
                 fetcher_config="config/fetcher_config.json"):
        if not hasattr(self, "_initialized"):  # Prevent reinitialization
            self.main_config = main_config
            self.fetcher_config = fetcher_config
            self._config: Dict[str, Any] = {}
            self._fetcher_config: Dict[str, Any] = {}
            self.load_config()
            self._initialized = True

    def load_config(self):
        with open(self.main_config, "r") as f:
            self._config = json.load(f)
        with open(self.fetcher_config, "r") as f:
            self._fetcher_config = json.load(f)

    def get(self, key: str, default=None):
        parts = key.split(".")
        target = self._config
        for part in parts:
            if isinstance(target, dict) and part in target:
                target = target[part]
            else:
                return default
        return target

    def get_fetcher(self, key: str, default=None):
        parts = key.split(".")
        target = self._fetcher_config
        for part in parts[:-1]:
            target = target.get(part, {})
        return target.get(parts[-1], default)

    @property
    def session_path(self):
        return self.get('storage_paths.sessions_path', 'data/sessions')

    @property
    def screenshots_path(self):
        return self.get('storage_paths.screenshots_path', 'data/screenshots')

    @property
    def cache_path(self):
        return self.get('storage_paths.cache_path', 'data/caches')

    @property
    def proxies_path(self):
        return self.get('storage_paths.proxies_path', 'data/proxies')

    @property
    def raw_data_path(self):
        return self.get('storage_paths.raw_data_path', 'data/raw')

    @property
    def processed_data_path(self):
        return self.get('storage_paths.processed_data_path', 'data/processed')
