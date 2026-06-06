"""
Human Programming Language - A custom language with plain English syntax.

Version: 0.1.0
Author: KielTech
License: MIT
"""

__version__ = "0.1.1"
__author__ = "KielTech"
__license__ = "MIT"

from .interpreter import run_file, repl

__all__ = ["run_file", "repl"]
