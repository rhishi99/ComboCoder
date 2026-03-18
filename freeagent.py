#!/usr/bin/env python3
"""
FreeAgentDev - Multi-provider AI development agent.

Entry point that routes commands to the CLI.
"""

import sys
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

from freeagentdev.cli import app

if __name__ == "__main__":
    # If a direct task is provided (not a subcommand or option), route it to 'run'
    if len(sys.argv) > 1 and sys.argv[1] not in [
        "onboard", "run", "status", "providers", "--help", "-h", "--version"
    ]:
        sys.argv.insert(1, "run")
    app()
