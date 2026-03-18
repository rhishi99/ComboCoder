# FreeAgentDev - Multi-Provider AI Developer Agent

Local AI-powered developer agent with multi-provider support, automatic fallback, and high software development standards.

## 📖 Complete Documentation

**For complete step-by-step instructions**, see [USERS_GUIDE.md](./USERS_GUIDE.md)

The detailed guide covers:
- System requirements and installation
- Getting API keys from 8+ providers
- Virtual environment setup (Windows/Mac/Linux)
- Configuration with security best practices
- Real-world usage examples
- Troubleshooting guide
- Multi-agent workflow explanation

---



1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys** (at least one):
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Run**:
   ```bash
   python freeagent.py "Add a hello world python script"
   ```

## 🔑 Supported Providers (All Free Tiers Available)

| Provider | Best For | Free Tier | Get Key |
|----------|----------|-----------|---------|
| **Groq** | Fastest inference | 500K tokens/day | [console.groq.com](https://console.groq.com/) |
| **NVIDIA NIM** | Model variety (GLM, Kimi, MiniMax, DeepSeek) | 1000 credits (90 days) | [build.nvidia.com](https://build.nvidia.com/) |
| **Google** | Gemini, generous limits | 1.5M tokens/day | [aistudio.google.com](https://aistudio.google.com/) |
| **OpenRouter** | Many models, aggregator | Various free models | [openrouter.ai](https://openrouter.ai/) |
| **Cerebras** | Ultra-fast | Free tier | [cerebras.ai](https://cerebras.ai/) |
| **Together** | Open models | Free credits | [together.ai](https://api.together.xyz/) |
| **DeepInfra** | Cost-effective | Pay-per-use | [deepinfra.com](https://deepinfra.com/) |
| **Fireworks** | Fast inference | Free credits | [fireworks.ai](https://fireworks.ai/) |

## 🛠 Features

### Multi-Provider Support
- **8+ providers** with automatic switching on rate limits
- **Resilient operation** - continues even if one provider fails
- **Rate limit handling** - tracks usage and waits appropriately

### 4-Agent Workflow
1. **Planner** → Analyzes requirements, creates implementation plan
2. **Architect** → Designs technical specifications
3. **Engineer** → Writes production-quality code
4. **Reviewer** → Validates against requirements and standards

### Execution Modes
- **Auto-detect**: System determines best mode based on task complexity
- **Parallel**: Use keywords like "parallel", "simultaneously", "concurrently"
- **Sequential**: Use "step by step" or let complex tasks auto-detect

### Context Awareness
Automatically reads these files if present in your repo:
- `PRD.md`, `REQUIREMENTS.md`, `SPEC.md`
- `docs/prd.md`, `docs/requirements.md`

### High Quality Standards
- SOLID principles
- Clean code conventions
- Proper error handling
- Type hints
- Documentation

## 📋 CLI Commands

```bash
# Run a task
python freeagent.py "Your task here"

# Force parallel execution
python freeagent.py "Create multiple components" --parallel

# Force sequential execution
python freeagent.py "Complex feature" --sequential

# Check provider status
python freeagent.py status

# List providers
python freeagent.py providers

# Generate this onboarding file
python freeagent.py onboard
```

## 💡 Tips

1. **Multiple API Keys**: Configure multiple providers for best reliability - the system will fallback automatically.

2. **PRD Integration**: Create a `PRD.md` file in your repo root - the agent will read it for context.

3. **Complex Tasks**: For large tasks, the system automatically parallelizes work across agents.

4. **Rate Limits**: If you hit limits, the system automatically tries the next provider. Configure multiple keys for uninterrupted operation.

## 🔧 Configuration

Edit `freeagentdev/config.yaml` to:
- Change provider priority order
- Set different models for each agent role
- Adjust rate limit thresholds
- Configure parallel execution settings

## 📁 Project Structure

```
.
├── freeagent.py          # Entry point
├── requirements.txt      # Dependencies
├── .env.example          # Environment template
├── freeagentdev/
│   ├── cli.py           # CLI commands
│   ├── config.yaml      # Provider & agent config
│   ├── core/
│   │   ├── config_loader.py    # Configuration management
│   │   ├── llm_client.py       # Multi-provider LLM client
│   │   ├── file_ops.py         # File operations
│   │   └── task_detector.py    # Task analysis
│   └── agents/
│       ├── base.py      # Base agent class
│       ├── roles.py     # Planner, Architect, Engineer, Reviewer
│       └── workflow.py  # LangGraph orchestration
```
