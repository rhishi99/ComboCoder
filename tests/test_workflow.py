from freeagentdev.agents.workflow import FreeAgentWorkflow
from freeagentdev.core.llm_client import LLMClient
from pathlib import Path
import os

def test_workflow_run():
    print("Testing FreeAgentWorkflow.run()...")
    try:
        llm = LLMClient()
        workflow = FreeAgentWorkflow(llm)
        root_path = Path(os.getcwd())
        task = "Create a file named hello_test.txt with content 'Testing FreeAgentDev'"
        
        print(f"Running task: {task}")
        final_state = workflow.run(root_path, task)
        
        print(f"Workflow finished successfully.")
        print(f"Final current_agent: {final_state.get('current_agent')}")
        print(f"Review feedback: {final_state.get('review_feedback')}")
        print(f"Code changes: {final_state.get('code_changes')}")
        
        # Check if file was created (workflow.run calls apply_changes? No, cli.py does)
        # Wait, workflow.run doesn't call apply_changes.
    except Exception as e:
        print(f"Error during workflow run: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow_run()
