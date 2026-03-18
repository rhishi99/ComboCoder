"""File operations for repo scanning and change application."""

import os
import re
from pathlib import Path
from typing import List, Optional

# Common ignore patterns
IGNORE_PATTERNS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache",
    ".vscode", ".idea", "dist", "build", ".DS_Store", "package-lock.json",
    "yarn.lock", ".env", ".env.local", "*.pyc", ".mypy_cache", ".ruff_cache",
    "Poetry.lock", "Pipfile.lock", "go.sum", "Cargo.lock"
}

# Extensions to include (empty = include all)
INCLUDE_EXTENSIONS = set()  # Add specific extensions if needed


def is_ignored(path: Path) -> bool:
    """Returns True if any part of the path matches an ignore pattern."""
    name = path.name
    return any(
        part in IGNORE_PATTERNS or part.startswith(".")
        for part in path.parts
    ) or name in IGNORE_PATTERNS or name.startswith(".")


def get_repo_summary(root_path: Path, max_depth: int = 4) -> str:
    """Generates a tree-like summary of the current directory."""
    summary_lines = [f"Root: {root_path.name}/"]

    def _walk(current: Path, depth: int):
        if depth > max_depth:
            return

        try:
            items = sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return

        for item in items:
            if is_ignored(item):
                continue

            rel_path = item.relative_to(root_path)
            indent = "  " * depth

            if item.is_dir():
                summary_lines.append(f"{indent}📁 {item.name}/")
                _walk(item, depth + 1)
            else:
                # Show file size for context
                try:
                    size = item.stat().st_size
                    size_str = _format_size(size)
                    summary_lines.append(f"{indent}📄 {item.name} ({size_str})")
                except:
                    summary_lines.append(f"{indent}📄 {item.name}")

    _walk(root_path, 1)
    return "\n".join(summary_lines)


def _format_size(size: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.0f}{unit}" if unit == 'B' else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def get_file_content(root_path: Path, file_path_str: str) -> str:
    """Safely reads file content."""
    try:
        full_path = root_path / file_path_str
        if full_path.exists() and full_path.is_file():
            # Check file size (skip if > 1MB)
            if full_path.stat().st_size > 1_000_000:
                return f"[FILE {file_path_str} TOO LARGE TO READ]"
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        return f"[ERROR READING {file_path_str}: {e}]"
    return f"[FILE {file_path_str} NOT FOUND]"


def get_context_from_design(root_path: Path, design_text: str) -> str:
    """Extracts file names mentioned in design and returns their content."""
    # Matches common file paths/names
    potential_paths = set()

    # Backticked paths
    potential_paths.update(re.findall(r"[`\']([\w\.\/\-_]+\.\w+)[\'`]", design_text))

    # Paths with ./ or / prefix
    potential_paths.update(re.findall(r"(?:\s|\n)(\.?/[\w\.\/\-_]+\.\w+)", design_text))

    # Quoted paths
    potential_paths.update(re.findall(r"\"([\w\.\/\-_]+\.\w+)\"", design_text))

    # File markers like "File: path" or "path/to/file.ext:"
    potential_paths.update(re.findall(r"(?:File:?\s*|^)([\w\/\-_]+\.\w+)", design_text, re.MULTILINE))

    context_blocks = []
    for p_str in sorted(potential_paths):
        p_str = p_str.lstrip("./")
        content = get_file_content(root_path, p_str)
        if content and not content.startswith("[FILE") and not content.startswith("[ERROR"):
            context_blocks.append(f"--- FILE: {p_str} ---\n{content}\n")

    return "\n".join(context_blocks) if context_blocks else "No relevant context found."


def apply_changes(root_path: Path, code_changes: str) -> List[str]:
    """
    Parses code blocks and writes them to disk.

    Supports formats:
    ### path/to/file.ext
    ```language
    content
    ```

    Or:
    ```language: path/to/file.ext
    content
    ```

    Returns list of modified/created files.
    """
    modified_files = []

    # Pattern 1: ### header with code block
    blocks = re.findall(r"###\s+(.*?)\n```(?:\w+)?\n(.*?)\n```", code_changes, re.DOTALL)

    for rel_path_str, content in blocks:
        rel_path_str = rel_path_str.strip().lstrip("./")
        # Clean up path name
        rel_path_str = re.sub(r"[`\'*\[\]]", "", rel_path_str)

        if not rel_path_str or not content.strip():
            continue

        full_path = root_path / rel_path_str
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content.strip() + "\n")
            modified_files.append(rel_path_str)
        except Exception as e:
            print(f"Error writing {rel_path_str}: {e}")

    # Pattern 2: Code block with path in header
    blocks2 = re.findall(r"```(?:\w+)?:\s*(.*?)\n(.*?)\n```", code_changes, re.DOTALL)
    for rel_path_str, content in blocks2:
        rel_path_str = rel_path_str.strip().lstrip("./")
        if not rel_path_str or not content.strip():
            continue

        full_path = root_path / rel_path_str
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content.strip() + "\n")
            modified_files.append(rel_path_str)
        except Exception as e:
            print(f"Error writing {rel_path_str}: {e}")

    return list(set(modified_files))  # Deduplicate


def find_similar_files(root_path: Path, filename: str) -> List[str]:
    """Find files with similar names to help locate references."""
    matches = []
    filename_lower = filename.lower()

    for path in root_path.rglob("*"):
        if is_ignored(path):
            continue
        if path.is_file() and filename_lower in path.name.lower():
            matches.append(str(path.relative_to(root_path)))

    return matches[:10]  # Limit to 10 matches
