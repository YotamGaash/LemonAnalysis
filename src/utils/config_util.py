import json
import os


class ConfigUtil:
    """
    Utility class for loading, validating, and accessing configuration constants from a JSON file.
    """
    _config = None  # Class attribute to hold the loaded configuration

    @classmethod
    def load_config(cls, config_file="config/config.json"):
        """
        Load the configuration file, validate its values using the 'meta' section,
        and store them in memory.

        Args:
            config_file (str): Path to the JSON configuration file.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not a valid JSON format.
            ValueError: If required keys are missing or invalid.
        """
        if cls._config is None:
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"Configuration file not found: {config_file}")

            # Load configuration
            with open(config_file, "r") as file:
                config = json.load(file)

            # Validate and normalize configuration
            if "meta" not in config:
                raise ValueError("The configuration file must contain a 'meta' section for validation rules.")

            cls._validate_and_normalize(config)
            cls._config = config
        return cls._config

    @classmethod
    def get(cls, key):
        """
        Get a configuration value by key. Supports nested keys (e.g., "logging.log_dir").

        Args:
            key (str): Dot-separated key to the configuration value.

        Returns:
            Value from the configuration if found, or the default value from `meta`.

        Raises:
            KeyError: If the `key` is not in the configuration and no default exists in `meta`.
        """
        if cls._config is None:
            cls.load_config()  # Ensure configuration is loaded

        keys = key.split(".")
        value = cls._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Check the meta section for a default value
                meta_default = cls._config["meta"].get(key, {}).get("default")
                if meta_default is not None:
                    return meta_default
                else:
                    raise KeyError(f"Key '{key}' not found in configuration and no default is defined in 'meta'.")
        return value

    @classmethod
    def reload_config(cls, config_file="config/config.json"):
        """
        Force reload the configuration file.

        Args:
            config_file (str): Path to the JSON configuration file.
        """
        cls._config = None
        cls.load_config(config_file)

    @staticmethod
    def _validate_and_normalize(config):
        """
        Validate and normalize configuration values based on the 'meta' section of the JSON file.

        Args:
            config (dict): The configuration dictionary.

        Raises:
            KeyError: If a required key is missing.
            ValueError: If keys are invalid based on meta validation rules.
        """
        meta = config.get("meta", {})

        for full_key, rules in meta.items():
            # Traverse and validate nested keys
            keys = full_key.split(".")
            value = config
            for k in keys[:-1]:
                value = value.setdefault(k, {})
            last_key = keys[-1]

            # Check if key is present
            if last_key not in value:
                default = rules.get("default")
                if default is not None:
                    value[last_key] = default
                else:
                    raise KeyError(f"Required key '{full_key}' is missing and has no defined default in meta.")

            # Validate value type
            val = value[last_key]
            expected_type = rules.get("type")
            if expected_type and not isinstance(val, eval(expected_type)):
                raise ValueError(f"Key '{full_key}' must be of type {expected_type}, got {type(val)} instead.")

            # Validate additional rules
            if "min" in rules and isinstance(val, (int, float)) and val < rules["min"]:
                raise ValueError(f"Key '{full_key}' must be >= {rules['min']}. Current value: {val}")
            if "max" in rules and isinstance(val, (int, float)) and val > rules["max"]:
                raise ValueError(f"Key '{full_key}' must be <= {rules['max']}. Current value: {val}")
            if "choices" in rules and isinstance(val, str) and val not in rules["choices"]:
                raise ValueError(f"Key '{full_key}' must be one of {rules['choices']}. Current value: {val}")
