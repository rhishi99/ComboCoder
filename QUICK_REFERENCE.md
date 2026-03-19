# FreeAgentDev - Quick Reference Card

**For comprehensive instructions**, see [USERS_GUIDE.md](./USERS_GUIDE.md)

---

## ⚡ 3-Minute Setup

```bash
# 1. Clone
git clone <repo-url>
cd ComboCoder

# 2. Setup (choose your OS)
# Windows:
python -m venv .venv && .venv\Scripts\activate

# Mac/Linux:
python3 -m venv .venv && source .venv/bin/activate

# 3. Install
pip install -r requirements.txt

# 4. Configure (get a free API key from groq.com, then)
cp config.example.yaml config.yaml
# Edit config.yaml and add your API key
```

---

## 🔑 Free API Keys (Pick Any 2)

| Provider | Sign Up | Free Limit | Time |
|----------|---------|-----------|------|
| **Groq** ⭐ | [console.groq.com](https://console.groq.com/) | 500K tokens/day | 2 min |
| **Google** | [aistudio.google.com](https://aistudio.google.com/) | 1.5M tokens/day | 1 min |
| **NVIDIA** | [build.nvidia.com](https://build.nvidia.com/) | $1000 credits/90 days | 5 min |
| **OpenRouter** | [openrouter.ai](https://openrouter.ai/) | Free models | 3 min |

---

## ▶️ Basic Commands

```bash
# Run a task
python freeagent.py "Create a Python script that prints hello world"

# Parallel execution (independent tasks)
python freeagent.py "Create auth AND database schema" --parallel

# Sequential (dependent tasks)
python freeagent.py "Create database, then migrations" --sequential

# Check providers
python freeagent.py providers

# Check status & active provider
python freeagent.py status

# Example output:
# Groq: 120/500k tokens (84%) — *CURRENT PROVIDER*
# Google: 0/1.5M tokens
# NVIDIA: $25.50/$1000 credits (Available)

# During task execution, you'll see:
# 📝 Planner is thinking... (GROQ/llama-3.3-70b)
# 💻 Engineer is writing code... (OPENROUTER/qwen-2.5-coder)
```

---

## 🏗️ How It Works

```
Your Task
   ↓
🔍 PLANNER → Creates execution plan
   ↓
🏗️ ARCHITECT → Designs solution
   ↓
💻 ENGINEER → Writes code
   ↓
✅ REVIEWER → Validates output
```

---

## 🔐 Security Checklist

- ✅ Never commit `config.yaml` (already .gitignored)
- ✅ Never commit `.env` (already .gitignored)
- ✅ Use environment variables for API keys
- ✅ Keep API keys in `.env` file (not in config.yaml)

**Verify before committing**:
```bash
git status  # Should NOT show config.yaml or .env
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "No module named 'freeagentdev'" | Activate venv: `source .venv/bin/activate` |
| "API key invalid" | Re-copy key from provider website |
| "Rate limit exceeded" | System auto-switches to next provider ✓ |
| "Task too slow" | Break into smaller tasks |

---

## 📚 Learn More

- **Complete Setup**: [USERS_GUIDE.md](./USERS_GUIDE.md)
- **Architecture**: [README.md](./README.md#architecture)
- **Troubleshooting**: [USERS_GUIDE.md#troubleshooting](./USERS_GUIDE.md#troubleshooting)

---

## 💡 Pro Tips

1. **Add multiple providers** → Better uptime and higher limits
2. **Use PRD.md** → System reads for context automatically
3. **Break big tasks** → "Create X" then "Create Y" instead of "Create X and Y"
4. **Monitor usage** → `python freeagent.py status` prevents surprises

---

## 🎯 Example Workflow

```bash
# 1. Create a requirements file
cat > PRD.md << 'EOF'
# Build a Todo App

Create a todo app with:
- FastAPI backend
- React frontend
- SQLite database
EOF

# 2. Run the task
python freeagent.py "Build a complete todo app"

# 3. Review generated code
# Check the output and modified files

# 4. Test it
python -m pytest tests/
```

---

**New to this?** → Start with [USERS_GUIDE.md](./USERS_GUIDE.md)

**Ready to code?** → Run `python freeagent.py "Your task"`
