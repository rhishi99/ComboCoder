# ONBOARDING.md - FreeAgentDev

Welcome to **FreeAgentDev**! Your local AI-powered developer agent.

## 🚀 One-Click Setup

### **Windows**
1. Run the PowerShell setup script: `.\setup_windows.ps1`
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
