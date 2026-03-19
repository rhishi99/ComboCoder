import litellm
import os
import time
import threading
from typing import Optional, List, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
from freeagentdev.core.config_loader import get_config, ConfigLoader

# Silence LiteLLM output
litellm.suppress_debug_info = True
os.environ["LITELLM_LOG"] = "ERROR"
litellm.set_verbose = False

class RateLimitTracker:
    """Tracks API usage for rate limiting."""

    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    def record_request(self, provider: str):
        """Record a request timestamp."""
        with self.lock:
            self.requests[provider].append(datetime.now())

    def get_requests_in_window(self, provider: str, window_seconds: int = 60) -> int:
        """Get number of requests in the sliding window."""
        with self.lock:
            cutoff = datetime.now() - timedelta(seconds=window_seconds)
            self.requests[provider] = [
                t for t in self.requests[provider] if t > cutoff
            ]
            return len(self.requests[provider])

    def should_wait(self, provider: str, max_requests: int, window_seconds: int = 60) -> bool:
        """Check if we should wait before making another request."""
        return self.get_requests_in_window(provider, window_seconds) >= max_requests

    def wait_if_needed(self, provider: str, max_requests: int, window_seconds: int = 60, max_wait: int = 300):
        """Wait if rate limit is reached."""
        start = time.time()
        while self.should_wait(provider, max_requests, window_seconds):
            if time.time() - start > max_wait:
                raise TimeoutError(f"Rate limit wait exceeded {max_wait} seconds for {provider}")
            time.sleep(5)

