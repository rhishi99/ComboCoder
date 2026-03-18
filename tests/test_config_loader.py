"""Tests for config_loader module."""
import os
import pytest
from pathlib import Path
from freeagentdev.core.config_loader import ConfigLoader


class TestConfigLoader:
    """Test suite for ConfigLoader."""

    @pytest.fixture
    def test_config_path(self, tmp_path):
        """Create a test config file."""
        config_content = """
providers:
  test_provider:
    api_key_env: "TEST_API_KEY"
    api_key: "direct_test_key_123"
    base_url: "https://test.api.com/v1"
    models:
      planner: "test/model-1"
      engineer: "test/model-2"

  env_only_provider:
    api_key_env: "ENV_ONLY_KEY"
    base_url: null
    models:
      planner: "env/model"

  direct_key_provider:
    api_key: "my_direct_key_456"
    base_url: "https://direct.api.com/v1"
    models:
      planner: "direct/model"

  # Simulate real providers with direct keys (like in config.yaml)
  groq_simulator:
    api_key_env: "gsk_testkey123456"
    base_url: null
    models:
      planner: "groq/model"

  nvidia_simulator:
    api_key_env: "nvapi-testkey123"
    base_url: "https://test.api.nvidia.com"
    models:
      planner: "nvidia/model"

provider_order:
  - test_provider
  - env_only_provider
  - direct_key_provider
  - groq_simulator
  - nvidia_simulator

llm:
  temperature: 0.3
  max_tokens: 4096
  timeout_seconds: 60

agents:
  max_turns: 5
  retry_on_failure: true

rate_limit:
  cooldown_seconds: 30
  max_wait_seconds: 120
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(config_content)
        return config_file

    def test_load_config_from_file(self, test_config_path):
        """Test loading configuration from a YAML file."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        config = loader.load(test_config_path)

        assert config is not None
        assert "providers" in config
        assert "test_provider" in config["providers"]

    def test_get_provider_config(self, test_config_path):
        """Test retrieving provider configuration."""
        # Reset singleton for fresh test
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        loader.load(test_config_path)

        provider_config = loader.get_provider_config("test_provider")
        assert provider_config is not None
        assert provider_config["base_url"] == "https://test.api.com/v1"

    def test_is_provider_configured_with_env_var(self, test_config_path):
        """Test provider configured check with environment variable."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        # Clear any existing env vars
        for key in ["TEST_API_KEY", "ENV_ONLY_KEY"]:
            if key in os.environ:
                del os.environ[key]

        # Set the environment variable
        os.environ["TEST_API_KEY"] = "env_key_value"
        os.environ["ENV_ONLY_KEY"] = "env_only_value"

        try:
            loader = ConfigLoader()
            loader.load(test_config_path)

            # Provider should be configured via env var
            assert loader.is_provider_configured("test_provider") is True
            assert loader.is_provider_configured("env_only_provider") is True

            # Clean up
            del os.environ["TEST_API_KEY"]
            del os.environ["ENV_ONLY_KEY"]
        finally:
            ConfigLoader._instance = None
            ConfigLoader._config = None

    def test_is_provider_configured_with_direct_key(self, test_config_path):
        """Test provider configured check with direct API key."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        loader.load(test_config_path)

        # Should detect direct API key
        assert loader.is_provider_configured("direct_key_provider") is True

    def test_is_provider_configured_with_key_prefix(self, test_config_path):
        """Test provider configured with keys that have known prefixes."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        loader.load(test_config_path)

        # Should detect keys with known prefixes (gsk_, nvapi-, sk-or-)
        assert loader.is_provider_configured("groq_simulator") is True
        assert loader.is_provider_configured("nvidia_simulator") is True

    def test_get_api_key_from_env_var(self, test_config_path):
        """Test retrieving API key from environment variable."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        os.environ["TEST_API_KEY"] = "env_key_value"

        try:
            loader = ConfigLoader()
            loader.load(test_config_path)

            # test_provider has both api_key and api_key_env
            # api_key should take priority
            api_key = loader.get_api_key("test_provider")
            assert api_key == "direct_test_key_123"  # api_key has priority

            # env_only_provider should get from env var
            api_key = loader.get_api_key("env_only_provider")
            assert api_key == "env_key_value"
        finally:
            if "TEST_API_KEY" in os.environ:
                del os.environ["TEST_API_KEY"]
            ConfigLoader._instance = None
            ConfigLoader._config = None

    def test_get_api_key_from_direct_value(self, test_config_path):
        """Test retrieving direct API key from config."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        loader.load(test_config_path)

        api_key = loader.get_api_key("direct_key_provider")
        assert api_key == "my_direct_key_456"

    def test_get_api_key_with_prefix_detection(self, test_config_path):
        """Test detecting API keys with known prefixes."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        loader.load(test_config_path)

        # groq_simulator has key starting with "gsk_"
        api_key = loader.get_api_key("groq_simulator")
        assert api_key == "gsk_testkey123456"

        # nvidia_simulator has key starting with "nvapi-"
        api_key = loader.get_api_key("nvidia_simulator")
        assert api_key == "nvapi-testkey123"

    def test_get_model_for_role(self, test_config_path):
        """Test getting model for specific role."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        loader.load(test_config_path)

        model = loader.get_model_for_role("test_provider", "planner")
        assert model == "test/model-1"

        model = loader.get_model_for_role("test_provider", "engineer")
        assert model == "test/model-2"

    def test_llm_settings(self, test_config_path):
        """Test retrieving LLM settings."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        loader.load(test_config_path)

        llm_settings = loader.llm_settings
        assert llm_settings["temperature"] == 0.3
        assert llm_settings["max_tokens"] == 4096

    def test_agent_settings(self, test_config_path):
        """Test retrieving agent settings."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        loader.load(test_config_path)

        agent_settings = loader.agent_settings
        assert agent_settings["max_turns"] == 5
        assert agent_settings["retry_on_failure"] is True

    def test_rate_limit_settings(self, test_config_path):
        """Test retrieving rate limit settings."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        loader.load(test_config_path)

        rate_settings = loader.rate_limit_settings
        assert rate_settings["cooldown_seconds"] == 30
        assert rate_settings["max_wait_seconds"] == 120

    def test_provider_order(self, test_config_path):
        """Test retrieving provider order."""
        # Reset singleton
        ConfigLoader._instance = None
        ConfigLoader._config = None

        loader = ConfigLoader()
        loader.load(test_config_path)

        order = loader.provider_order
        assert order == ["test_provider", "env_only_provider", "direct_key_provider", "groq_simulator", "nvidia_simulator"]


