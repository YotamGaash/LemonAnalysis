# tests/utils/test_config_util.py
import json
import os
import pytest
from legacy.src.utils.config_util import ConfigUtil


@pytest.fixture
def valid_main_config(tmp_path):
    """Create a valid main configuration file"""
    config = {
        "logging": {
            "log_dir": "logs",
            "log_file_name": "app.log",
            "max_file_size": 5242880,
            "backup_count": 3,
            "log_level_console": "DEBUG",
            "log_level_file": "INFO"
        },
        "storage_paths": {
            "sessions_path": "data/sessions",
            "screenshots_path": "data/screenshots",
            "cache_path": "data/caches",
            "proxies_path": "data/proxies",
            "raw_data_path": "data/raw",
            "processed_data_path": "data/processed"
        },
        "meta": {
            "logging.log_dir": {
                "type": "str",
                "default": "logs"
            },
            "logging.backup_count": {
                "type": "int",
                "default": 3,
                "min": 0
            }
        }
    }
    config_file = tmp_path / "app_config.json"
    with open(config_file, "w", encoding='utf-8') as f:
        json.dump(config, f)
    return config_file


@pytest.fixture
def valid_fetcher_config(tmp_path):
    """Create a valid fetcher configuration file"""
    config = {
        "fetcher": {
            "timeout": 30,
            "max_retries": 3
        }
    }
    config_file = tmp_path / "fetcher_config.json"
    with open(config_file, "w", encoding='utf-8') as f:
        json.dump(config, f)
    return config_file


@pytest.fixture
def config_util(valid_main_config, valid_fetcher_config):
    """Create a ConfigUtil instance with valid configurations"""
    ConfigUtil._instance = None
    instance = ConfigUtil(
        main_config=str(valid_main_config),
        fetcher_config=str(valid_fetcher_config)
    )
    yield instance
    ConfigUtil._instance = None


@pytest.fixture(autouse=True)
def cleanup_config():
    """Cleanup ConfigUtil singleton after each test"""
    yield
    ConfigUtil._instance = None


def test_singleton_pattern(valid_main_config, valid_fetcher_config):
    """Test that ConfigUtil maintains singleton pattern"""
    config1 = ConfigUtil(main_config=str(valid_main_config),
                         fetcher_config=str(valid_fetcher_config))
    config2 = ConfigUtil()
    assert config1 is config2


def test_config_loading(config_util):
    """Test basic configuration loading"""
    assert config_util.get("logging.log_dir") == "logs"
    assert config_util.get("logging.log_file_name") == "app.log"


def test_storage_path_properties(config_util):
    """Test all storage path properties"""
    assert config_util.session_path == "data/sessions"
    assert config_util.screenshots_path == "data/screenshots"
    assert config_util.cache_path == "data/caches"
    assert config_util.proxies_path == "data/proxies"
    assert config_util.raw_data_path == "data/raw"
    assert config_util.processed_data_path == "data/processed"


def test_environment_variable_override(config_util, monkeypatch):
    """Test environment variable overrides configuration"""
    monkeypatch.setenv("LOGGING_LOG_DIR", "/custom/log/path")
    assert config_util.get("logging.log_dir") == "/custom/log/path"


def test_meta_default_values(config_util):
    """Test meta default values are used when config value is missing"""
    assert config_util.get("logging.nonexistent") is None
    assert config_util.get("logging.backup_count") == 3

def test_invalid_config_file():
    """Test handling of invalid configuration file"""
    # Create an invalid JSON file
    config_path = "test_invalid.json"
    try:
        with open(config_path, "w", encoding='utf-8') as f:
            f.write("{invalid json")

        # Test invalid JSON format
        ConfigUtil._instance = None
        with pytest.raises(ValueError, match="Invalid JSON format"):
            ConfigUtil(main_config=config_path)

        # Test missing files - should not raise error but use defaults
        ConfigUtil._instance = None
        config = ConfigUtil(main_config="nonexistent.json")
        assert config.get("storage_paths.sessions_path") == "data/sessions"

        # Test default paths are created when config is missing
        assert config.session_path == "data/sessions"
        assert config.screenshots_path == "data/screenshots"
        assert config.cache_path == "data/caches"

    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.remove(config_path)

def test_json_decode_error(tmp_path):
    """Test handling of invalid JSON"""
    invalid_json = tmp_path / "invalid.json"
    with open(invalid_json, "w", encoding='utf-8') as f:
        f.write("{invalid json syntax")

    fetcher_config = tmp_path / "fetcher_config.json"
    with open(fetcher_config, "w", encoding='utf-8') as f:
        json.dump({"fetcher": {}}, f)

    ConfigUtil._instance = None

    with pytest.raises(ValueError, match="Invalid JSON format"):
        ConfigUtil(
            main_config=str(invalid_json),
            fetcher_config=str(fetcher_config)
        )


@pytest.mark.parametrize("path_property", [
    "session_path",
    "screenshots_path",
    "cache_path",
    "proxies_path",
    "raw_data_path",
    "processed_data_path"
])
def test_default_storage_paths(path_property):
    """Test default values for storage paths when config is missing"""
    ConfigUtil._instance = None
    config = ConfigUtil()
    path_value = getattr(config, path_property)
    assert isinstance(path_value, str)
    assert "data" in path_value


def test_fetcher_config_access(config_util):
    """Test accessing fetcher-specific configuration"""
    assert config_util.get_fetcher("fetcher.timeout") == 30
    assert config_util.get_fetcher("fetcher.max_retries") == 3
    assert config_util.get_fetcher("fetcher.nonexistent", "default") == "default"


def test_nonexistent_value_with_default(config_util):
    """Test getting nonexistent value with provided default"""
    default_value = "default_value"
    assert config_util.get("nonexistent.key", default_value) == default_value


def test_nested_config_access(config_util):
    """Test accessing deeply nested configuration values"""
    assert isinstance(config_util.get("storage_paths"), dict)
    assert config_util.get("storage_paths.sessions_path") == "data/sessions"
