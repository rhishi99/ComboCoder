import yaml
import os
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

# Known API key prefixes to detect direct keys vs env var names
API_KEY_PREFIXES = (
    "gsk_",      # Groq
    "nvapi-",    # NVIDIA
    "sk-or-",    # OpenRouter
    "sk-ant-",   # Anthropic/Claude
    "sk-",       # OpenAI and many others
    "AIza",      # Google
    "cerebras",  # Cerebras
    "tk.",       # Together AI
)

class ConfigLoader:
    """Handles loading and managing multi-provider configuration."""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self.load()

    def load(self, config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict:
        """Load configuration from YAML file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found at {path}.")
        with open(path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f) or {}
        return self._config

    def get(self, key: str, default=None):
        """Get nested config value using dot notation."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        if value is None:
            return default
        return value

    @property
    def providers(self) -> dict:
        return self._config.get("providers", {})

    @property
    def provider_order(self) -> list:
        return self._config.get("provider_order", [])

    @property
    def llm_settings(self) -> dict:
        return self._config.get("llm", {})

    @property
    def agent_settings(self) -> dict:
        return self._config.get("agents", {})

    @property
    def rate_limit_settings(self) -> dict:
        return self._config.get("rate_limit", {})

    @property
    def task_detection(self) -> dict:
        return self._config.get("task_detection", {})

    def get_provider_config(self, provider_name: str) -> Optional[dict]:
        """Get configuration for a specific provider."""
        return self.providers.get(provider_name)

    def get_model_for_role(self, provider_name: str, role: str) -> Optional[str]:
        """Get the model for a specific provider and role."""
        provider = self.get_provider_config(provider_name)
        if provider:
            return provider.get("models", {}).get(role)
        return None

    def _is_likely_api_key(self, value: str) -> bool:
        """Check if a string looks like an actual API key (not an env var name)."""
        if not value:
            return False
        return value.startswith(API_KEY_PREFIXES) or len(value) > 20

    def get_api_key(self, provider_name: str) -> Optional[str]:
        """Get API key for a provider.

        Priority:
        1. Check for 'api_key' field (direct key in config)
        2. Check 'api_key_env' - if it looks like a direct key, use it directly
        3. Otherwise, treat 'api_key_env' as environment variable name and fetch from os.environ
        """
        provider = self.get_provider_config(provider_name)
        if not provider:
            return None

        # First priority: 'api_key' field (explicit direct key)
        direct_key = provider.get("api_key")
        if direct_key:
            return direct_key

        # Second: Check 'api_key_env' - could be direct key or env var name
        env_var = provider.get("api_key_env")
        if not env_var:
            return None

        # If the value looks like an actual API key, use it directly
        if self._is_likely_api_key(env_var):
            return env_var

        # Otherwise, treat as environment variable name
        return os.environ.get(env_var)

    def is_provider_configured(self, provider_name: str) -> bool:
        """Check if a provider has valid configuration."""
        return bool(self.get_api_key(provider_name))


# Global instance
_config_loader = None

def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict:
    """Legacy function for backward compatibility."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader.load(config_path)

def get_config() -> ConfigLoader:
    """Get the global config loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

def get_role_model(role: str, config: dict = None) -> str | None:
    """Legacy function for backward compatibility."""
    loader = get_config()
    # Try each provider in order
    for provider in loader.provider_order:
        model = loader.get_model_for_role(provider, role)
        if model and loader.is_provider_configured(provider):
            return model
    return None