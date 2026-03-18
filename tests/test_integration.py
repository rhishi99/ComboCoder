from freeagentdev.core.llm_client import LLMClient
import os

def test_llm_flow():
    print("Testing LLM Client with multi-provider fallback...")
    try:
        client = LLMClient()
        prompt = "Reply with exactly 'SUCCESS: FreeAgentDev is working.'"
        print(f"Sending prompt to available providers...")
        response = client.complete(prompt=prompt, role="planner")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_llm_flow()
