#!/usr/bin/env python3
"""
Debug runner for sspec CLI commands.

This script allows debuggers (VS Code) to run sspec commands with breakpoint support.
It serves as the entry point for debugging sspec functionality.

Usage (direct CLI):
    python scripts/debug_runner.py change new
    python scripts/debug_runner.py ask create test --cwd /tmp/test-project
    python scripts/debug_runner.py project status --cwd .

Usage (VS Code prompt - shell-style):
    When prompted in VS Code, enter full command:
    change new --from test-a
    ask create test
    project status

Environment variables:
    DEBUG_CWD: Override working directory (same as --cwd)
"""

import os
import shlex
import sys
from pathlib import Path

# Add src/ to path so sspec module can be imported
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sspec.cli import main


def run() -> None:
    """
    Run sspec with the provided command-line arguments.

    Handles:
    - Shell-style command parsing (supports quoted args with spaces)
    - Converting --cwd to working directory change
    - Delegating to sspec.cli.main()
    """
    # Check for --cwd argument
    cwd = os.environ.get("DEBUG_CWD")

    argv = sys.argv[1:]

    # If single argument that looks like shell-style command, parse it
    # (happens when user enters full command in VS Code prompt)
    if len(argv) == 1 and ' ' in argv[0]:
        argv = shlex.split(argv[0])

    # Parse --cwd from argv if present
    if "--cwd" in argv:
        cwd_idx = argv.index("--cwd")
        if cwd_idx + 1 < len(argv):
            cwd = argv[cwd_idx + 1]
            # Remove --cwd and its value from argv
            argv = argv[:cwd_idx] + argv[cwd_idx + 2:]

    # Change directory if specified
    if cwd:
        os.chdir(cwd)
        print(f"📍 Working directory: {os.getcwd()}", file=sys.stderr)

    # Restore modified argv for Click to parse
    sys.argv = ["sspec"] + argv

    # Call sspec CLI
    main()


if __name__ == "__main__":
    run()
