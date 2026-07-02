#!/usr/bin/env python3
"""
Command-line interface for the Human programming language.
"""

import argparse
import sys
import os
from pathlib import Path

from .interpreter import run_file, repl
from .native_packaging import build_executable
from .installer import ensure_self_installed
from . import __version__


def debug_file(script: str, breakpoints=None, verbose: bool = False):
    from .lexer import Lexer
    from .parser import Parser
    from .compiler import Compiler
    from .vm import VM

    if breakpoints is None:
        breakpoints = []

    if not os.path.isfile(script):
        raise FileNotFoundError(script)

    source = Path(script).read_text(encoding="utf-8")
    if verbose:
        print(f"[Lexing] {script}...")
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    if verbose:
        print("[Parsing...]")
    parser = Parser(tokens)
    ast = parser.parse()
    if verbose:
        print("[Compiling to bytecode...]")
    compiler = Compiler()
    bytecode = compiler.compile(ast)
    if verbose:
        print("[Executing...]")

    vm = VM(bytecode)
    for pc in breakpoints:
        vm.add_breakpoint(pc)

    print(f"Debugging {script}")
    print("Commands: run, step, continue, break <pc>, clear, list, locals, stack, pc, help, quit")

    while True:
        if not vm.running:
            print("Program finished.")
            break

        cmd = input("(debug) ").strip()
        if not cmd:
            continue
        if cmd in ("exit", "quit"):
            break
        if cmd == "help":
            print("run      - execute until completion or next breakpoint")
            print("step     - execute a single instruction")
            print("continue - run until the next breakpoint")
            print("break N  - add a breakpoint at instruction index N")
            print("clear    - remove all breakpoints")
            print("list     - list current breakpoints")
            print("locals   - print current frame variables")
            print("stack    - print the runtime stack")
            print("pc       - print current program counter")
            print("quit     - exit the debugger")
            continue
        if cmd.startswith("break "):
            try:
                parts = cmd.split()
                for token in parts[1:]:
                    pc_value = int(token)
                    vm.add_breakpoint(pc_value)
                    print(f"Breakpoint added at PC={pc_value}")
            except ValueError:
                print("Invalid breakpoint. Use: break <pc>")
            continue
        if cmd == "clear":
            vm.clear_breakpoints()
            print("Breakpoints cleared")
            continue
        if cmd == "list":
            print("Breakpoints:", sorted(vm.breakpoints))
            continue
        if cmd == "locals":
            print(vm.get_current_locals())
            continue
        if cmd == "stack":
            print(vm.stack)
            continue
        if cmd == "pc":
            print(f"PC={vm.pc}")
            continue
        if cmd in ("run", "continue"):
            vm.run()
            if not vm.running:
                print("Program finished.")
                break
            print(f"Paused at PC={vm.pc}")
            vm.print_debug_state()
            continue
        if cmd == "step":
            vm.step()
            if not vm.running:
                print("Program finished.")
                break
            vm.print_debug_state()
            continue
        print(f"Unknown debugger command: {cmd}. Type 'help' for commands.")


def main():
    if len(sys.argv) >= 2 and sys.argv[1] in ("--version", "-v"):
        print(f"Human {__version__}")
        sys.exit(0)

    if ensure_self_installed():
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] in ("--android", "--android-gui"):
        print("Android packaging is not available in this build.", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) >= 2 and sys.argv[1] == "--package-native":
        parser = argparse.ArgumentParser(
            prog="human --package-native",
            description="Compile a Human script into a native executable.",
        )
        parser.add_argument("script", help="Human script path to package")
        parser.add_argument("--format", choices=["native"], default="native")
        parser.add_argument("--dist", default="dist", help="Output folder for the executable")
        parser.add_argument("--gui", action="store_true", help="Build a GUI windowed executable")
        parser.add_argument(
            "--bundle-python",
            action="store_true",
            help="Bundle the Python runtime so users do not need a separate Python install",
        )
        parser.add_argument("--name", default=None, help="Name of the output executable (without extension)")
        args = parser.parse_args(sys.argv[2:])

        build_executable(
            Path(args.script),
            Path(args.dist),
            format=args.format,
            gui=args.gui,
            bundle_python=args.bundle_python,
            name=args.name,
        )
        sys.exit(0)



    if len(sys.argv) >= 2 and sys.argv[1] == "--debug":
        parser = argparse.ArgumentParser(
            prog="human --debug",
            description="Run a Human script with an interactive debugger.",
        )
        parser.add_argument("script", help="Human script path to debug")
        parser.add_argument("--breakpoint", type=int, action="append", default=[], help="Add a breakpoint at bytecode instruction index")
        parser.add_argument("--verbose", action="store_true", help="Show compilation and execution progress messages")
        args = parser.parse_args(sys.argv[2:])
        try:
            debug_file(args.script, breakpoints=args.breakpoint, verbose=args.verbose)
            sys.exit(0)
        except FileNotFoundError:
            print(f"Error: File '{args.script}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    if len(sys.argv) < 2:
        print(f"Human {__version__}")
        print('Type "help", or "license" for more information.')
        print()
        repl()
        sys.exit(0)

    if sys.argv[1] == "--repl":
        repl()
        sys.exit(0)

    program_file = sys.argv[1]
    if not os.path.isfile(program_file):
        print(f"Error: File '{program_file}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        run_file(program_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
