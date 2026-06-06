# Human Language - Installation & Quick Start

## Installation

### Option 1: Development Installation (Recommended for Development)
```bash
pip install -e .
```

This installs the package in development mode, allowing you to modify the code and test immediately.

### Option 2: Standard Installation
```bash
pip install .
```

This creates a standard installation of the package.

### Verify Installation
After installation, verify the `human` command is available:
```bash
human
```

You should see the help message showing usage instructions.

---

## Usage

Once installed, you can run Human programs simply by typing:

```bash
human program.hm
```

### Examples

Run hello world:
```bash
human examples/hello_world.hm
```

Run fibonacci:
```bash
human examples/fibonacci.hm
```

Run lambda and comprehension tests:
```bash
human examples/lambda_comprehension_test.hm
```

### Running from Any Directory

The `human` command works from anywhere on your system after installation:

```bash
# From your project directory
human myprogram.hm

# From home directory
cd ~
human path/to/myprogram.hm

# With absolute paths
human C:/path/to/myprogram.hm
```

---

## Development

### Setup Development Environment

1. **Clone/Extract the project**
   ```bash
   cd path/to/human-language
   ```

2. **Install in development mode**
   ```bash
   pip install -e .
   ```

3. **Run tests**
   ```bash
   human examples/hello_world.hm
   human examples/lambda_comprehension_test.hm
   human examples/fibonacci.hm
   ```

### Project Structure

```
human_language/
├── __init__.py           # Package initialization
├── __main__.py           # Module execution support (python -m human_language)
├── cli.py                # Command-line interface
├── lexer.py              # Tokenizer
├── parser.py             # Syntax parser
├── ast_nodes.py          # AST node definitions
├── compiler.py           # Bytecode compiler
└── vm.py                 # Virtual machine executor

examples/
├── hello_world.hm
├── variables.hm
├── conditionals.hm
├── fibonacci.hm
├── lambda_comprehension_test.hm
└── ...

setup.py                  # Setup configuration
pyproject.toml           # Modern Python project config
MANIFEST.in              # Packaging manifest
```

---

## Features

### Language Constructs
- ✓ Variables: `set x to 42`
- ✓ Functions: `define add x, y: x + y end`
- ✓ Lambda Functions: `set double to fn x: x * 2`
- ✓ List Comprehensions: `[x * 2 from x in list if x > 5]`
- ✓ Classes: `class Person: define __init__ name: set this.name to name end end`
- ✓ Control Flow: `if`, `else`, `while`, `for`, `loop`
- ✓ Exception Handling: `try`, `catch`
- ✓ Imports: `import module_name`

### Builtin Functions
- I/O: `print`, `ask`
- Collections: `len`, `range`
- Type Conversion: `str`, `int`, `float`, `type`
- HTTP: `http_get`, `http_post`, `http_route`, `http_listen`
- File I/O: `file_read`, `file_write`, `file_exists`
- JSON: `json_parse`, `json_stringify`
- OpenAI: `openai_chat`, `openai_request`
- Utilities: `sleep`, `env`, `call_python`, `log`

---

## Troubleshooting

### Command not found
If you get "human: command not found", reinstall the package:
```bash
pip install --force-reinstall -e .
```

### Import errors
If you see module import errors, ensure you're in the correct directory and the package is properly installed:
```bash
pip install -e .
```

### File not found
Ensure the .hm file path is correct (can be relative or absolute):
```bash
human ./examples/hello_world.hm    # Relative path
human examples/hello_world.hm       # From project root
```

---

## Next Steps

- Create your first Human program in a `.hm` file
- Use syntax highlighting in VS Code by installing the Human Language extension
- Join the community and share your programs

For more information, see [README.md](README.md)
