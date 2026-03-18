# FreeAgentDev: Multi-Provider AI Software Development Agent

A smart, local AI coding assistant that automatically falls back between multiple LLM providers when rate limits are hit. Built for developers who need reliable, autonomous AI assistance directly on their local codebase.

## 🚀 Overview

FreeAgentDev is a **local-first** CLI tool that turns your natural language tasks into working code. It uses a 4-agent workflow (Planner, Architect, Engineer, Reviewer) orchestrated via LangGraph to ensure high-quality, reviewed code changes.

### Key Features
- **Local Execution**: Reads and writes files directly in your current working directory.
- **Multi-Provider Fallback**: Automatically switches between 8+ LLM providers (Groq, NVIDIA, OpenRouter, Gemini, etc.) if rate limits are hit.
- **Agentic Workflow**: Includes dedicated agents for planning, architecture, engineering, and review.
- **Zero Cost**: Optimized for free-tier coding models like `Qwen-2.5-Coder`.

---

## 📖 Documentation Index

For detailed information, please refer to the following guides:

- [**🚀 Onboarding Guide (ONBOARDING.md)**](./ONBOARDING.md): The best place to start. Covers quick setup and core features.
- [**📘 User's Guide (USERS_GUIDE.md)**](./USERS_GUIDE.md): Comprehensive manual covering installation, 8+ provider setups, and advanced usage.
- [**⚡ Quick Reference (QUICK_REFERENCE.md)**](./QUICK_REFERENCE.md): A "cheat sheet" for CLI commands and configuration.
- [**✅ GitHub Checklist (GITHUB_CHECKLIST.md)**](./GITHUB_CHECKLIST.md): Best practices for using FreeAgentDev with GitHub repositories.
- [**🏁 Project Completion (PROJECT_COMPLETION.md)**](./PROJECT_COMPLETION.md): Detailed technical summary of the project architecture and capabilities.

---

## 🛠 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd ComboCoder

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Initialize the configuration and add your API keys:

```bash
# Initialize config.yaml
python freeagent.py init

# Generate the onboarding guide for reference
python freeagent.py onboard
```

Edit `config.yaml` with your API keys (e.g., from [OpenRouter](https://openrouter.ai/keys)).

### 3. Usage

Navigate to any project folder and run:

```bash
# Example: Add a new feature
python path/to/freeagent.py "Add a logout button to the navigation bar"
```

---

## 🏗 Architecture

FreeAgentDev uses a stateful graph to manage the development lifecycle:

1.  **Planner**: Analyzes the task and repository structure to create a step-by-step plan.
2.  **Architect**: Designs the specific file changes and technical structure.
3.  **Engineer**: Implements the code changes directly to your local files.
4.  **Reviewer**: Validates the changes and provides feedback for iteration if necessary.

---

## 🛡 Security & Best Practices

- **Never commit `config.yaml`**: This file contains your private API keys. It is ignored by `.gitignore` by default.
- **Use `config.example.yaml`**: Share this template with others instead of your actual config.
- **Review changes**: While the Reviewer agent validates code, always perform a final manual check before committing agent-generated code.

---

## License

MIT License - See [LICENSE](./LICENSE) file for details.
