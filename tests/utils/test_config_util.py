import json
import pytest
from src.utils.config_util import ConfigUtil


@pytest.fixture
def valid_config_file(tmp_path):
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
    config = {
        "logging": {
            "log_dir": "logs",
        },
        "meta": {
            "logging.max_file_size": {
                "type": "int",
                "default": 5242880,
                "min": 1
            }
        }
    }
    config_file = tmp_path / "config_invalid.json"
    with open(config_file, "w") as f:
        json.dump(config, f)
    return config_file


def test_invalid_config(invalid_config_file):
    """
    Test loading an invalid configuration file sets default value from meta.
    """
    config = ConfigUtil.load_config(config_file=str(invalid_config_file))
    assert config["logging"]["max_file_size"] == 5242880  # Default value from meta