"""
Human Language Interpreter - Main entry point
"""

import sys
from pathlib import Path
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler
from .vm import VM

def run_file(filename: str):
    """Run a Human language file"""
    try:
        # Read the source code
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Tokenize
        print(f"[Lexing] {filename}...")
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Parse
        print("[Parsing...]")
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Compile
        print("[Compiling to bytecode...]")
        compiler = Compiler()
        bytecode = compiler.compile(ast)
        
        # Execute
        print("[Executing...]")
        vm = VM(bytecode)
        vm.execute()
        
        print("\n[Done]")
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def repl():
    """Interactive REPL mode"""
    # Banner shown by `human` before calling repl(); keep concise here
    print("Type 'exit' to quit")

    while True:
        try:
            source = input(">>> ")

            cmd = source.strip().lower()
            if cmd == "exit":
                break
            if cmd == "help":
                content = None
                # 1) try current working directory
                cwd_readme = Path.cwd() / "README.md"
                if cwd_readme.exists():
                    content = cwd_readme.read_text(encoding="utf-8")
                else:
                    # 2) walk parents from cwd
                    for p in [Path.cwd()] + list(Path.cwd().parents):
                        cand = p / "README.md"
                        if cand.exists():
                            content = cand.read_text(encoding="utf-8")
                            break
                # 3) try package-relative location
                if content is None:
                    pkg_dir = Path(__file__).resolve().parent
                    # try repo root (package parent) first, then package dir
                    cand = pkg_dir.parent / "README.md"
                    if not cand.exists():
                        cand = pkg_dir / "README.md"
                    if cand.exists():
                        content = cand.read_text(encoding="utf-8")

                if content:
                    print(content)
                else:
                    print("Help: could not find README.md in cwd, parents, or package")
                continue

            if cmd == "license":
                content = None
                cwd_lic = Path.cwd() / "LICENSE"
                if cwd_lic.exists():
                    content = cwd_lic.read_text(encoding="utf-8")
                else:
                    for p in [Path.cwd()] + list(Path.cwd().parents):
                        cand = p / "LICENSE"
                        if cand.exists():
                            content = cand.read_text(encoding="utf-8")
                            break
                if content is None:
                    pkg_dir = Path(__file__).resolve().parent
                    cand = pkg_dir.parent / "LICENSE"
                    if not cand.exists():
                        cand = pkg_dir / "LICENSE"
                    if cand.exists():
                        content = cand.read_text(encoding="utf-8")

                if content:
                    print(content)
                else:
                    print("License: could not find LICENSE in cwd, parents, or package")
                continue

            if not source.strip():
                continue

            # Tokenize
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            # Parse
            parser = Parser(tokens)
            ast = parser.parse()

            # Compile
            compiler = Compiler()
            bytecode = compiler.compile(ast)

            # Execute
            vm = VM(bytecode)
            vm.execute()

        except SyntaxError as e:
            print(f"Syntax Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <file.hm>")
        print("   or: python interpreter.py --repl")
        sys.exit(1)
    
    if sys.argv[1] == "--repl":
        repl()
    else:
        run_file(sys.argv[1])

if __name__ == "__main__":
    main()
