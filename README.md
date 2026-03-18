# 🤖 FreeAgentDev: Your Local AI-Powered Pair Programmer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by LiteLLM](https://img.shields.io/badge/LLM-LiteLLM-orange.svg)](https://github.com/BerriAI/litellm)
[![Workflow: LangGraph](https://img.shields.io/badge/Workflow-LangGraph-green.svg)](https://github.com/langchain-ai/langgraph)

**FreeAgentDev** is a local-first, multi-agent AI development tool that transforms your natural language tasks into production-ready code. It utilizes a sophisticated 4-agent workflow to plan, architect, engineer, and review changes directly on your local files—all while leveraging **free-tier LLM APIs** to keep your costs at zero.

---

## 🌟 Why FreeAgentDev?

*   **🛡️ Local-First & Secure**: Operates directly on your local codebase. No sensitive code is stored in the cloud.
*   **🔄 Automatic Provider Fallback**: If one AI provider (like Groq) hits a rate limit, the system automatically switches to another (like OpenRouter or NVIDIA) without stopping.
*   **🧪 Multi-Agent SOPs**: Inspired by MetaGPT, it uses a team of specialized agents (Planner, Architect, Engineer, Reviewer) to ensure high code quality.
*   **💸 100% Free Tier Optimized**: Specifically tuned to work with high-performance free models like `Qwen-2.5-Coder` and `Llama-3.3`.

---

## 🚀 Fast Onboarding (3-Minute Setup)

### 1. Install Dependencies
Clone the repository and install the required Python packages:
```bash
git clone <your-repo-url>
cd ComboCoder
pip install -r requirements.txt
```

### 2. Initialize Configuration
Generate your local `config.yaml` file:
```bash
python freeagent.py init
```

### 3. Add Your API Keys
Open `freeagentdev/config.yaml` and add at least one free API key. We recommend [OpenRouter](https://openrouter.ai/keys) or [Groq](https://console.groq.com/keys).

**Example:** Setting an environment variable is often easiest:
```bash
# Windows
set OPENROUTER_API_KEY=sk-or-v1-your-key

# macOS / Linux
export OPENROUTER_API_KEY=sk-or-v1-your-key
```

Or edit the file directly:
```yaml
providers:
  openrouter:
    api_key_env: "OPENROUTER_API_KEY"  # Either the env var name OR paste the key here
```

---

## 🛠️ Usage Examples

Navigate to your project folder and run the agent from the command line:

### **General Task**
```bash
python path/to/freeagent.py "Create a modern CSS grid layout for a landing page"
```

### **Bug Fix**
```bash
python path/to/freeagent.py "Fix the broken validation in login.js"
```

### **Code Refactor**
```bash
python path/to/freeagent.py "Refactor the database module to use async/await"
```

---

## 📂 Documentation Hub

| File | Best For... |
| :--- | :--- |
| [**📖 User's Guide**](./USERS_GUIDE.md) | Deep dive into installation, 8+ provider setups, and advanced config. |
| [**🚀 Onboarding**](./ONBOARDING.md) | A simplified walkthrough for first-time users. |
| [**⚡ Quick Reference**](./QUICK_REFERENCE.md) | CLI command "cheat sheet" and common patterns. |
| [**✅ GitHub Checklist**](./GITHUB_CHECKLIST.md) | Best practices for committing agent-generated code safely. |
| [**🏁 Project Completion**](./PROJECT_COMPLETION.md) | Technical architecture overview and system capabilities. |

---

## 🧠 How It Works: The 4-Agent Workflow

FreeAgentDev doesn't just "guess" code. it follows a rigorous **Standard Operating Procedure (SOP)**:

1.  **📝 Planner**: Analyzes your repository and creates a logical step-by-step implementation plan.
2.  **📐 Architect**: Designs the specific file structure and technical specifications required.
3.  **💻 Engineer**: Writes the actual code, reading your local files for context and ensuring compatibility.
4.  **🕵️ Reviewer**: Validates the code against your task. If errors are found, it sends feedback back to the Planner for another iteration (up to 3 times).

---

## 🔒 Security & Privacy

*   **API Keys**: Your `config.yaml` is ignored by Git by default. Never share this file.
*   **Local Data**: The agent only reads files in your current directory to gain context for the task.
*   **Templates**: Use `config.example.yaml` to share configuration structures without sharing keys.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Ready to start?** Run `python freeagent.py onboard` to generate your first local guide!