class LLMClient:
    """Multi-provider LLM client with automatic fallback."""

    def __init__(self, config_path=None):
        self.config_loader = get_config()
        self.config = self.config_loader._config
        self.rate_tracker = RateLimitTracker()

        # Get global settings
        self.temperature = self.config_loader.llm_settings.get("temperature", 0.2)
        self.max_tokens = self.config_loader.llm_settings.get("max_tokens", 8192)
        self.timeout = self.config_loader.llm_settings.get("timeout_seconds", 120)

        # Agent settings
        agent_settings = self.config_loader.agent_settings
        self.max_retries = agent_settings.get("max_retries_per_request", 3)
        self.retry_delay = agent_settings.get("retry_delay_seconds", 5)
        self.fallback_on_rate_limit = agent_settings.get("fallback_on_rate_limit", True)

        # Rate limit settings
        rate_settings = self.config_loader.rate_limit_settings
        self.cooldown = rate_settings.get("cooldown_seconds", 60)
        self.max_wait = rate_settings.get("max_wait_seconds", 300)

        # Track provider health
        self.provider_errors = defaultdict(int)
        self.provider_cooldown_until = {}
        
        # Tracking for UI
        self.last_provider = "none"
        self.last_model = "none"

    def _get_available_providers(self) -> List[str]:
        """Get list of providers with valid API keys."""
        available = []
        for provider in self.config_loader.provider_order:
            if self.config_loader.is_provider_configured(provider):
                # Check if in cooldown
                cooldown_until = self.provider_cooldown_until.get(provider)
                if cooldown_until and datetime.now() < cooldown_until:
                    continue
                available.append(provider)
        return available

    def _get_model(self, provider: str, role: str) -> str:
        """Get model for provider and role."""
        model = self.config_loader.get_model_for_role(provider, role)
        if not model:
            # Fallback to first available model
            provider_config = self.config_loader.get_provider_config(provider)
            if provider_config and "models" in provider_config:
                models = list(provider_config["models"].values())
                if models:
                    model = models[0]
        return model

    def _setup_provider_env(self, provider: str):
        """Setup environment for a specific provider."""
        api_key = self.config_loader.get_api_key(provider)
        if api_key:
            provider_config = self.config_loader.get_provider_config(provider)
            # LiteLLM uses specific env vars
            env_mapping = {
                "groq": "GROQ_API_KEY",
                "nvidia": "NVIDIA_API_KEY",
                "openrouter": "OPENROUTER_API_KEY",
                "google": "GEMINI_API_KEY",
                "cerebras": "CEREBRAS_API_KEY",
                "together": "TOGETHER_API_KEY",
                "deepinfra": "DEEPINFRA_API_KEY",
                "fireworks": "FIREWORKS_API_KEY",
                "opencode": "OPENCODE_API_KEY"
            }
            env_var = env_mapping.get(provider, f"{provider.upper()}_API_KEY")
            os.environ[env_var] = api_key

    def complete(
        self,
        prompt: str,
        role: str = None,
        messages: list = None,
        provider: str = None,
        progress_callback=None
    ) -> str:
        """
        Complete a prompt with automatic provider fallback.

        Args:
            prompt: The prompt to complete
            role: Agent role (planner, architect, engineer, reviewer)
            messages: Optional message list for chat completion
            provider: Optional specific provider to use
            progress_callback: Optional callable for logging fallback events

        Returns:
            The completion text
        """
        if messages is None:
            messages = [{"role": "user", "content": prompt}]

        # If specific provider requested, try only that
        if provider:
            return self._try_provider(provider, role, messages)

        # Try each available provider
        errors = []
        providers_to_try = self._get_available_providers()

        if not providers_to_try:
            raise RuntimeError("No providers configured with valid API keys")

        for current_provider in providers_to_try:
            try:
                # Update metadata for UI
                self.last_provider = current_provider
                self.last_model = self._get_model(current_provider, role or "planner")
                
                result = self._try_provider(current_provider, role, messages)
                # Reset error count on success
                self.provider_errors[current_provider] = 0
                return result
            except Exception as e:
                errors.append((current_provider, str(e)))
                self.provider_errors[current_provider] += 1

                # Put provider in cooldown if too many errors
                if self.provider_errors[current_provider] >= 3:
                    self.provider_cooldown_until[current_provider] = (
                        datetime.now() + timedelta(seconds=self.cooldown)
                    )

                # Check if it's a rate limit error
                if "rate" in str(e).lower() and self.fallback_on_rate_limit:
                    if progress_callback:
                        progress_callback(f"⚠️ {current_provider.upper()} rate limited. Switching to next provider...")
                    continue  # Try next provider

                # For other errors, retry with delay
                if self.provider_errors[current_provider] < self.max_retries:
                    if progress_callback:
                        progress_callback(f"⚠️ {current_provider.upper()} error. Retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                    try:
                        result = self._try_provider(current_provider, role, messages)
                        self.provider_errors[current_provider] = 0
                        return result
                    except Exception as e2:
                        errors.append((current_provider, f"retry: {e2}"))

        # All providers failed
        error_msg = "\n".join([f"{p}: {e}" for p, e in errors])
        raise RuntimeError(f"All providers failed:\n{error_msg}")

    def _try_provider(self, provider: str, role: str, messages: list) -> str:
        """Try completion with a specific provider."""
        # Setup environment
        self._setup_provider_env(provider)

        # Get model
        model = self._get_model(provider, role or "planner")

        # Check rate limits
        provider_config = self.config_loader.get_provider_config(provider)
        rate_limit = provider_config.get("rate_limit", {})
        max_requests = rate_limit.get("requests_per_minute", 30)

        self.rate_tracker.wait_if_needed(
            provider,
            max_requests,
            window_seconds=60,
            max_wait=self.max_wait
        )

        # Get provider-specific settings
        base_url = provider_config.get("base_url")

        # Make request
        self.rate_tracker.record_request(provider)

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }

        if base_url:
            kwargs["api_base"] = base_url

        response = litellm.completion(**kwargs)

        return response.choices[0].message.content

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        status = {}
        for provider in self.config_loader.provider_order:
            configured = self.config_loader.is_provider_configured(provider)
            in_cooldown = False
            cooldown_until = self.provider_cooldown_until.get(provider)
            if cooldown_until and datetime.now() < cooldown_until:
                in_cooldown = True

            status[provider] = {
                "configured": configured,
                "available": configured and not in_cooldown,
                "error_count": self.provider_errors.get(provider, 0),
                "in_cooldown": in_cooldown,
                "cooldown_remaining": (
                    (cooldown_until - datetime.now()).total_seconds()
                    if in_cooldown and cooldown_until else 0
                )
            }
        return status
