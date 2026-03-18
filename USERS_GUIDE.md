# FreeAgentDev Users Guide - Complete Step-by-Step Instructions

This comprehensive guide walks you through every step needed to set up and use FreeAgentDev - a multi-provider AI software development agent that automatically switches between multiple LLM providers.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Initial Setup (First Time Users)](#initial-setup-first-time-users)
3. [Getting API Keys](#getting-api-keys)
4. [Configuration](#configuration)
5. [Running Tasks](#running-tasks)
6. [Understanding the Multi-Agent Workflow](#understanding-the-multi-agent-workflow)
7. [Execution Modes](#execution-modes)
8. [Real-World Examples](#real-world-examples)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)

---

## System Requirements

Before starting, ensure your system meets these requirements:

### **1. Python Installation**
- **Version Required**: Python 3.11 or higher (3.12+ recommended)
- **Check your version**:
  ```bash
  python --version
  # or
  python3 --version
  ```
- **If Python is not installed**:
  - **Windows**: Download from [python.org](https://www.python.org/downloads/) and run the installer. ✅ Check "Add Python to PATH"
  - **macOS**: Use Homebrew: `brew install python3`
  - **Linux**: Use your package manager: `sudo apt install python3.11 python3-pip`

### **2. Git (Optional but Recommended)**
- Needed to clone the repository
- **Check if installed**:
  ```bash
  git --version
  ```
- **If not installed**:
  - **Windows/macOS/Linux**: Download from [git-scm.com](https://git-scm.com/)

### **3. Text Editor for Configuration**
- Any text editor works (VS Code, Notepad++, Sublime, etc.)
- Or use command-line editors (nano, vim)

---

## Initial Setup (First Time Users)

### **Step 1: Clone or Download the Repository**

#### Option A: Clone with Git
```bash
git clone https://github.com/yourusername/ComboCoder.git
cd ComboCoder
```

#### Option B: Download as ZIP
1. Go to the GitHub repository
2. Click **Code** → **Download ZIP**
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder

### **Step 2: Create a Virtual Environment**

A virtual environment isolates project dependencies from your system Python. This prevents conflicts.

#### Windows (Command Prompt)
```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
⚠️ **If PowerShell gives an error about execution policies**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating again
```

#### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**✅ How to confirm it's activated?** Your terminal prompt should show `(.venv)` at the beginning.

### **Step 3: Install Dependencies**

With the virtual environment active, install all required packages:

```bash
pip install -r requirements.txt
```

This installs:
- `litellm` - Multi-provider LLM support
- `pyyaml` - Configuration file handling
- `typer` - Command-line interface
- `rich` - Beautiful terminal output
- `langgraph` - Agent workflow orchestration
- `python-dotenv` - Environment variable loading
- And other required dependencies

**⏱️ Expected time**: 2-5 minutes depending on your internet speed

### **Step 4: Verify Installation**

```bash
python -m pip list
# Should show: litellm, pyyaml, typer, rich, langgraph, python-dotenv
```

---

## Getting API Keys

You need **at least one API key** from a supported provider. The more providers you configure, the better - the system automatically falls back when rate limits are hit.

### **Quick Start (Recommended for Beginners)**

Start with **Groq** - it's the easiest and fastest:

#### **1. Create a Groq Account**
1. Go to [console.groq.com](https://console.groq.com/)
2. Click **Sign Up** (or **Login** if you have an account)
3. Complete email verification
4. Accept terms

#### **2. Get Your API Key**
1. Click your profile icon (top-right) → **API Keys**
2. Click **Create API Key**
3. Copy the generated key (starts with `gsk_`)
4. 🔒 **Save it somewhere safe** - you won't see it again!

### **All Supported Providers with Free Tiers**

| Provider | Sign Up | Free Tier | Best For | Time to Setup |
|----------|---------|-----------|----------|---------------|
| **Groq** | [console.groq.com](https://console.groq.com/) | 14,400 requests/day (500K tokens/day) | ⭐ **Start here** - Fastest | 2 min |
| **Google AI Studio** | [aistudio.google.com](https://aistudio.google.com/) | 1,500 requests/day (1.5M tokens/day) | Gemini models | 1 min |
| **NVIDIA NIM** | [build.nvidia.com](https://build.nvidia.com/) | $1000 credits (90 days) | Diverse models | 5 min |
| **OpenRouter** | [openrouter.ai](https://openrouter.ai/) | Various free models | Model variety | 3 min |
| **Cerebras** | [cerebras.ai](https://cerebras.ai/) | Free tier | Ultra-fast inference | 3 min |
| **Together AI** | [together.ai](https://together.ai/) | Free credits | Open-source models | 3 min |
| **DeepInfra** | [deepinfra.com](https://deepinfra.com/) | Pay-per-use (cheap) | Cost-effective | 2 min |

**👉 Recommendation**: Start with **Groq + Google AI Studio** for maximum reliability and token availability.

---

## Configuration

### **Step 1: Create Your Configuration File**

Instead of creating the file manually, use the built-in `init` command to generate a default configuration file with the correct structure and model settings:

```bash
# Run from the ComboCoder directory
python freeagent.py init
```

This will create a `config.yaml` file inside the `freeagentdev/` directory.

### **Step 2: Edit freeagentdev/config.yaml**

Open `freeagentdev/config.yaml` in your text editor and add your API keys. Here's a snippet of what the file looks like:

```yaml
providers:
  groq:
    api_key_env: "GROQ_API_KEY"        # Environment variable name
    models:
      planner: "groq/meta-llama/llama-4-scout-17b-16e-instruct"
      architect: "groq/llama-3.3-70b-versatile"
      engineer: "groq/qwen/qwen3-32b"
      reviewer: "groq/llama-3.3-70b-versatile"
    rate_limit:
      requests_per_minute: 30
      tokens_per_minute: 15000
```

### **Step 3: Add Your API Keys**

You have two ways to add your keys:

#### **Option A: Using Environment Variables (Recommended - Most Secure)**

1. Create a `.env` file in the `ComboCoder` directory:
   ```bash
   # .env file
   GROQ_API_KEY=gsk_your_actual_key_here
   OPENROUTER_API_KEY=sk-or-v1-your_key_here
   NVIDIA_API_KEY=nvapi-your_key_here
   ```

2. The system will automatically load these keys when you run the agent.

#### **Option B: Pasting Directly in config.yaml**

You can also paste the keys directly into the `api_key_env` field in `freeagentdev/config.yaml`:

```yaml
providers:
  groq:
    api_key_env: "gsk_your_actual_key_here" # Paste key here
```

**⚠️ SECURITY NOTICE**: Your `config.yaml` and `.env` files are already in `.gitignore` so they won't be committed to Git. Never share these files or upload them to GitHub.
#### **Option B: Direct Key in config.yaml (Easier for Local Development)**

```yaml
providers:
  groq:
    api_key: "gsk_your_actual_key_here"  # Paste your key here directly
    api_key_env: ""
```

**⚠️ WARNING**: Never commit `config.yaml` with actual keys to Git! (It's in `.gitignore`)

### **Step 3: Set Provider Priority Order**

Edit this section to choose which providers to use and in what order:

```yaml
provider_order:
  - groq        # Try first (fastest, most free tokens)
  - google      # Second fallback
  - nvidia      # Third fallback
  - openrouter  # Last resort
```

The system tries providers in this order. If one hits a rate limit, it automatically switches to the next.

### **Step 4: Verify Configuration**

Test that your configuration is correct:

```bash
python freeagent.py providers
```

Expected output:
```
✓ Groq (CONFIGURED) - llama-3.3-70b-versatile
✓ Google (CONFIGURED) - gemini-2.0-flash
✓ NVIDIA (CONFIGURED) - qwen2.5-coder-32b-instruct
```

If you see ✗ next to a provider, check that:
- API key is correct
- Spelling matches config.yaml exactly
- Environment variable is set (if using `.env`)

---

## Running Tasks

### **Basic Task Execution**

#### **Example 1: Simple Task**
```bash
python freeagent.py "Create a Python script that prints hello world"
```

#### **Example 2: Complex Task with Auto-Detection**
```bash
python freeagent.py "Build a REST API with user authentication"
```

The system automatically detects complexity and adjusts execution strategy.

### **Available Commands**

#### **1. Run a Task**
```bash
# Basic
python freeagent.py "Your task description here"

# Force parallel execution (multiple agents work simultaneously)
python freeagent.py "Create UI components and database schema" --parallel

# Force sequential execution (one after another)
python freeagent.py "Setup database, then create models" --sequential
```

#### **2. Check Provider Status**
```bash
python freeagent.py status
```

Shows:
- Which providers are available
- Current rate limit usage
- Estimated time until limits reset

#### **3. List All Providers**
```bash
python freeagent.py providers
```

Shows all configured providers with their models.

#### **4. Generate Onboarding Document**
```bash
python freeagent.py onboard
```

Generates a team onboarding guide specific to your configuration.

### **Understanding Output**

When you run a task, you'll see output like:

```
🔍 PLANNER: Analyzing task requirements...
✓ Created implementation plan (3 steps)

🏗️  ARCHITECT: Designing technical solution...
✓ Generated architecture diagram

💻 ENGINEER: Writing code...
✓ Created 5 files

✅ REVIEWER: Validating implementation...
✓ All checks passed
```

Each emoji indicates which agent is working:
- 🔍 **Planner** - Analyzing requirements
- 🏗️ **Architect** - Designing solution
- 💻 **Engineer** - Writing code
- ✅ **Reviewer** - Validating output

---

## Understanding the Multi-Agent Workflow

The system uses **4 specialized AI agents** that work together:

### **1. Planner Agent** 🔍
**What it does**: Analyzes your task and creates a step-by-step execution plan

**Example output**:
```
Task: "Add user authentication"

Plan:
1. Create User model
2. Implement registration endpoint
3. Implement login endpoint
4. Add JWT token generation
5. Add authentication middleware
```

**Why it matters**: Ensures the task is broken down correctly before expensive code generation.

### **2. Architect Agent** 🏗️
**What it does**: Designs the technical solution, including file structure, data models, and APIs

**Example output**:
```
Architecture:
├── models/
│   └── User.py          # User data model
├── routes/
│   └── auth.py          # Authentication endpoints
├── middleware/
│   └── jwt_handler.py   # JWT token validation
└── config.py            # Configuration
```

**Why it matters**: Ensures code is well-structured before writing begins.

### **3. Engineer Agent** 💻
**What it does**: Writes the actual production-quality code

**Example output**:
```python
@app.post("/register")
async def register(user: UserCreate):
    # Validates email uniqueness
    # Hashes password securely
    # Stores in database
    # Returns JWT token
```

**Why it matters**: Generates clean, tested, documented code following best practices.

### **4. Reviewer Agent** ✅
**What it does**: Validates the implementation against requirements and coding standards

**Checks performed**:
- ✓ Does it meet all requirements?
- ✓ Are there security vulnerabilities?
- ✓ Does code follow best practices?
- ✓ Is error handling adequate?
- ✓ Are tests included?

**Why it matters**: Catches issues before they reach production.

---

## Execution Modes

The system can run tasks in different ways:

### **1. Auto-Detect Mode (Default)**

System analyzes task complexity and chooses:
- **Parallel**: For independent tasks (can run simultaneously)
- **Sequential**: For dependent tasks (must run in order)

```bash
python freeagent.py "Your task"
# Automatically chooses best mode
```

### **2. Parallel Execution**

Multiple agents work **at the same time** to speed up large tasks.

```bash
python freeagent.py "Create authentication AND database schema" --parallel
```

**Use when**: Task has independent components that don't depend on each other

**Example tasks**:
- "Create login form AND create API endpoints"
- "Write tests AND write documentation"
- "Design database schema AND create frontend components"

**Speed improvement**: 30-50% faster than sequential

### **3. Sequential Execution**

Agents work **one after another**, with later steps depending on earlier results.

```bash
python freeagent.py "First create database schema, then build API" --sequential
```

**Use when**: Later tasks depend on earlier tasks being complete

**Example tasks**:
- "Create database, then write migration scripts"
- "Setup project structure, then write tests"
- "Create data models, then build API endpoints"

---

## Real-World Examples

### **Example 1: Create a Todo App**

```bash
python freeagent.py "Create a simple todo app with React frontend and FastAPI backend"
```

**Expected workflow**:
1. Planner breaks it into: frontend setup, backend setup, API endpoints, database
2. Architect designs: React component structure, FastAPI project layout, database schema
3. Engineer writes: React components, FastAPI routes, database models
4. Reviewer checks: functionality, error handling, security, code quality

### **Example 2: Add Feature to Existing Project**

First, create a `PRD.md` file with your requirements:

```markdown
# Product Requirements Document

## Feature: User Profiles

### Requirements
1. Users can view their profile
2. Users can edit their name and bio
3. Profile picture upload support
4. Display user stats (created projects, followers)

### Non-Functional Requirements
- Must be fast (< 200ms load time)
- Mobile responsive
- Secure file upload validation
```

Then run:
```bash
python freeagent.py "Implement user profile feature"
```

The system automatically reads `PRD.md` for context.

### **Example 3: Parallel Component Creation**

```bash
python freeagent.py "Create LoginForm component, SignupForm component, and ProfileCard component in parallel" --parallel
```

All three components are created simultaneously since they're independent.

### **Example 4: Fix a Bug with Context**

Create a `REQUIREMENTS.md`:
```markdown
# Bug: Login not working after 10 PM

## Symptoms
- Users can't login after 10 PM UTC
- Error: "Session timeout"
- Works fine during other hours

## Environment
- Using JWT tokens with 1 hour expiry
- Server in UTC timezone
```

Run:
```bash
python freeagent.py "Debug and fix the 10 PM login issue"
```

---

## Troubleshooting

### **Problem: "No module named 'freeagentdev'"**

**Cause**: Virtual environment not activated or dependencies not installed

**Solution**:
```bash
# 1. Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows

# 2. Reinstall dependencies
pip install -r requirements.txt
```

### **Problem: "Provider not available" or "API key invalid"**

**Cause**: API key not configured correctly

**Solution**:
```bash
# 1. Verify API key is correct
# Go to provider website and copy key again

# 2. Check configuration
python freeagent.py providers

# 3. If using .env file, verify it exists:
ls .env  # macOS/Linux
dir .env  # Windows
```

### **Problem: "Rate limit exceeded"**

**Cause**: Hit provider's daily/hourly limit

**Expected behavior**: System automatically switches to next provider ✅

**Solution - Add more providers**:
1. Sign up for another provider
2. Get API key
3. Add to `config.yaml`
4. Reorder `provider_order` to try different providers first

### **Problem: Task is taking too long**

**Possible causes**:
- ⏳ Large task (normal - can take 5-15 minutes)
- 🔗 Slow internet connection
- 🚫 Provider is overloaded

**Solutions**:
1. **Break into smaller tasks**: Instead of "Build entire app", do "Create authentication module"
2. **Use faster providers**: Groq is usually fastest
3. **Check provider status**: Run `python freeagent.py status`

### **Problem: "Execution policy" error on PowerShell**

**Cause**: PowerShell security policy blocking script execution

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating virtual environment again
.venv\Scripts\Activate.ps1
```

### **Problem: Task failed or incomplete**

**Debug steps**:
```bash
# 1. Try again (temporary glitch)
python freeagent.py "Your task"

# 2. Try with different provider
# Edit config.yaml - move a different provider to top of provider_order

# 3. Break into smaller task
python freeagent.py "First part of task"

# 4. Check logs (if verbose output available)
python freeagent.py "Your task" -v
```

---

## Security Best Practices

### **🔐 API Key Management**

#### **DO:**
✅ Use `.env` file for local development
```bash
GROQ_API_KEY=gsk_xxxxx
```

✅ Use environment variables in production
```bash
export GROQ_API_KEY="gsk_xxxxx"
```

✅ Rotate keys regularly
- Go to provider website
- Generate new key
- Update .env file
- Delete old key from provider

✅ Monitor usage
```bash
python freeagent.py status
```

#### **DON'T:**
❌ Put actual API keys in code
❌ Commit config.yaml with keys to Git
❌ Share API keys via email/chat
❌ Store keys in plain text files

### **🛡️ File Security**

**Files that MUST NOT be committed to Git:**
- `config.yaml` ✔️ Already in .gitignore
- `.env` ✔️ Already in .gitignore
- `progress/` folder ✔️ Already in .gitignore
- `workspace/` folder ✔️ Already in .gitignore

**Verify with**:
```bash
git status
# Should NOT show config.yaml or .env
```

### **🔍 Protecting Generated Code**

When the system generates code:
1. Review it before deploying
2. Check for hardcoded secrets
3. Run security scans
4. Test thoroughly

---

## Advanced Usage

### **Using as a Python Library**

Instead of CLI, use in your Python code:

```python
from freeagentdev.core.llm_client import LLMClient
from freeagentdev.core.config_loader import ConfigLoader

# Load configuration
config = ConfigLoader()
client = LLMClient(config)

# Make request (auto-fallback to next provider if rate limited)
response = client.complete(
    prompt="Analyze this code for security issues",
    role="reviewer"
)

print(response.text)
```

### **Custom Provider Configuration**

Edit `config.yaml` to customize models per role:

```yaml
providers:
  groq:
    models:
      planner: "groq/llama-3.3-70b-versatile"      # Best for planning
      architect: "groq/llama-3.3-70b-versatile"    # Best for architecture
      engineer: "groq/llama-3.1-70b-versatile"     # Best for coding
      reviewer: "groq/llama-3.3-70b-versatile"     # Best for reviews
```

---

## Next Steps

1. **Complete initial setup**: Follow [Initial Setup](#initial-setup-first-time-users)
2. **Get API keys**: Follow [Getting API Keys](#getting-api-keys)
3. **Configure**: Follow [Configuration](#configuration)
4. **Test**: Run `python freeagent.py "Hello world"` to verify everything works
5. **Use**: Start with simple tasks, then progress to complex ones
6. **Optimize**: Monitor token usage with `python freeagent.py status`

---

## Need Help?

1. **Check Troubleshooting**: Section [Troubleshooting](#troubleshooting)
2. **Verify configuration**: `python freeagent.py providers`
3. **Check provider status**: `python freeagent.py status`
4. **Review logs**: Enable verbose output

---

## Summary

**FreeAgentDev** lets you:
- ✅ Execute complex coding tasks automatically
- ✅ Use multiple AI providers with automatic fallback
- ✅ Leverage 4 specialized agents (Planner, Architect, Engineer, Reviewer)
- ✅ Choose parallel or sequential execution
- ✅ Work with free tier API keys
- ✅ Scale from simple to complex tasks

**Start now**: Follow the [Initial Setup](#initial-setup-first-time-users) section!
