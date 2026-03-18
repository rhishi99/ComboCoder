"""Enhanced CLI for FreeAgentDev with multi-provider support."""

import typer
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from freeagentdev.core.config_loader import load_config, get_config
from freeagentdev.core.llm_client import LLMClient
from freeagentdev.core.file_ops import FileOperations, get_repo_summary, apply_changes
from freeagentdev.core.task_detector import TaskDetector
from freeagentdev.agents.workflow import FreeAgentWorkflow

app = typer.Typer(help="FreeAgentDev: Your local AI dev agent with multi-provider support.")
console = Console()


@app.command()
def onboard():
    """Generates ONBOARDING.md with setup steps."""
    content = """# ONBOARDING.md - FreeAgentDev

Welcome to **FreeAgentDev**! Your local AI-powered developer agent.

## 🚀 One-Click Setup

### **Windows**
1. Run the PowerShell setup script: `.\\setup_windows.ps1`
2. Add your API key to `freeagentdev/config.yaml`.
3. **Restart terminal** and run `freeagent "task"` anywhere!

### **macOS / Linux**
1. Run the setup script: `bash setup_unix.sh`
2. Follow instructions to add to PATH.
3. Add your API key to `freeagentdev/config.yaml`.
4. **Restart terminal** and run `freeagent "task"` anywhere!

## 🛠 Features
- **🔄 Multi-Provider Fallback**: Automatic switching between Groq, NVIDIA, OpenRouter, etc.
- **🔍 Inquiry Mode**: Automatically detects when you want an explanation instead of code changes.
- **📡 Router Visibility**: Shows exactly which provider and model are working in real-time.
- **🧪 4-Agent Workflow**: Planner, Architect, Engineer, and Reviewer SOP.

## 📋 Example Commands
```bash
# Code Task
freeagent "Create a Python timer script"

# Inquiry Task
freeagent "Explain how the multi-agent workflow works in this project"

# Force Sequential Mode
freeagent "Step by step, create a login form and then the backend" --sequential
```
"""
    with open("ONBOARDING.md", "w", encoding="utf-8") as f:
        f.write(content)
    console.print(Panel("[green]ONBOARDING.md generated successfully![/green]"))


@app.command()
def status():
    """Show provider configuration status."""
    try:
        config = get_config()
        llm = LLMClient()
        status = llm.get_provider_status()

        table = Table(title="Provider Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Configured", style="green")
        table.add_column("Available", style="yellow")
        table.add_column("Errors", style="red")

        for provider, info in status.items():
            configured = "✓" if info["configured"] else "✗"
            available = "✓" if info["available"] else "✗"
            errors = str(info["error_count"]) if info["error_count"] > 0 else "0"
            table.add_row(provider, configured, available, errors)

        console.print(table)

        if not any(info["available"] for info in status.values()):
            console.print("\n[red]No providers available![/red]")
            console.print("[yellow]Set at least one API key environment variable.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")


import warnings
# Suppress Pydantic and other library warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="pydantic")

@app.command(name="run")
def task_run(
    task: str = typer.Argument(..., help="The natural language task you want the agent to perform."),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Force parallel execution"),
    sequential: bool = typer.Option(False, "--sequential", "-s", help="Force sequential execution"),
):
    """Executes a development task using the multi-agent workflow."""
    root_path = Path(os.getcwd())

    try:
        config = load_config()
        llm = LLMClient()
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        raise typer.Exit(code=1)

    # Check for available providers
    provider_status = llm.get_provider_status()
    available = [p for p, info in provider_status.items() if info["available"]]
    if not available:
        console.print("[red]No providers available![/red]")
        console.print("[yellow]Set at least one API key environment variable:[/yellow]")
        console.print("  export GROQ_API_KEY='your-key'")
        console.print("  export NVIDIA_API_KEY='your-key'")
        console.print("  export OPENROUTER_API_KEY='your-key'")
        raise typer.Exit(code=1)

    # Detect task mode
    task_detector = TaskDetector(root_path)

    execution_mode = "auto"
    if parallel:
        execution_mode = "parallel"
    elif sequential:
        execution_mode = "sequential"

    task_analysis = task_detector.analyze_task_structure(task)
    context_docs = task_detector.gather_context_documents()

    console.print(Panel(
        f"[bold blue]🚀 Task:[/bold blue] {task}\n"
        f"[bold blue]📂 Path:[/bold blue] {root_path}\n"
        f"[bold blue]🔧 Mode:[/bold blue] {execution_mode}\n"
        f"[bold blue]📡 Providers:[/bold blue] {', '.join(available)}"
    ))

    if context_docs:
        console.print("[dim]📄 Found context documents (PRD/Specs)[/dim]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True # Keep the terminal clean
    ) as progress:

        # Step 1: Analyze repo
        progress.add_task(description="[cyan]Analyzing repository structure...", total=None)
        summary = get_repo_summary(root_path)

        # Step 2: Build and run workflow
        workflow = FreeAgentWorkflow(llm)
        
        # We'll use a shared task ID for agent updates
        agent_task_id = progress.add_task(description="[cyan]Initializing agents...", total=None)

        try:
            final_state = workflow.run(root_path, task, progress, agent_task_id)
        except Exception as e:
            progress.stop()
            console.print(f"\n[red]Workflow Error: {e}[/red]")
            if "rate" in str(e).lower():
                console.print("[yellow]All providers are rate limited. Please wait a moment and try again.[/yellow]")
            raise typer.Exit(code=1)

        # Step 3: Apply changes
        progress.add_task(description="[cyan]Applying code changes to local files...", total=None)
        modified_files = apply_changes(root_path, final_state.get("code_changes", ""))

    # Show results
    if modified_files:
        console.print(Panel(
            Markdown(final_state.get("code_changes", "No changes")[:2000]),
            title="Applied Changes"
        ))
        console.print(
            f"[bold green]Success![/bold green] "
            f"Modified {len(modified_files)} files: [cyan]{', '.join(modified_files)}[/cyan]"
        )
    else:
        # If no changes, it might be an informational task
        if final_state.get("review_feedback"):
            console.print(Panel(
                Markdown(final_state["review_feedback"]),
                title="Agent Response"
            ))
        else:
            console.print("[yellow]No code changes were applied.[/yellow]")

    # Show review result if it's not the main answer
    if modified_files and final_state.get("review_feedback"):
        if "PASS" in final_state["review_feedback"].upper():
            console.print(f"[green]✓ Review: PASSED[/green]")
        elif "MAX TURNS" in final_state["review_feedback"]:
            console.print(f"[yellow]⚠ Review: Max iterations reached[/yellow]")
        else:
            console.print(f"[yellow]Review feedback:[/yellow] {final_state['review_feedback'][:500]}")


