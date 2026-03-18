"""
Multi-agent workflow with parallel and sequential execution support.
Uses LangGraph for orchestrating the 4-agent workflow with automatic fallback.
"""

import concurrent.futures
from typing import TypedDict, Optional, List, Dict, Any
from pathlib import Path
from langgraph.graph import StateGraph, END

from freeagentdev.agents.roles import Planner, Architect, Engineer, Reviewer, SubTaskAgent
from freeagentdev.core.file_ops import get_context_from_design, get_repo_summary
from freeagentdev.core.task_detector import TaskDetector


class AgentState(TypedDict):
    root_path: Path
    task: str
    repo_summary: str
    repo_context: str
    plan: str
    design: str
    code_changes: str
    review_feedback: str
    turns: int
    current_agent: str
    # New fields
    context_docs: str
    execution_mode: str  # "parallel" or "sequential"
    subtasks: List[str]
    subtask_results: Dict[str, str]


class FreeAgentWorkflow:
    """Multi-agent workflow with parallel execution support."""

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.planner = Planner(llm_client)
        self.architect = Architect(llm_client)
        self.engineer = Engineer(llm_client)
        self.reviewer = Reviewer(llm_client)

        # Get configuration
        from freeagentdev.core.config_loader import get_config
        config = get_config()
        self.max_turns = config.agent_settings.get("max_turns", 3)
        self.parallel_enabled = config.agent_settings.get("parallel_execution", True)
        self.max_parallel = config.agent_settings.get("max_parallel_agents", 2)

    def _get_task_detector(self, root_path: Path) -> TaskDetector:
        return TaskDetector(root_path)

    def planner_node(self, state: AgentState) -> dict:
        """Plan the implementation based on task and context."""
        task_detector = self._get_task_detector(state["root_path"])

        # Gather context documents if available
        context_docs = state.get("context_docs", "")
        if not context_docs:
            context_docs = task_detector.gather_context_documents() or ""

        # Determine execution mode
        execution_mode = state.get("execution_mode", "")
        if not execution_mode:
            execution_mode = task_detector.detect_execution_mode(state["task"])

        # Analyze task for subtasks
        task_analysis = task_detector.analyze_task_structure(state["task"])

        # Generate plan
        plan = self.planner.plan(
            repo_summary=state["repo_summary"],
            task=state["task"],
            feedback=state.get("review_feedback", ""),
            context_docs=context_docs
        )

        return {
            "plan": plan,
            "context_docs": context_docs,
            "execution_mode": execution_mode,
            "subtasks": task_analysis.get("subtasks", []),
            "current_agent": "architect"
        }

    def architect_node(self, state: AgentState) -> dict:
        """Design the technical specification."""
        design = self.architect.design(
            plan=state["plan"],
            repo_summary=state["repo_summary"],
            context_docs=state.get("context_docs", "")
        )
        return {"design": design, "current_agent": " context_gatherer"}

    def context_gatherer_node(self, state: AgentState) -> dict:
        """Fetch relevant files mentioned in the design."""
        context = get_context_from_design(state["root_path"], state["design"])

        # Also include context docs
        context_docs_context = ""
        if state.get("context_docs"):
            context_docs_context = f"\n\n=== Project Context ===\n{state['context_docs']}"

        return {
            "repo_context": context + context_docs_context,
            "current_agent": "engineer"
        }

    def engineer_node(self, state: AgentState) -> dict:
        """Implement the code based on design."""
        # Check if parallel execution is needed
        if (self.parallel_enabled and
            state.get("execution_mode") == "parallel" and
            state.get("subtasks") and
            state.get("turns", 0) == 0):  # Only on first iteration
            return self._parallel_engineering(state)

        # Sequential execution
        code_changes = self.engineer.implement(
            design_doc=state["design"],
            repo_context=state["repo_context"],
            task=state["task"]
        )
        return {"code_changes": code_changes, "current_agent": "reviewer"}

    def _parallel_engineering(self, state: AgentState) -> dict:
        """Execute engineering tasks in parallel."""
        subtasks = state.get("subtasks", [])
        results = {}

        # Limit parallel execution
        max_workers = min(self.max_parallel, len(subtasks)) if subtasks else 1

        if subtasks and max_workers > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_subtask = {}
                for i, subtask in enumerate(subtasks[:max_workers]):
                    agent = SubTaskAgent(self.llm_client, i)
                    future = executor.submit(
                        agent.implement_subtask,
                        subtask,
                        state["repo_context"],
                        state["design"]
                    )
                    future_to_subtask[future] = subtask

                for future in concurrent.futures.as_completed(future_to_subtask):
                    subtask = future_to_subtask[future]
                    try:
                        results[subtask] = future.result()
                    except Exception as e:
                        results[subtask] = f"# Error implementing {subtask}: {e}"

        # Combine results
        combined_changes = ""
        if results:
            for subtask, changes in results.items():
                combined_changes += f"\n# Task: {subtask}\n{changes}\n"
        else:
            # Fallback to single engineering
            combined_changes = self.engineer.implement(
                design_doc=state["design"],
                repo_context=state["repo_context"],
                task=state["task"]
            )

        return {
            "code_changes": combined_changes,
            "subtask_results": results,
            "current_agent": "reviewer"
        }

    def reviewer_node(self, state: AgentState) -> dict:
        """Review the code changes."""
        feedback = self.reviewer.review(
            task=state["task"],
            code_changes=state["code_changes"],
            design_doc=state.get("design", ""),
            context_docs=state.get("context_docs", "")
        )

        turns = state["turns"]

        # Check if passed or max turns reached
        if "PASS" in feedback.upper():
            return {
                "review_feedback": feedback,
                "current_agent": END,
                "turns": turns + 1
            }
        elif turns >= self.max_turns:
            return {
                "review_feedback": f"MAX TURNS REACHED. Last review:\n{feedback}",
                "current_agent": END,
                "turns": turns + 1
            }
        else:
            # Continue iteration
            return {
                "review_feedback": feedback,
                "current_agent": "planner",
                "turns": turns + 1
            }

    def build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("planner", self.planner_node)
        workflow.add_node("architect", self.architect_node)
        workflow.add_node("context_gatherer", self.context_gatherer_node)
        workflow.add_node("engineer", self.engineer_node)
        workflow.add_node("reviewer", self.reviewer_node)

        # Set entry point
        workflow.set_entry_point("planner")

        # Add edges
        workflow.add_edge("planner", "architect")
        workflow.add_edge("architect", "context_gatherer")
        workflow.add_edge("context_gatherer", "engineer")

        # Conditional edge from reviewer
        def should_continue(state: AgentState):
            return state["current_agent"]

        workflow.add_conditional_edges("reviewer", should_continue)

        return workflow.compile()

    def run(self, root_path: Path, task: str) -> dict:
        """
        Run the complete workflow.

        Args:
            root_path: Path to the repository
            task: The natural language task

        Returns:
            Final state with all results
        """
        # Initialize task detector
        task_detector = self._get_task_detector(root_path)

        # Gather initial context
        repo_summary = get_repo_summary(root_path)
        context_docs = task_detector.gather_context_documents() or ""
        execution_mode = task_detector.detect_execution_mode(task)

        # Build initial state
        initial_state = {
            "root_path": root_path,
            "task": task,
            "repo_summary": repo_summary,
            "repo_context": "",
            "plan": "",
            "design": "",
            "code_changes": "",
            "review_feedback": "",
            "turns": 0,
            "current_agent": "planner",
            "context_docs": context_docs,
            "execution_mode": execution_mode,
            "subtasks": [],
            "subtask_results": {}
        }

        # Run workflow
        graph = self.build_graph()
        final_state = graph.invoke(initial_state)

        return final_state
