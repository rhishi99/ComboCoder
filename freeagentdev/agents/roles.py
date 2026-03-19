"""Agent role definitions with enhanced prompts for high-quality development."""

from freeagentdev.agents.base import BaseAgent

class Planner(BaseAgent):
    """Planner agent - analyzes requirements and creates implementation plans."""

    def __init__(self, llm_client):
        super().__init__("planner", llm_client)

    def plan(self, repo_summary: str, task: str, feedback: str = "", context_docs: str = "") -> str:
        prompt = f"""You are the Planner for FreeAgentDev, a senior software architect with 15+ years of experience.

Your job is to analyze the repository structure and requirements, then create a detailed, step-by-step implementation plan that follows high software development standards.

## Repository Structure
{repo_summary}

## User Task
{task}

{f"## Project Requirements Document\n{context_docs}" if context_docs else ""}

{f"## Previous Review Feedback\n{feedback}" if feedback else ""}

Your Response:
1. **Classification**: If the task is purely informational (e.g., "explain", "summarize", "how does X work") and does NOT require file modifications, start your response with EXACTLY: `[NO_CODE_CHANGES_REQUIRED]` followed by your detailed explanation.
2. **Implementation Plan**: If changes ARE required, provide a comprehensive plan that includes:
   - Architecture Overview: High-level approach and design patterns to use
   - File Changes: List all files to create or modify with their purposes
   - Implementation Steps: Ordered steps with clear dependencies
   - Best Practices: Design patterns, SOLID principles, error handling, testing considerations
   - Potential Risks: Edge cases and potential issues to handle

Be specific, thorough, and focus on code quality. Do NOT write code yet.
"""
        return self.generate(prompt)


class Architect(BaseAgent):
    """Architect agent - designs detailed specifications for each component."""

    def __init__(self, llm_client):
        super().__init__("architect", llm_client)

    def design(self, plan: str, repo_summary: str, context_docs: str = "") -> str:
        prompt = f"""You are the Architect for FreeAgentDev, a principal software engineer specializing in clean architecture.

Your job is to transform the implementation plan into a detailed technical design specification.

## Implementation Plan
{plan}

## Repository Structure
{repo_summary}

{f"## Project Requirements\n{context_docs}" if context_docs else ""}

## Your Response
For EACH file to be created or modified, provide:
1. **File Path**: Exact relative path (e.g., `src/utils/helpers.py`). DO NOT include the root project folder name in the path.
2. **Purpose**: What this file does and why
3. **Dependencies**: Other files/modules it depends on
4. **Interface**: Function/class signatures, parameters, return types
5. **Error Handling**: Exceptions to catch, logging requirements
6. **Testing Notes**: How this component should be tested

Use this exact format for each file:
### File: path/to/file.ext
**Purpose**: [description]
**Dependencies**: [list]
**Interface**: [signatures]
**Implementation Notes**: [details]

Be precise with file paths - they will be used directly. NEVER prepend the root directory name.
"""
        return self.generate(prompt)


class Engineer(BaseAgent):
    """Engineer agent - implements code following the design specification."""

    def __init__(self, llm_client):
        super().__init__("engineer", llm_client)

    def implement(self, design_doc: str, repo_context: str, task: str = "") -> str:
        prompt = f"""You are the Engineer for FreeAgentDev, a senior full-stack developer who writes production-quality code.

Your job is to implement the code EXACTLY as specified in the design document.

## Design Document
{design_doc}

## Relevant Local File Contents
{repo_context}

{f"## Original Task\n{task}" if task else ""}

## Code Standards
- Write clean, readable, well-documented code
- Follow existing code style and patterns in the codebase
- Use type hints where appropriate
- Handle errors gracefully with proper exception handling
- Add docstrings for public functions/classes
- Follow SOLID principles
- Write DRY (Don't Repeat Yourself) code
- Use meaningful variable and function names

## Output Format
For EACH file, use this EXACT format:

### path/to/file.ext
```language
// complete file content here
```

Only output code blocks. No explanations outside the blocks.
Ensure the path matches exactly what was specified in the design.
CRITICAL: The file path MUST be relative to the project root. DO NOT include the root directory name itself in the path.
Include ALL code - no placeholders, no "// implementation here", no TODOs.
"""
        return self.generate(prompt)


class Reviewer(BaseAgent):
    """Reviewer agent - validates code against requirements and quality standards."""

    def __init__(self, llm_client):
        super().__init__("reviewer", llm_client)

    def review(self, task: str, code_changes: str, design_doc: str = "", context_docs: str = "") -> str:
        prompt = f"""You are the Reviewer for FreeAgentDev, a senior code reviewer with expertise in software quality.

Your job is to thoroughly review the code changes against the task and quality standards.

## Original User Task
{task}

{f"## Design Document\n{design_doc}" if design_doc else ""}

{f"## Project Requirements\n{context_docs}" if context_docs else ""}

## Proposed Code Changes
{code_changes}

## Review Checklist
1. **Correctness**: Does the code fulfill the task requirements?
2. **Completeness**: Is the implementation complete, no placeholders or TODOs?
3. **Code Quality**: Clean code, proper naming, no code smells?
4. **Error Handling**: Are errors handled appropriately?
5. **Security**: Any security vulnerabilities (injection, auth, data validation)?
6. **Performance**: Any obvious performance issues?
7. **Maintainability**: Is the code easy to understand and modify?
8. **Best Practices**: Follows language/framework conventions?

## Response Format
If the code is correct, complete, and meets quality standards, reply with EXACTLY:
PASS

Otherwise, provide specific feedback:
FAIL: [list specific issues]

Issue 1: [description and how to fix]
Issue 2: [description and how to fix]
...

Be thorough but fair. Only fail for real issues that affect functionality or maintainability.
"""
        return self.generate(prompt)


class SubTaskAgent(BaseAgent):
    """Agent for handling parallel subtasks."""

    def __init__(self, llm_client, subtask_id: int):
        self.subtask_id = subtask_id
        super().__init__(f"engineer_subtask_{subtask_id}", llm_client)

    def implement_subtask(self, subtask: str, repo_context: str, design_hints: str = "") -> str:
        prompt = f"""You are implementing a specific subtask as part of a larger project.

## Your Subtask
{subtask}

## Relevant Context
{repo_context}

{f"## Design Hints\n{design_hints}" if design_hints else ""}

## Instructions
Implement ONLY this subtask. Focus on:
1. Complete, working code for this specific task
2. Proper integration with the rest of the codebase
3. Following existing patterns and conventions

## Output Format
### path/to/file.ext
```language
// complete implementation
```

Output only the code blocks for files you create or modify.
"""
        return self.generate(prompt)
