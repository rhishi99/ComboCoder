"""Base agent class with enhanced error handling."""

from freeagentdev.core.llm_client import LLMClient

class BaseAgent:
    """Base class for all agents with role-based model selection."""

    def __init__(self, role: str, llm_client: LLMClient):
        self.role = role
        self.llm_client = llm_client
        self.last_provider = None
        self.last_model = None

    def generate(self, prompt: str, messages: list = None) -> str:
        """
        Sends a request to the LLM for the current role.
        Uses multi-provider fallback automatically.
        """
        result = self.llm_client.complete(prompt=prompt, role=self.role, messages=messages)
        return result

    def generate_with_provider(self, prompt: str, provider: str, messages: list = None) -> str:
        """Generate using a specific provider."""
        return self.llm_client.complete(
            prompt=prompt,
            role=self.role,
            messages=messages,
            provider=provider
        )

    def get_status(self) -> dict:
        """Get the current agent status."""
        return {
            "role": self.role,
            "provider_status": self.llm_client.get_provider_status()
        }
