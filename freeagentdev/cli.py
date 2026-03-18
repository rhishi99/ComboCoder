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
from freeagentdev.core.file_ops import get_repo_summary, apply_changes
from freeagentdev.core.task_detector import TaskDetector
from freeagentdev.agents.workflow import FreeAgentWorkflow

app = typer.Typer(help="FreeAgentDev: Your local AI dev agent with multi-provider support.")
console = Console()


@app.command()
def onboard():
    """Generates ONBOARDING.md with setup steps."""
    content = """# ONBOARDING.md - FreeAgentDev

Welcome to **FreeAgentDev**! Your local AI-powered developer agent with multi-provider support.

## 🚀 Setup

1. **Configure API Keys**: Set environment variables for providers you want to use:
   ```bash
   export GROQ_API_KEY="your-key"         # Fastest inference
   export NVIDIA_API_KEY="your-key"       # Wide model variety (GLM, Kimi, MiniMax)
   export OPENROUTER_API_KEY="your-key"   # Many model options
   export GOOGLE_API_KEY="your-key"       # Gemini models
   export CEREBRAS_API_KEY="your-key"     # Ultra-fast
   export TOGETHER_API_KEY="your-key"     # Open models
   ```

2. **Run**: Execute the agent with your task:
   ```bash
   python freeagent.py "Add a hello world python script"
   ```

## 🛠 Features
- **8+ Provider Support**: Groq, NVIDIA NIM, OpenRouter, Google, Cerebras, Together, DeepInfra, Fireworks
- **Automatic Fallback**: Switches providers on rate limits automatically
- **4-Agent Workflow**: Planner, Architect, Engineer, and Reviewer work together
- **Parallel/Sequential Execution**: Automatically detects and handles task complexity
- **Context Awareness**: Reads PRD.md, REQUIREMENTS.md, SPEC.md automatically
- **High Quality Standards**: SOLID principles, clean code, proper error handling

## 📋 Task Modes
- **Parallel**: Use keywords like "parallel", "simultaneously", "concurrently"
- **Sequential**: Use keywords like "step by step", "one after another"
- **Auto**: System detects automatically based on task complexity
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
        console=console
    ) as progress:

        # Step 1: Analyze repo
        progress.add_task(description="[cyan]Analyzing repository structure...", total=None)
        summary = get_repo_summary(root_path)

        # Step 2: Build and run workflow
        progress.add_task(description="[cyan]Running agent workflow (this may take 1-2 mins)...", total=None)
        workflow = FreeAgentWorkflow(llm)

        try:
            final_state = workflow.run(root_path, task)
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
        console.print("[yellow]No code changes were applied. Check the agent's output below.[/yellow]")
        console.print(Markdown(final_state.get("code_changes", "No output")))

    # Show review result
    if final_state.get("review_feedback"):
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


@app.callback()
def main():
    """FreeAgentDev: Local AI-powered development agent with multi-provider support."""
    pass


if __name__ == "__main__":
    app()