@app.command()
def providers():
    """List all supported providers and their models."""
    console.print(Panel("[bold]Supported Providers[/bold]\n\n"
                       "1. [cyan]Groq[/cyan] - Fastest inference (free tier available)\n"
                       "2. [cyan]NVIDIA NIM[/cyan] - GLM, Kimi, MiniMax, DeepSeek models\n"
                       "3. [cyan]OpenRouter[/cyan] - Aggregates many providers\n"
                       "4. [cyan]Google[/cyan] - Gemini models (generous free tier)\n"
                       "5. [cyan]Cerebras[/cyan] - Ultra-fast inference\n"
                       "6. [cyan]Together[/cyan] - Many open models\n"
                       "7. [cyan]DeepInfra[/cyan] - Cost-effective\n"
                       "8. [cyan]Fireworks[/cyan] - Fast inference\n"
                       "\n[dim]Set environment variables to enable providers.[/dim]"))


@app.command()
def create_file(
    filename: str = typer.Argument(..., help="Name of the file to create"),
    content: str = typer.Argument(..., help="Content to write to the file")
):
    """
    Create a new file with the specified name and content.
    
    Example:
        freeagentdev create_file hello.txt "Hello, World!"
    """
    file_ops = FileOperations()
    try:
        file_ops.create_file(filename, content)
        console.print(Panel(f"[green]File '{filename}' created successfully![/green]"))
    except Exception as e:
        console.print(Panel(f"[red]Error creating file '{filename}': {e}[/red]"))
        raise typer.Exit(code=1)


@app.command()
def init():
    """Initialize FreeAgentDev with a default config.yaml."""
    config_dir = Path(__file__).parent
    config_path = config_dir / "config.yaml"
    
    if config_path.exists():
        console.print(f"[yellow]Configuration file already exists at {config_path}.[/yellow]")
        return

    import yaml
    default_config = {
        "providers": {
            "groq": {
                "api_key_env": "GROQ_API_KEY",
                "models": {
                    "planner": "groq/meta-llama/llama-4-scout-17b-16e-instruct",
                    "architect": "groq/llama-3.3-70b-versatile",
                    "engineer": "groq/qwen/qwen3-32b",
                    "reviewer": "groq/llama-3.3-70b-versatile"
                }
            },
            "nvidia": {
                "api_key_env": "NVIDIA_API_KEY",
                "models": {
                    "planner": "nvidia/meta/llama-3.3-70b-instruct",
                    "architect": "nvidia/meta/llama-3.3-70b-instruct",
                    "engineer": "nvidia/qwen/qwen2.5-coder-32b-instruct",
                    "reviewer": "nvidia/meta/llama-3.3-70b-instruct"
                }
            },
            "openrouter": {
                "api_key_env": "OPENROUTER_API_KEY",
                "models": {
                    "planner": "openrouter/anthropic/claude-4.5-sonnet",
                    "architect": "openrouter/anthropic/claude-4.5-sonnet",
                    "engineer": "openrouter/qwen/qwen3-32b",
                    "reviewer": "openrouter/anthropic/claude-3.5-sonnet"
                }
            }
        },
        "provider_order": ["groq", "nvidia", "openrouter"],
        "llm": {
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_seconds": 120
        },
        "agents": {
            "max_turns": 3,
            "retry_on_failure": True,
            "max_retries_per_request": 3,
            "parallel_execution": True
        },
        "log_level": "info"
    }

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, sort_keys=False)
        console.print(Panel(f"[green]Successfully created default configuration at:[/green]\n{config_path}\n\n"
                           "[yellow]Next steps:[/yellow]\n"
                           "1. Open the file and add your API keys\n"
                           "2. Or set them as environment variables (e.g., OPENROUTER_API_KEY)"))
    except Exception as e:
        console.print(f"[red]Error creating configuration file: {e}[/red]")
        raise typer.Exit(code=1)


@app.callback()
def main():
    """FreeAgentDev: Local AI-powered development agent with multi-provider support."""
    pass


if __name__ == "__main__":
    app()
