import json
import pytest
from src.utils.config_util import ConfigUtil


@pytest.fixture
def valid_config_file(tmp_path):
    """
    Provide a temporary valid configuration file for testing.
    """
    config = {
        "logging": {
            "log_dir": "logs",
            "log_file_name": "app.log",
            "max_file_size": 5242880,
            "backup_count": 3,
            "log_level_console": "DEBUG",
            "log_level_file": "INFO",
            "log_format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
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
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)
    return config_file


@pytest.fixture
def invalid_config_file(tmp_path):
    """
    Provide a temporary invalid configuration file for testing.
    """
    config = {
        "logging": {
            "log_dir": "logs"
        },
        "meta": {}
    }
    config_file = tmp_path / "config_invalid.json"
    with open(config_file, "w") as f:
        json.dump(config, f)
    return config_file

def test_valid_config(valid_config_file):
    """
    Test loading a valid configuration file.
    """
    config_util = ConfigUtil(main_config=str(valid_config_file))
    assert config_util.get("logging.log_dir") == "logs"
    assert config_util.get("logging.log_file_name") == "app.log"


def test_invalid_config(invalid_config_file):
    """
    Test loading an invalid configuration file sets default value from meta.
    """
    config_util = ConfigUtil(main_config=str(invalid_config_file))
    assert config_util.get("logging.max_file_size",
                           5242880) == 5242880  # Default
