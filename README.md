
# Human Programming Language

![CI](https://github.com/kieltech2/Human/actions/workflows/ci.yml/badge.svg)

**Created and owned by KielTech**

A human-friendly programming language with plain English syntax.

## Overview

**Human** is an interpreted/compiled language that prioritizes readability and naturalness. It uses plain English constructs with minimal keywords.

## File Extension

`.hm` - Human Language files

## Quick Example

```
print "Hello, World!"

set age to 25
if age is greater than 18
    print "You are an adult"
end if

define greet with name
    print "Hello, " + name + "!"
end define

greet "Alice"
```

## Project Structure

- `lexer.py` - Tokenizes Human language source code
- `parser.py` - Parses tokens into an abstract syntax tree (AST)
- `compiler.py` - Compiles AST to bytecode
- `vm.py` - Virtual machine that executes bytecode
- `interpreter.py` - Main interpreter/entry point
- `examples/` - Example .hm programs

## Installation & Usage

### Quick Install (Recommended)

```bash
# Install globally from PyPI
pip install human-language

# Then run any .hm file from anywhere
human program.hm
```

### Alternative: Direct Execution

```bash
# Run without installation
human program.hm
```

For detailed installation and setup instructions, see [INSTALLATION.md](INSTALLATION.md)

## Language Features

- **Variables**: `set x to 10`
- **Arithmetic**: `+, -, *, /, %`
- **Lists**: `[1, 2, 3]`
- **Dictionaries**: `{name: "Alice", age: 30}`
- **Indexing**: `data["name"]`, `numbers[0]`
- **Conditionals**: `if ... then ... end if`
- **While loops**: `while condition do ... end while`
- **For loops**: `for item in list do ... end for`
- **Functions**: `define myFunc with param1, param2 ... end define`
- **Classes and objects**: `class`, `new`, `this`, method calls like `obj.method()`
- **Imports**: `import "module.hm"`
- **Exception handling**: `try ... catch err ... end try`
- **Builtins**: `len()`, `range()`, `str()`, `int()`, `float()`, `type()`, `env()`, `file_read()`, `file_write()`, `file_exists()`, `path_join()`, `sleep()`, `call_python()`, `log()`, `http_get()`, `http_post()`, `http_put()`, `http_delete()`, `http_route()`, `http_middleware()`, `http_static()`, `http_listen()`, `http_listen_async()`, `http_response()`, `request_body()`, `request_json()`, `request_query()`, `request_headers()`, `request_method()`, `request_path()`, `json_parse()`, `json_stringify()`, `openai_request()`, `openai_chat()`
- **Output**: `print "text"` or `print "Hello," name`
- **Input**: `ask "prompt"`
- **Comments**: `-- this is a comment`

## AI App Helper Example

```
set key to env("OPENAI_API_KEY")
set body to file_read("prompt.txt")
set response to openai_request(key, body)
print response
```

## Example project

A sample AI app is available at `examples/ai_app.hm`:

```
human examples/ai_app.hm
```

A sample web app is available at `examples/web_app.hm`:

```
human examples/web_app
```

## Syntax Highlighting

The repository includes a VS Code language package for `*.hm` files.

- `package.json` contains the extension manifest for Human syntax highlighting.
- `human.tmLanguage.json` defines token patterns for comments, strings, numbers, booleans, keywords, operators, and identifiers.
- `human-language-configuration.json` provides comment, bracket, auto-closing, and folding support.

To use this in VS Code, open the workspace and run the Extension Development Host, or install the extension package from this folder.

## Python Interop (`py_import` / `py_call`)

Human provides direct in-process Python interop via two builtins:

- `py_import(module_name)` — imports a Python module using `importlib.import_module` and returns the module key (string). Raises a runtime error if the module cannot be imported.
- `py_call(module_key, function_name, [args])` — calls `function_name` on the imported module with the provided arguments and returns a Human-friendly representation of the result.

Example (requires `numpy` installed in the same Python environment):

```
set npmod to py_import("numpy")
set s to py_call(npmod, "sum", [[1,2,3]])
print s
```

Wrapper modules are included in `examples/numby.hm` for convenience (e.g. `np_sum`, `np_mean`, `np_matmul`, `np_reshape`, `np_dot`, `np_transpose`). Use `import "examples/numby.hm"` to access them.

Notes:
- This interop runs Python code in-process; only import trusted modules.
- The VM converts common Python types back to Human-friendly types: `numpy` arrays use `.tolist()`, `bytes` are base64 encoded, `datetime` objects are ISO strings, and `pandas` DataFrames/Series convert to dicts. Arbitrary objects are pickled and base64-encoded when possible.
- A subprocess-based wrapper (`tools/np_wrapper.py`) still exists in the repository as an alternate approach but is not used by the VM by default.

## Security & Runtime environment variables for Python interop

Human supports runtime controls to harden in-process Python imports. These variables are read by the VM at startup:

- `HUMAN_PY_IMPORT_ENABLED` (default `1`) — set to `0` to completely disable `py_import` and prevent any in-process Python imports. Recommended for strict production deployments where executing third-party Python code is not allowed.
- `HUMAN_PY_IMPORT_ALLOWLIST` (optional) — a comma-separated list of module names (for example: `numpy,pandas,scipy`). When set, only the exact module names in this allowlist may be imported in-process via `py_import`; attempts to import other modules will raise a `VMException`.
- `HUMAN_PY_FALLBACK` (optional) — a comma-separated list of modules that are eligible to fallback to the subprocess wrapper when an in-process import fails. Note: if `HUMAN_PY_IMPORT_ALLOWLIST` is set, the allowlist must include the module for the VM to attempt an in-process import (and therefore to fall back). In other words, fallback is only attempted for modules that are permitted by the allowlist.

Examples (PowerShell):

```powershell
# Disable all in-process imports
$env:HUMAN_PY_IMPORT_ENABLED = "0"

# Allow only numpy and pandas to be imported in-process
$env:HUMAN_PY_IMPORT_ALLOWLIST = "numpy,pandas"

# Allow numpy to fall back to the subprocess wrapper if in-process import fails
$env:HUMAN_PY_FALLBACK = "numpy"
```

Examples (bash):

```bash
# Disable all in-process imports
export HUMAN_PY_IMPORT_ENABLED=0

# Allow only numpy and pandas
export HUMAN_PY_IMPORT_ALLOWLIST=numpy,pandas

# Allow numpy fallback
export HUMAN_PY_FALLBACK=numpy
```

Recommendations:

- In production, prefer setting `HUMAN_PY_IMPORT_ENABLED=0` if your runtime must never execute third-party Python modules.
- If you need a small set of trusted modules, set `HUMAN_PY_IMPORT_ALLOWLIST` to the minimal set required and keep `HUMAN_PY_IMPORT_ENABLED` at the default (`1`).
- Use `HUMAN_PY_FALLBACK` only for modules you explicitly trust to be run via the repository's subprocess wrappers; fallbacks are intended as an emergency compatibility mechanism and are less efficient and feature-complete than in-process imports.

Behavior note: when both an allowlist and fallback are configured, the VM first checks the allowlist before attempting an import; fallback is attempted only if the module is allowed and the in-process import fails.

Project-level configuration (human.toml)

You can declare the `py_import` policy in a `human.toml` file at the repository root. This is recommended for reproducible project policies that are code-reviewed alongside the project.

Example `human.toml`:

```toml
[py_import]
enabled = true
allowlist = ["numpy", "pandas"]
fallback = ["numpy"]
```

Precedence order: environment variables override project config. Effective order is:

- environment variables (`HUMAN_PY_IMPORT_ENABLED`, `HUMAN_PY_IMPORT_ALLOWLIST`, `HUMAN_PY_FALLBACK`)
- `human.toml` `[py_import]` settings
- built-in defaults (enabled = true, empty allowlist/fallback)

Tooling: a helper script is included at `scripts/validate_import_policy.py` to print the effective policy and optionally validate that allowlisted modules can be imported in the current environment.

Note: a sample project configuration is included at the repository root as `human.toml.sample`. Copy it to `human.toml` and edit as needed for your project.

Production setup
 - Create a virtual environment and install required packages:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

 - Optionally set `HUMAN_PY_FALLBACK` to a comma-separated list of module names that may fallback to subprocess wrappers (for example: `numpy`). Example (PowerShell):

```powershell
$env:HUMAN_PY_FALLBACK = "numpy"
```

 - Run examples (after activating the virtualenv):

```powershell
python -m human_language examples\numby_test.hm
```

Troubleshooting

- If an in-process import fails, run the included health-check to see which modules failed:

```powershell
.\scripts\setup_venv.ps1 -Force   # recreate venv and install deps
.\.venv\Scripts\python scripts\health_check.py
```

- If you cannot install a dependency in-process, you can opt into subprocess fallbacks for specific modules by setting `HUMAN_PY_FALLBACK` (comma-separated). Example:

```powershell
$env:HUMAN_PY_FALLBACK = "numpy"
```

- The `scripts\health_check.py` script prints actionable guidance including commands to recreate the venv or set fallback modules.
