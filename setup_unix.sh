#!/bin/bash
# FreeAgentDev Unix One-Click Setup
set -e
CURRENT_DIR=$(pwd)

echo "🤖 Starting FreeAgentDev Setup..."

# 1. Create Virtual Environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# 2. Install Dependencies
echo "📥 Installing dependencies..."
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

# 3. Initialize Config
echo "⚙️ Initializing configuration..."
./.venv/bin/python3 freeagent.py init

# 4. Make wrapper executable
chmod +x freeagent

# 5. Instructions for PATH
echo ""
echo "🚀 SETUP COMPLETE!"
echo "--------------------------------------------------"
echo "1. Add your API key to: freeagentdev/config.yaml"
echo "2. Add this directory to your PATH by adding this line to your ~/.bashrc or ~/.zshrc:"
echo "   export PATH=\"\$PATH:$CURRENT_DIR\""
echo "3. Restart your terminal and run 'freeagent \"task\"' anywhere!"
echo "--------------------------------------------------"
