#!/usr/bin/env python3
"""
Command-line interface for the Human programming language.
"""

import sys
import os
from pathlib import Path

# Import from the interpreter module
from .interpreter import run_file, repl
from . import __version__
from importlib import metadata


def main():
    """Main entry point for the 'human' command."""
    # Support --version / -v
    if len(sys.argv) >= 2 and sys.argv[1] in ("--version", "-v"):
        print(f"Human {__version__}")
        sys.exit(0)

    # No arguments -> start interactive REPL
    if len(sys.argv) < 2:
        # Banner similar to Python interactive startup
        print(f"Human {__version__}")
        print('Type "help", or "license" for more information.')
        print()
        repl()
        sys.exit(0)
    
    program_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.isfile(program_file):
        print(f"Error: File '{program_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Run the program
    try:
        run_file(program_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
