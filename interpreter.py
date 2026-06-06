"""
Human Language Interpreter - Main entry point
"""

import sys
from lexer import Lexer
from parser import Parser
from compiler import Compiler
from vm import VM

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
    print("Human Language Interpreter (REPL)")
    print("Type 'exit' to quit")
    print("-" * 40)
    
    while True:
        try:
            source = input(">>> ")
            
            if source.lower() == "exit":
                break
            
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
