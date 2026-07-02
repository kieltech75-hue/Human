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
from .android_packaging import build_android_apk
from .android_native_compiler import build_android_native_apk
from .package_manager import PackageManager, PackageManagerError
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
        sys.argv = ['human', 'examples/android_gui.hm']

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

    if len(sys.argv) >= 2 and sys.argv[1] == "--package-apk-native":
        parser = argparse.ArgumentParser(
            prog="human --package-apk-native",
            description="Generate and optionally build a native Android APK from a Human script.",
        )
        parser.add_argument("script", help="Human script path to compile for Android")
        parser.add_argument("--project-dir", default="android_native_project", help="Output Android project directory")
        parser.add_argument("--package", default="org.human.nativeapp", help="Android package name")
        parser.add_argument("--app-name", default="HumanNativeApp", help="Android application name")
        parser.add_argument("--variant", choices=["debug", "release"], default="debug", help="Build variant")
        parser.add_argument("--build", action="store_true", help="Run Android Gradle build after generating the project")
        args = parser.parse_args(sys.argv[2:])

        build_android_native_apk(
            Path(args.script),
            Path(args.project_dir),
            package_name=args.package,
            app_name=args.app_name,
            variant=args.variant,
            build=args.build,
        )
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] == "--package-apk":
        parser = argparse.ArgumentParser(
            prog="human --package-apk",
            description="Build an Android APK from the Human project using Buildozer.",
        )
        parser.add_argument("--spec", default="buildozer.spec", help="Buildozer spec file")
        parser.add_argument("--target", choices=["debug", "release"], default="debug", help="APK build target")
        args = parser.parse_args(sys.argv[2:])

        build_android_apk(Path(args.spec), args.target)
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] == "--install":
        parser = argparse.ArgumentParser(
            prog="human --install",
            description="Install a Human module from a local path or Git repository.",
        )
        parser.add_argument("package", help="Package name, local path, or Git URL")
        parser.add_argument("--global", dest="global_install", action="store_true", help="Install package into the user-wide Human module directory")
        args = parser.parse_args(sys.argv[2:])
        manager = PackageManager()
        try:
            destination = manager.install(args.package, global_install=args.global_install)
            print(f"Installed {args.package} to {destination}")
            sys.exit(0)
        except PackageManagerError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    if len(sys.argv) >= 2 and sys.argv[1] == "--list-packages":
        parser = argparse.ArgumentParser(
            prog="human --list-packages",
            description="List installed Human packages.",
        )
        parser.add_argument("--global", dest="global_install", action="store_true", help="List packages from the user-wide Human module directory")
        args = parser.parse_args(sys.argv[2:])
        manager = PackageManager()
        packages = manager.list_installed(global_install=args.global_install)
        for pkg in packages:
            print(pkg)
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] == "--remove":
        parser = argparse.ArgumentParser(
            prog="human --remove",
            description="Remove an installed Human package.",
        )
        parser.add_argument("package", help="Installed package name to remove")
        parser.add_argument("--global", dest="global_install", action="store_true", help="Remove package from the user-wide Human module directory")
        args = parser.parse_args(sys.argv[2:])
        manager = PackageManager()
        try:
            manager.remove(args.package, global_install=args.global_install)
            print(f"Removed {args.package}")
            sys.exit(0)
        except PackageManagerError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

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
