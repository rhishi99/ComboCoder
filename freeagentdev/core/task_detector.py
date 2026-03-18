"""Task detection and context analysis module."""

import os
import re
from pathlib import Path
from typing import Tuple, List, Optional
from freeagentdev.core.config_loader import get_config

class TaskDetector:
    """Detects task execution mode and gathers context."""

    def __init__(self, root_path: Path = None):
        self.config_loader = get_config()
        self.task_config = self.config_loader.task_detection
        self.root_path = root_path or Path.cwd()

    def detect_execution_mode(self, task: str) -> str:
        """
        Detect whether task should run in parallel or sequential mode.

        Returns: "parallel", "sequential", or "auto"
        """
        auto_detect = self.task_config.get("auto_detect_mode", True)
        if not auto_detect:
            return "auto"

        task_lower = task.lower()

        # Check for parallel keywords
        parallel_keywords = self.task_config.get("parallel_keywords", [])
        for keyword in parallel_keywords:
            if keyword.lower() in task_lower:
                return "parallel"

        # Check for sequential keywords
        sequential_keywords = self.task_config.get("sequential_keywords", [])
        for keyword in sequential_keywords:
            if keyword.lower() in task_lower:
                return "sequential"

        # Check for PRD keywords (usually sequential for thoroughness)
        prd_keywords = self.task_config.get("prd_keywords", [])
        for keyword in prd_keywords:
            if keyword.lower() in task_lower:
                return "sequential"

        # Analyze task complexity
        if self._is_complex_task(task):
            return "parallel"

        return "sequential"

    def _is_complex_task(self, task: str) -> bool:
        """Determine if task is complex enough to benefit from parallel execution."""
        complexity_indicators = [
            "multiple files",
            "several",
            "various",
            "all the",
            "refactor",
            "migrate",
            "implement",
            "add.*and",
            "update.*and",
            "create.*and",
        ]
        task_lower = task.lower()
        for pattern in complexity_indicators:
            if re.search(pattern, task_lower):
                return True

        # Check if multiple distinct actions
        action_words = ["add", "create", "update", "modify", "fix", "implement", "refactor", "remove"]
        action_count = sum(1 for word in action_words if word in task_lower)
        if action_count >= 2:
            return True

        return False

    def gather_context_documents(self) -> str:
        """Gather content from PRD, requirements, or spec documents."""
        context_docs = self.task_config.get("context_documents", [])
        gathered_content = []

        for doc_path in context_docs:
            full_path = self.root_path / doc_path
            if full_path.exists() and full_path.is_file():
                try:
                    content = full_path.read_text(encoding="utf-8")
                    if content.strip():
                        gathered_content.append(f"=== {doc_path} ===\n{content}\n")
                except Exception as e:
                    gathered_content.append(f"=== {doc_path} ===\n[Error reading: {e}]\n")

        return "\n".join(gathered_content) if gathered_content else None

    def analyze_task_structure(self, task: str) -> dict:
        """
        Analyze task to extract components that can be parallelized.

        Returns dict with:
        - main_task: The primary task
        - subtasks: List of potential subtasks
        - dependencies: List of file/module dependencies mentioned
        - suggested_agents: Optimal agent assignments
        """
        result = {
            "main_task": task,
            "subtasks": [],
            "dependencies": [],
            "suggested_agents": {},
            "execution_order": []
        }

        # Extract file paths mentioned
        file_patterns = [
            r"[\w/\-]+\.(py|js|ts|jsx|tsx|java|go|rs|cpp|c|h|json|yaml|yml|md)",
            r"`([^`]+)`",
            r"file[s]?\s*[:\"]?\s*([^\n,;]+)",
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, task)
            if matches:
                if isinstance(matches[0], tuple):
                    result["dependencies"].extend([m[0] for m in matches if m])
                else:
                    result["dependencies"].extend(matches)

        # Detect subtasks (numbered lists, bullet points, "and" conjunctions)
        subtask_patterns = [
            r"\d+\.\s*([^\n]+)",  # Numbered lists
            r"[-*]\s*([^\n]+)",   # Bullet points
        ]

        for pattern in subtask_patterns:
            matches = re.findall(pattern, task)
            if matches:
                result["subtasks"].extend(matches)

        # Split by "and" or semicolons for multi-part tasks
        parts = re.split(r"\s+and\s+|\s*;\s*", task)
        if len(parts) > 1:
            result["subtasks"].extend([p.strip() for p in parts if p.strip()])

        # Remove duplicates while preserving order
        result["subtasks"] = list(dict.fromkeys(result["subtasks"]))
        result["dependencies"] = list(dict.fromkeys(result["dependencies"]))

        return result

    def should_read_prd(self, task: str) -> bool:
        """Check if task should trigger PRD reading."""
        prd_keywords = self.task_config.get("prd_keywords", [])
        task_lower = task.lower()
        return any(kw.lower() in task_lower for kw in prd_keywords)

    def get_full_context(self, task: str, repo_summary: str) -> str:
        """
        Get complete context for task execution.
        Combines repo summary, PRD/spec documents, and task analysis.
        """
        context_parts = [f"Repository Structure:\n{repo_summary}"]

        # Check for and gather context documents
        if self.should_read_prd(task):
            doc_context = self.gather_context_documents()
            if doc_context:
                context_parts.append(f"\nProject Requirements:\n{doc_context}")

        # Analyze task structure
        task_analysis = self.analyze_task_structure(task)
        if task_analysis["dependencies"]:
            context_parts.append(f"\nReferenced Files: {', '.join(task_analysis['dependencies'])}")

        return "\n".join(context_parts)
