# Human Language — Features Reference

This document summarizes the core capabilities of the Human programming language and its runtime. It is intended as a practical reference for developers exploring what Human can do today.

## Table of Contents

- [Interpreter & Compiler](#1-interpreter--compiler)
- [REPL & Debugger](#2-repl--debugger)
- [Natural English Syntax](#3-natural-english-syntax)
- [Core Types & Standard Library](#4-core-types--standard-library)
- [Modules & Imports](#5-modules--imports)
- [Object Support](#6-object-support)
- [Python Interop](#7-python-interop-py_import-py_call)
- [Built-in Web Framework](#8-built-in-web-framework-vm-level)
- [Templates & Static Sites](#9-templates--static-sites)
- [Async & Background Tasks](#10-async--background-tasks)
- [Packaging & Distribution](#11-packaging--distribution)
- [Language Server (LSP)](#12-language-server-lsp)
- [Deployment & Example Hooks](#13-deployment--example-hooks)
- [Examples & Tests](#14-examples--tests)
- [Extensibility](#15-extensibility)

---

## 1. Interpreter & Compiler

- Human executes `.hm` programs using an interpreter backed by a simple bytecode compiler and a lightweight VM.
- The compiler emits function definitions and a bytecode body executed by the VM; the runtime supports both synchronous and async-mode functions.

Example

```hm
print "Hello, Human!"
```

---

## 2. REPL & Debugger

- Interactive REPL with commands for debugging and package management.
- Debugger supports `:debug <file>` to start a file session, breakpoints, `step`, `continue`, and inspection commands: `:vars`, `:stack`, `:pc`.

REPL commands

```
:debug example.hm
:vars
:stack
:pc
```

---

## 3. Natural English Syntax

- Human uses plain-English phrases for common constructs (e.g., `set x to 1`, `if x is greater than 0`, `define foo with x`).
- The goal is readable code close to natural language while remaining unambiguous.

Example

```hm
set age to 25
if age is greater than 18
    print "Adult"
end if
```

---

## 4. Core Types & Standard Library

- Built-in types: `string`, `number` (int/float), `boolean`, `list`, `dict`.
- Standard utilities: file I/O, JSON, subprocess helpers, date/time, and math utilities.

Example

```hm
set data to {name: "Alice", age: 30}
print json_encode(data)
```

---

## 5. Modules & Imports

- Load and reuse `.hm` modules using the language's import mechanisms.
- REPL package manager helps install local or Git-hosted Human modules.

---

## 6. Object Support

- Lightweight classes and instances, method-like calls, and object construction.
- Suitable for structuring programs without heavy OOP ceremony.

---

## 7. Python Interop (`py_import`, `py_call`)

- Integrate with Python by importing Python modules and calling functions directly.
- Useful for leveraging Python ecosystem libraries from Human code.

Example

```hm
set np to py_import("numpy")
set arr to py_call(np, "array", [[1,2,3]])
```

Notes

- `py_import` may be gated by configuration flags and environment variables for security.

---

## 8. Built-in Web Framework (VM-level)

Human's runtime includes simple web helpers exposed as builtins for quick HTTP services and examples.

Key primitives

- `http_route(method, path, handler_name)`: register route to a handler function.
- `http_listen(host, port)` / `http_listen_async`: start a server.
- `http_middleware(handler_name)`: register middlewares that run before handlers.
- `http_static(mount, directory)`: mount static files.
- `render_template(path, context)`: render HTML templates.
- `http_response(status, body, headers)`, `http_json(body)`, `http_redirect(location)` for handler returns.
- Session helpers are available via `request["session"]` and a server-side session store.

Example handler

```hm
define home_handler with request
    set body to render_template("examples/templates/home.html", {title: "Home"})
    return http_response(200, body, {"Content-Type": "text/html; charset=utf-8"})
end define

http_route("GET", "/", "home_handler")
http_listen("127.0.0.1", 8080)
```

Middleware example

```hm
define request_logger with request
    print "[REQUEST]" request["method"] request["path"]
    return request
end define

http_middleware("request_logger")
```

Notes

- Handlers return a response `dict` with `status`, `body`, and `headers`.
- The VM writes responses to the HTTP stream and supports cookies and `Set-Cookie` for sessions.

---

## 9. Templates & Static Sites

- `render_template` loads and renders HTML templates with a context dict.
- `http_static` serves static files from a directory; useful for demos and simple sites.

---

## Production-ready Web Apps

Human includes features that make it suitable for building full production websites and backend services. The runtime exposes builtins for routing, templates, static asset serving, session management, JSON APIs, middleware, and deployment hooks. Key capabilities include:

- Routing via `http_route(method, path, handler)` with path parameters and middleware support
- Server-rendered templates via `render_template(path, context)` and reusable layouts
- Static assets serving with `http_static(mount, directory)` for CSS/JS/images/icons
- Sessions & cookies via `request["session"]` and server-side session storage
- Middleware with `http_middleware` for logging, auth, and request transforms
- Response helpers: `http_response`, `http_json`, `http_redirect`
- Deployment hooks and example handlers (`deploy_start`, `deploy_status`) for CI/CD workflows
- See `examples/production_web_app.hm` for a complete end-to-end demo


---

## 10. Async & Background Tasks

- The VM supports async-mode functions and a task scheduler for background work.
- Useful for long-running jobs or offloading work from request handlers.

---

## 11. Packaging & Distribution
- **Desktop & Mobile Apps:** Human supports desktop GUI apps via a `tkinter` wrapper and Android mobile apps via a Kivy wrapper.
- The project exposes a `human` CLI entry point and packaging helpers for creating native executables.
- Release v0.1.6 ships ready-to-run binaries for Windows, Linux, and macOS, plus a Windows installer helper and PyPI packaging workflow.
- Download the current release assets from [GitHub Releases v0.1.6](https://github.com/kieltech75-hue/Human/releases/tag/v0.1.6).
- The packaging pipeline uses PyInstaller and a dedicated release helper script so the same Human source can produce standalone executables for each platform.

Install example

```bash
pip install human-language
# Run the CLI
human examples/hello_world.hm
```

---

## 12. Language Server (LSP)

- `human-lsp` runs a language server for editor integrations (autocomplete, diagnostics, formatting hooks).

---

## 13. Deployment & Example Hooks

- The `examples/production_web_app.hm` demonstrates deployment hooks, sessions, templates, and static assets.
- Useful as a reference for building production-like demos.

---

## 14. Examples & Tests

- See the `examples/` directory for many sample programs (web apps, AI demo, GUI samples, algorithms).
- `tests/` provide runtime validations and can be used as guidance for expected behavior.

---

## 15. Extensibility

- Add builtins in the VM layer to expose more host capabilities.
- Package Human modules and publish them for reuse in other projects.

---

## Quick Reference: Common Builtins

- `print`, `set`, `if` / `end if`, `for` / `end for`, `define` / `end define`, `return`
- Web: `http_route`, `http_listen`, `http_middleware`, `http_static`, `render_template`, `http_response`, `http_json`, `http_redirect`
- Python interop: `py_import`, `py_call`
- Sessions: `create_session`, `get_session` (exposed through request/response flow)

---

If you'd like, I can:

- Add short runnable examples for each builtin into `examples/features/`.
- Expand any section here into a full `FEATURES/<feature>.md` file.
- Link `README.md` to this `FEATURES.md` (I can create a TOC entry in `README.md`).

Which of those would you like next?