class TestConfigLoaderReal:
    """Tests using the actual config.yaml file."""

    def test_groq_provider_has_key(self):
        """Test that Groq provider configuration can be detected."""
        from freeagentdev.core.config_loader import get_config

        config = get_config()
        provider = config.get_provider_config("groq")

        # The config has an actual key in api_key_env field
        assert provider is not None

        # The key should be accessible
        api_key = config.get_api_key("groq")
        assert api_key is not None, "Groq provider should have API key detected"

    def test_nvidia_provider_has_key(self):
        """Test that NVIDIA provider configuration can be detected."""
        from freeagentdev.core.config_loader import get_config

        config = get_config()
        api_key = config.get_api_key("nvidia")
        assert api_key is not None, "NVIDIA provider should have API key detected"

    def test_openrouter_provider_has_key(self):
        """Test that OpenRouter provider configuration can be detected."""
        from freeagentdev.core.config_loader import get_config

        config = get_config()
        api_key = config.get_api_key("openrouter")
        assert api_key is not None, "OpenRouter provider should have API key detected"

    def test_google_provider_from_env_var(self):
        """Test that Google provider can be configured via env var."""
        # Save current env var if exists
        original = os.environ.get("GOOGLE_API_KEY")

        try:
            # Set env var
            os.environ["GOOGLE_API_KEY"] = "test_google_key_123"

            # Force reload (need to create new instance)
            ConfigLoader._instance = None
            ConfigLoader._config = None

            from freeagentdev.core.config_loader import get_config
            config = get_config()

            api_key = config.get_api_key("google")
            assert api_key == "test_google_key_123"
        finally:
            # Restore original
            if original:
                os.environ["GOOGLE_API_KEY"] = original
            elif "GOOGLE_API_KEY" in os.environ:
                del os.environ["GOOGLE_API_KEY"]