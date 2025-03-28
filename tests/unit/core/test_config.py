# tests/unit/core/test_config.py
import pytest
from pathlib import Path
import json
from src.core.config import Config, ConfigurationError, DEFAULT_CONFIG


@pytest.fixture
def temp_env_vars(monkeypatch):
    """Set up temporary environment variables"""
    env_vars = {
        "FACEBOOK_EMAIL": "test@example.com",
        "FACEBOOK_PASSWORD": "secret123",
        "PROXY_USERNAME": "proxy_user",
        "PROXY_PASSWORD": "proxy_pass",
        "APP_ENVIRONMENT": "testing",
        "LOG_LEVEL": "DEBUG",
        "SESSION_VALIDITY_DAYS": "7"  # Add this line
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file"""
    config_file = tmp_path / "config.json"
    test_config = {
        "app": {
            "name": "TestApp",
            "environment": "testing"
        }
    }
    config_file.write_text(json.dumps(test_config))
    return config_file


@pytest.fixture
def config(temp_env_vars):
    """Create a config instance with test environment variables"""
    return Config()


class TestConfigInitialization:
    def test_default_config_loading(self, config):
        """Test that default configuration is loaded correctly"""
        assert config.get("app.name") == "Lemonade"
        assert config.get("app.version") == "1.0.0"
        assert config.get("app.environment") == "testing"

    def test_env_variables_override(self, config, temp_env_vars):
        """Test that environment variables override default config"""
        assert config.get("platforms.facebook.credentials.email") == temp_env_vars["FACEBOOK_EMAIL"]
        assert config.get("platforms.facebook.credentials.password") == temp_env_vars["FACEBOOK_PASSWORD"]
        assert config.get("stealth.proxy.credentials.username") == temp_env_vars["PROXY_USERNAME"]

    def test_custom_config_path(self, temp_config_file):
        """Test loading config from custom path"""
        config = Config(temp_config_file)
        assert config.get("app.name") == "TestApp"


class TestConfigAccess:
    def test_nested_config_access(self, config):
        """Test accessing nested configuration values"""
        assert isinstance(config.get("platforms.facebook.selectors.login"), dict)
        assert config.get("nonexistent.path") is None
        assert config.get("nonexistent.path", "default") == "default"

    def test_config_immutability(self, config):
        """Test that returned config values cannot modify internal state"""
        original = config.get('app')
        config_dict = config.as_dict
        config_dict['app']['name'] = 'Modified'
        assert config.get('app') == original

    def test_as_dict_property(self, config):
        """Test as_dict property returns complete config"""
        config_dict = config.as_dict
        assert isinstance(config_dict, dict)
        assert config_dict["app"]["name"] == config.get("app.name")


class TestConfigValidation:
    def test_validation_session_validity(self):
        """Test validation of session validity days"""
        with pytest.raises(ConfigurationError):
            config = Config()
            config.set("authentication.session_validity_days", 0)

    def test_validation_timeout(self):
        """Test validation of timeout values"""
        with pytest.raises(ConfigurationError):
            config = Config()
            config.set("fetcher.timeout_ms", 0)

    def test_validation_retry_attempts(self):
        """Test validation of retry attempts"""
        with pytest.raises(ConfigurationError):
            config = Config()
            config.set("fetcher.retry.attempts", 0)


class TestConfigModification:
    def test_config_set(self, config):
        """Test setting configuration values"""
        config.set('fetcher.timeout_ms', 90000)
        assert config.get('fetcher.timeout_ms') == 90000

    def test_config_set_with_persist(self, config, tmp_path):
        """Test persisting configuration changes"""
        config.config_path = tmp_path / "test_config.json"
        config.set('fetcher.retry.attempts', 5, persist=True)

        # Load new config instance to verify persistence
        new_config = Config(config.config_path)
        assert new_config.get('fetcher.retry.attempts') == 5

    def test_config_reset(self, config):
        """Test configuration reset functionality"""
        # Test specific path reset
        original_timeout = DEFAULT_CONFIG['fetcher']['timeout_ms']
        config.set('fetcher.timeout_ms', 90000)
        config.reset('fetcher.timeout_ms')
        assert config.get('fetcher.timeout_ms') == original_timeout

        # Test full reset
        config.reset()
        assert config.as_dict == DEFAULT_CONFIG


class TestConfigSecurity:
    def test_safe_export(self, config):
        """Test safe configuration export"""
        safe_config = config.export_safe()
        assert 'password' not in str(safe_config)
        assert '********' in str(safe_config)

        # Check specific sensitive fields
        assert safe_config['platforms']['facebook']['credentials']['password'] == '********'
        assert safe_config['stealth']['proxy']['credentials']['password'] == '********'

    def test_platform_credentials(self, config, temp_env_vars):
        """Test platform credentials retrieval"""
        creds = Config.get_platform_credentials('facebook')
        assert creds['username'] == temp_env_vars['FACEBOOK_EMAIL']
        assert creds['password'] == temp_env_vars['FACEBOOK_PASSWORD']


class TestConfigUtilities:
    def test_platform_validation(self, config):
        """Test platform configuration validation"""
        assert config.validate_platform('facebook')
        assert not config.validate_platform('nonexistent_platform')
        with pytest.raises(ValueError):
            config.validate_platform("")
        with pytest.raises(ValueError):
            config.validate_platform(None)

    def test_config_iteration(self, config):
        """Test configuration iteration"""
        paths = list(config.iter_config())
        assert len(paths) > 0
        assert all(isinstance(path, str) and path for path, _ in paths)

        # Test with prefix
        prefixed_paths = list(config.iter_config("test"))
        assert all(path.startswith("test") for path, _ in prefixed_paths)

    def test_environment_check(self, config):
        """Test environment checking"""
        config.set('app.environment', 'production')
        assert config.is_production
        config.set('app.environment', 'development')
        assert not config.is_production
