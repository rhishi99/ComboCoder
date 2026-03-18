"""Tests for LLM client - provider fallback mechanism."""
import pytest
import os
from freeagentdev.core.llm_client import LLMClient, RateLimitTracker


class TestRateLimitTracker:
    """Test suite for rate limit tracking."""

    def test_record_request(self):
        """Test recording request timestamps."""
        tracker = RateLimitTracker()
        tracker.record_request("test_provider")

        # Should have one request
        count = tracker.get_requests_in_window("test_provider", 60)
        assert count == 1

    def test_sliding_window(self):
        """Test sliding window clears old requests."""
        tracker = RateLimitTracker()
        tracker.record_request("test_provider")
        tracker.record_request("test_provider")

        # Set old timestamp by manipulating the internal dict
        from datetime import datetime, timedelta
        old_time = datetime.now() - timedelta(seconds=120)
        tracker.requests["test_provider"][0] = old_time

        # Should only count recent requests
        count = tracker.get_requests_in_window("test_provider", 60)
        assert count == 1

    def test_should_wait(self):
        """Test rate limit check."""
        tracker = RateLimitTracker()

        # Add requests up to limit
        for _ in range(10):
            tracker.record_request("test_provider")

        # Should wait now
        assert tracker.should_wait("test_provider", 10, 60) is True
        assert tracker.should_wait("test_provider", 20, 60) is False

    def test_isolation_between_providers(self):
        """Test that providers are tracked independently."""
        tracker = RateLimitTracker()

        for _ in range(5):
            tracker.record_request("provider_a")
            tracker.record_request("provider_b")

        assert tracker.get_requests_in_window("provider_a", 60) == 5
        assert tracker.get_requests_in_window("provider_b", 60) == 5


class TestLLMClientProviderFallback:
    """Test suite for LLM client provider fallback."""

    def test_get_provider_status(self):
        """Test getting provider status."""
        # Force fresh instance
        from freeagentdev.core.config_loader import ConfigLoader
        ConfigLoader._instance = None
        ConfigLoader._config = None

        client = LLMClient()
        status = client.get_provider_status()

        # Should have status for all providers
        assert "groq" in status
        assert "nvidia" in status
        assert "openrouter" in status

        # Check status structure
        for provider, info in status.items():
            assert "configured" in info
            assert "available" in info
            assert "error_count" in info
            assert "in_cooldown" in info

    def test_available_providers(self):
        """Test getting list of available providers."""
        from freeagentdev.core.config_loader import ConfigLoader
        ConfigLoader._instance = None
        ConfigLoader._config = None

        client = LLMClient()
        providers = client._get_available_providers()

        # Should include configured providers not in cooldown
        # With our API keys, should be groq, nvidia, openrouter
        assert "groq" in providers or "nvidia" in providers or "openrouter" in providers

    def test_model_selection(self):
        """Test model selection for different roles."""
        from freeagentdev.core.config_loader import ConfigLoader
        ConfigLoader._instance = None
        ConfigLoader._config = None

        client = LLMClient()

        # Test model for each role
        for role in ["planner", "architect", "engineer", "reviewer"]:
            model = client._get_model("groq", role)
            assert model is not None
            assert "groq" in model.lower() or "llama" in model.lower()

    def test_provider_cooldown(self):
        """Test provider cooldown after errors."""
        from freeagentdev.core.config_loader import ConfigLoader
        from datetime import datetime, timedelta

        ConfigLoader._instance = None
        ConfigLoader._config = None

        client = LLMClient()

        # Put a provider in cooldown manually
        client.provider_cooldown_until["test_provider"] = datetime.now() + timedelta(seconds=30)

        # Provider should not be available
        providers = client._get_available_providers()
        assert "test_provider" not in providers

    def test_error_tracking(self):
        """Test error count tracking."""
        from freeagentdev.core.config_loader import ConfigLoader
        ConfigLoader._instance = None
        ConfigLoader._config = None

        client = LLMClient()

        # Record errors
        client.provider_errors["test_provider"] += 1
        client.provider_errors["test_provider"] += 1

        assert client.provider_errors["test_provider"] == 2


class TestProviderIntegration:
    """Integration tests that make actual API calls - use sparingly."""

    @pytest.mark.slow
    def test_quick_completion(self):
        """Test a simple completion to verify providers work."""
        from freeagentdev.core.config_loader import ConfigLoader
        ConfigLoader._instance = None
        ConfigLoader._config = None

        # This test makes an actual API call - skip in CI
        if os.environ.get("CI"):
            pytest.skip("Skipping API test in CI")

        client = LLMClient()

        # Simple test prompt
        try:
            result = client.complete(
                prompt="Say 'test successful' in exactly 2 words.",
                role="planner",
                messages=[{"role": "user", "content": "Say 'test successful' in exactly 2 words."}]
            )
            # Just verify we got a response
            assert result is not None
            assert len(result) > 0
        except Exception as e:
            # Should not raise if providers are configured
            pytest.fail(f"API call failed: {e}")