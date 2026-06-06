"""
Human Language Virtual Machine - Executes bytecode
"""

import http.server
import os
import json
import socketserver
import subprocess
import threading
import time
import urllib.request
import urllib.parse
import importlib
import base64
import pickle
import datetime as _dt
import logging
try:
    import tomllib as _tomllib
except Exception:
    try:
        import tomli as _tomllib
    except Exception:
        try:
            import toml as _tomllib
        except Exception:
            _tomllib = None
try:
    import tomllib as _tomllib
except Exception:
    _tomllib = None
from typing import List, Dict, Any, Tuple
from .compiler import Bytecode, Opcode
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler
from .ast_nodes import *

class VMException(Exception):
    pass

class VM:
    def __init__(self, bytecode: Bytecode):
        self._logger = logging.getLogger(__name__)
        self.bytecode = bytecode
        self.stack: List[Any] = []
        self.frames: List[Dict[str, Any]] = [
            {'vars': {}, 'return_value': None, 'returning': False, 'name': '<global>'}
        ]
        self.handler_stack: List[int] = []
        self.imported_modules = set()
        self.py_modules: Dict[str, Any] = {}
        # Load project config from human.toml if present (tomllib required on older/newer python)
        config = {}
        config_path = os.path.join(os.getcwd(), 'human.toml')
        if os.path.exists(config_path):
            if _tomllib is not None:
                try:
                    with open(config_path, 'rb') as f:
                        # tomllib/tomli/toml all provide load(file) semantics
                        config = _tomllib.load(f)
                except Exception:
                    config = {}
            else:
                # No TOML parser available; warn user to install a small dependency
                self._logger.warning(
                    "human.toml found but no TOML parser available. Install 'tomli' or 'toml', or run on Python 3.11+ to enable project config parsing."
                )

        # Start with values from project config (if provided)
        py_import_cfg = config.get('py_import', {}) if isinstance(config, dict) else {}
        cfg_enabled = py_import_cfg.get('enabled', None)
        cfg_allowlist = py_import_cfg.get('allowlist', []) or []
        cfg_fallback = py_import_cfg.get('fallback', []) or []

        # Modules that are allowed to fallback to subprocess wrappers when in-process import fails.
        # Can be configured via environment variable HUMAN_PY_FALLBACK (comma-separated names)
        fallback_env = os.environ.get('HUMAN_PY_FALLBACK', None)
        if fallback_env is not None:
            self.py_fallback_modules = set([m.strip() for m in fallback_env.split(',') if m.strip()])
        else:
            self.py_fallback_modules = set([m for m in cfg_fallback if isinstance(m, str)])

        # Optional allowlist for py_import. If non-empty, only modules listed here can be imported in-process.
        allow_env = os.environ.get('HUMAN_PY_IMPORT_ALLOWLIST', None)
        if allow_env is not None:
            self.py_import_allowlist = set([m.strip() for m in allow_env.split(',') if m.strip()])
        else:
            self.py_import_allowlist = set([m for m in cfg_allowlist if isinstance(m, str)])

        # Feature flag to disable py_import entirely in production: set HUMAN_PY_IMPORT_ENABLED=0 to disable.
        env_enabled = os.environ.get('HUMAN_PY_IMPORT_ENABLED', None)
        if env_enabled is not None:
            self.py_import_enabled = env_enabled != '0'
        elif cfg_enabled is not None:
            self.py_import_enabled = bool(cfg_enabled)
        else:
            self.py_import_enabled = True
        self.http_routes: List[Tuple[str, str, str]] = []
        self.http_middlewares: List[str] = []
        self.http_static: List[Tuple[str, str]] = []
        self.http_server: Any = None
        self.http_lock = threading.Lock()
        self.current_http_request: Dict[str, Any] = {}
        self.pc = 0
        self.running = True

    def current_frame(self) -> Dict[str, Any]:
        return self.frames[-1]

    def ensure_var_index(self, name: str) -> int:
        if name not in self.bytecode.var_indices:
            self.bytecode.var_indices[name] = len(self.bytecode.var_indices)
        return self.bytecode.var_indices[name]

    def get_var(self, var_idx: int):
        for frame in reversed(self.frames):
            if var_idx in frame['vars']:
                return frame['vars'][var_idx]
        return None

    def set_var(self, var_idx: int, value: Any):
        if len(self.frames) > 1:
            self.current_frame()['vars'][var_idx] = value
        else:
            self.frames[0]['vars'][var_idx] = value

    def execute(self):
        while self.running and self.pc < len(self.bytecode.instructions):
            opcode, arg = self.bytecode.instructions[self.pc]
            self.pc += 1

            try:
                if opcode == Opcode.LOAD_CONST:
                    self.stack.append(self.bytecode.constants[arg])

                elif opcode == Opcode.LOAD_VAR:
                    self.stack.append(self.get_var(arg))

                elif opcode == Opcode.STORE_VAR:
                    value = self.stack.pop()
                    self.set_var(arg, value)

                elif opcode == Opcode.MAKE_LIST:
                    values = [self.stack.pop() for _ in range(arg)][::-1]
                    self.stack.append(values)

                elif opcode == Opcode.MAKE_DICT:
                    result = {}
                    for _ in range(arg):
                        value = self.stack.pop()
                        key = self.stack.pop()
                        result[key] = value
                    self.stack.append(result)

                elif opcode == Opcode.LOAD_INDEX:
                    index = self.stack.pop()
                    collection = self.stack.pop()
                    self.stack.append(self.load_index(collection, index))

                elif opcode == Opcode.SLICE:
                    # Stack: collection, start, end, step  (step may be None)
                    step = self.stack.pop()
                    end = self.stack.pop()
                    start = self.stack.pop()
                    collection = self.stack.pop()
                    self.stack.append(self.load_slice(collection, start, end, step))

                elif opcode == Opcode.STORE_INDEX:
                    value = self.stack.pop()
                    index = self.stack.pop()
                    collection = self.stack.pop()
                    self.store_index(collection, index, value)

                elif opcode == Opcode.LEN:
                    value = self.stack.pop()
                    self.stack.append(self.get_length(value))

                elif opcode == Opcode.ADD:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    if isinstance(a, str) or isinstance(b, str):
                        self.stack.append(str(a) + str(b))
                    else:
                        self.stack.append(a + b)

                elif opcode == Opcode.SUB:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.append(a - b)

                elif opcode == Opcode.MUL:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.append(a * b)

                elif opcode == Opcode.DIV:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    if b == 0:
                        raise VMException("Division by zero")
                    self.stack.append(a / b)

                elif opcode == Opcode.MOD:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.append(a % b)

                elif opcode == Opcode.NEG:
                    a = self.stack.pop()
                    self.stack.append(-a)

                elif opcode == Opcode.COMPARE_EQ:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.append(a == b)

                elif opcode == Opcode.COMPARE_GT:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.append(a > b)

                elif opcode == Opcode.COMPARE_LT:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.append(a < b)

                elif opcode == Opcode.LOGIC_AND:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.append(a and b)

                elif opcode == Opcode.LOGIC_OR:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.append(a or b)

                elif opcode == Opcode.LOGIC_NOT:
                    a = self.stack.pop()
                    self.stack.append(not a)

                elif opcode == Opcode.JUMP:
                    self.pc = arg

                elif opcode == Opcode.JUMP_IF_FALSE:
                    condition = self.stack.pop()
                    if not self.is_truthy(condition):
                        self.pc = arg

                elif opcode == Opcode.JUMP_IF_TRUE:
                    condition = self.stack.pop()
                    if self.is_truthy(condition):
                        self.pc = arg

                elif opcode == Opcode.PUSH_HANDLER:
                    self.handler_stack.append(arg)

                elif opcode == Opcode.POP_HANDLER:
                    if self.handler_stack:
                        self.handler_stack.pop()

                elif opcode == Opcode.PRINT:
                    args = [self.stack.pop() for _ in range(arg)][::-1]
                    print(" ".join(str(a) for a in args))

                elif opcode == Opcode.INPUT:
                    prompt = self.stack.pop()
                    user_input = input(str(prompt) + " ")
                    self.stack.append(user_input)

                elif opcode == Opcode.CALL:
                    name, count = arg
                    call_args = [self.stack.pop() for _ in range(count)][::-1]
                    # Check if this is a lambda variable call
                    var_idx = self.bytecode.var_indices.get(name)
                    if var_idx is not None:
                        func_obj = self.get_var(var_idx)
                        if isinstance(func_obj, dict) and func_obj.get('__lambda__'):
                            self.stack.append(self.call_lambda(func_obj, call_args))
                        else:
                            self.stack.append(self.call_function(name, call_args))
                    else:
                        self.stack.append(self.call_function(name, call_args))

                elif opcode == Opcode.CALL_METHOD:
                    method_name, count = arg
                    call_args = [self.stack.pop() for _ in range(count)][::-1]
                    obj = self.stack.pop()
                    self.stack.append(self.call_method(obj, method_name, call_args))

                elif opcode == Opcode.NEW:
                    class_name, count = arg
                    new_args = [self.stack.pop() for _ in range(count)][::-1]
                    self.stack.append(self.create_instance(class_name, new_args))

                elif opcode == Opcode.MAKE_LAMBDA:
                    params, body = arg
                    self.stack.append({'__lambda__': True, 'params': params, 'body': body})

                elif opcode == Opcode.LIST_COMP:
                    var, element, condition = arg
                    iterable = self.stack.pop()
                    result = []
                    for item in iterable:
                        var_idx = self.ensure_var_index(var)
                        self.set_var(var_idx, item)
                        if condition is None or self.is_truthy(self.evaluate_ast(condition)):
                            result.append(self.evaluate_ast(element))
                    self.stack.append(result)

                elif opcode == Opcode.IMPORT:
                    path = self.stack.pop()
                    self.import_module(path)

                elif opcode == Opcode.RETURN:
                    self.current_frame()['returning'] = True
                    self.current_frame()['return_value'] = self.stack.pop() if self.stack else None
                    return

                elif opcode == Opcode.POP:
                    if self.stack:
                        self.stack.pop()

                elif opcode == Opcode.HALT:
                    self.running = False

                elif opcode == Opcode.NOP:
                    pass

            except Exception as e:
                if self.handler_stack:
                    catch_pc = self.handler_stack.pop()
                    self.stack.append(str(e))
                    self.pc = catch_pc
                    continue
                raise VMException(f"Runtime error at pc={self.pc-1}: {str(e)}")

    def load_index(self, collection: Any, index: Any):
        if isinstance(collection, dict):
            if '__fields__' in collection and index in collection['__fields__']:
                return collection['__fields__'][index]
            return collection.get(index)
        if isinstance(collection, list) or isinstance(collection, str):
            return collection[index]
        raise VMException(f"Cannot index into {type(collection).__name__}")

    def store_index(self, collection: Any, index: Any, value: Any):
        if isinstance(collection, dict):
            if '__fields__' in collection:
                collection['__fields__'][index] = value
                return
            collection[index] = value
            return
        if isinstance(collection, list):
            collection[index] = value
            return
        raise VMException(f"Cannot assign into {type(collection).__name__}")

    def load_slice(self, collection: Any, start: Any, end: Any, step: Any):
        # Normalize slice parameters to ints or None
        s = None if start is None else int(start)
        e = None if end is None else int(end)
        st = None if step is None else int(step)

        if isinstance(collection, dict):
            # Preserve insertion order: slice keys and build sub-dict
            keys = list(collection.keys())[s:e:st]
            return {k: collection[k] for k in keys}

        if isinstance(collection, (list, str)):
            return collection[s:e:st]

        raise VMException(f"Cannot slice {type(collection).__name__}")

    def get_length(self, value: Any) -> int:
        if isinstance(value, (str, list, dict)):
            return len(value)
        raise VMException(f"Cannot get length of {type(value).__name__}")

    def is_truthy(self, value) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if value is None:
            return False
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True

    def call_function(self, name: str, args: List[Any]):
        if name in self.bytecode.functions:
            func_info = self.bytecode.functions[name]
            params = func_info['params']
            if len(args) != len(params):
                raise VMException(f"Function '{name}' expected {len(params)} arguments, got {len(args)}")

            frame = {'vars': {}, 'return_value': None, 'returning': False, 'name': name}
            for param, value in zip(params, args):
                idx = self.ensure_var_index(param)
                frame['vars'][idx] = value
            self.frames.append(frame)
            self.execute_ast_block(func_info['node'].body)
            self.frames.pop()
            return frame['return_value']

        return self.call_builtin(name, args)

    def call_lambda(self, lambda_obj: Dict[str, Any], args: List[Any]):
        params = lambda_obj.get('params', [])
        body = lambda_obj.get('body')
        
        if len(args) != len(params):
            raise VMException(f"Lambda expected {len(params)} arguments, got {len(args)}")
        
        frame = {'vars': {}, 'return_value': None, 'returning': False, 'name': '<lambda>'}
        for param, value in zip(params, args):
            idx = self.ensure_var_index(param)
            frame['vars'][idx] = value
        self.frames.append(frame)
        result = self.evaluate_ast(body)
        self.frames.pop()
        return result

    def call_method(self, obj: Any, method_name: str, args: List[Any]):
        # String methods
        if isinstance(obj, str):
            if method_name == "upper":
                return obj.upper()
            elif method_name == "lower":
                return obj.lower()
            elif method_name == "split":
                separator = args[0] if args else None
                if separator is None:
                    return obj.split()
                return obj.split(separator)
            elif method_name == "replace":
                if len(args) < 2:
                    raise VMException("replace() requires 2 arguments (old, new)")
                return obj.replace(args[0], args[1])
            elif method_name == "strip":
                return obj.strip()
            elif method_name == "startswith":
                if not args:
                    raise VMException("startswith() requires 1 argument")
                return obj.startswith(args[0])
            elif method_name == "endswith":
                if not args:
                    raise VMException("endswith() requires 1 argument")
                return obj.endswith(args[0])
            elif method_name == "find":
                if not args:
                    raise VMException("find() requires 1 argument")
                return obj.find(args[0])
            elif method_name == "count":
                if not args:
                    raise VMException("count() requires 1 argument")
                return obj.count(args[0])
            elif method_name == "join":
                if not args or not isinstance(args[0], list):
                    raise VMException("join() requires a list argument")
                return obj.join(str(x) for x in args[0])
            elif method_name == "contains":
                if not args:
                    raise VMException("contains() requires 1 argument")
                return args[0] in obj
            else:
                raise VMException(f"String has no method '{method_name}'")
        
        # List methods
        if isinstance(obj, list):
            if method_name == "append":
                if not args:
                    raise VMException("append() requires 1 argument")
                obj.append(args[0])
                return None
            elif method_name == "pop":
                if not obj:
                    raise VMException("pop from empty list")
                return obj.pop()
            elif method_name == "extend":
                if not args or not isinstance(args[0], list):
                    raise VMException("extend() requires a list argument")
                obj.extend(args[0])
                return None
            elif method_name == "index":
                if not args:
                    raise VMException("index() requires 1 argument")
                return obj.index(args[0])
            elif method_name == "count":
                if not args:
                    raise VMException("count() requires 1 argument")
                return obj.count(args[0])
            elif method_name == "reverse":
                obj.reverse()
                return None
            elif method_name == "clear":
                obj.clear()
                return None
            elif method_name == "insert":
                if len(args) < 2:
                    raise VMException("insert() requires 2 arguments (index, value)")
                obj.insert(args[0], args[1])
                return None
            else:
                raise VMException(f"List has no method '{method_name}'")
        
        # Dict methods
        if isinstance(obj, dict):
            if method_name == "keys":
                return list(obj.keys())
            elif method_name == "values":
                return list(obj.values())
            elif method_name == "items":
                return [[k, v] for k, v in obj.items()]
            elif method_name == "get":
                if not args:
                    raise VMException("get() requires at least 1 argument")
                default = args[1] if len(args) > 1 else None
                return obj.get(args[0], default)
            elif method_name == "pop":
                if not args:
                    raise VMException("pop() requires 1 argument")
                default = args[1] if len(args) > 1 else None
                return obj.pop(args[0], default)
            elif method_name == "clear":
                obj.clear()
                return None
            elif method_name == "update":
                if not args or not isinstance(args[0], dict):
                    raise VMException("update() requires a dict argument")
                obj.update(args[0])
                return None
            else:
                raise VMException(f"Dict has no method '{method_name}'")
        
        # Object methods (classes)
        if isinstance(obj, dict) and '__methods__' in obj:
            methods = obj['__methods__']
            if method_name in methods:
                method_node = methods[method_name]
                frame = {'vars': {}, 'return_value': None, 'returning': False, 'name': method_name}
                this_idx = self.ensure_var_index('this')
                frame['vars'][this_idx] = obj
                for param, value in zip(method_node.parameters, args):
                    idx = self.ensure_var_index(param)
                    frame['vars'][idx] = value
                self.frames.append(frame)
                self.execute_ast_block(method_node.body)
                self.frames.pop()
                return frame['return_value']

        raise VMException(f"Method '{method_name}' not found on {type(obj).__name__}")

    def create_instance(self, class_name: str, args: List[Any]):
        if class_name not in self.bytecode.classes:
            raise VMException(f"Class '{class_name}' not found")

        class_node = self.bytecode.classes[class_name]['node']
        instance = {'__class__': class_name, '__methods__': {}, '__fields__': {}}
        for stmt in class_node.body:
            if isinstance(stmt, FunctionDef):
                instance['__methods__'][stmt.name] = stmt

        if 'init' in instance['__methods__']:
            self.call_method(instance, 'init', args)

        return instance

    def import_module(self, path: str):
        if not path.endswith('.hm'):
            path = f"{path}.hm"

        normalized = os.path.normpath(path)
        if normalized in self.imported_modules:
            return
        self.imported_modules.add(normalized)

        if not os.path.exists(normalized):
            raise VMException(f"Cannot import module '{path}'")

        with open(normalized, 'r', encoding='utf-8') as f:
            source = f.read()

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        compiler = Compiler()
        module_bytecode = compiler.compile(ast)

        shared_functions = {**self.bytecode.functions, **module_bytecode.functions}
        shared_classes = {**self.bytecode.classes, **module_bytecode.classes}

        self.bytecode.functions = shared_functions
        self.bytecode.classes = shared_classes

        # Remap module variable indices into this VM's var index table so STORE/LOAD use consistent indices
        mod_var_indices = dict(module_bytecode.var_indices)
        remap = {}
        for name, idx in mod_var_indices.items():
            if name not in self.bytecode.var_indices:
                self.bytecode.var_indices[name] = len(self.bytecode.var_indices)
            remap[idx] = self.bytecode.var_indices[name]

        # Patch numeric var indices in module instructions
        new_instructions = []
        for opcode, arg in module_bytecode.instructions:
            if opcode in (Opcode.LOAD_VAR, Opcode.STORE_VAR):
                new_arg = remap.get(arg, arg)
                new_instructions.append((opcode, new_arg))
            else:
                new_instructions.append((opcode, arg))
        module_bytecode.instructions = new_instructions

        # Debug: list functions available after merging
        print("[import_module] functions:", list(self.bytecode.functions.keys()))

        import_vm = VM(module_bytecode)
        import_vm.frames = self.frames
        import_vm.handler_stack = self.handler_stack
        import_vm.imported_modules = self.imported_modules
        import_vm.bytecode.functions = shared_functions
        import_vm.bytecode.classes = shared_classes
        # Share python interop module registry so imports inside modules persist
        import_vm.py_modules = self.py_modules
        import_vm.execute()

    def execute_ast_block(self, statements: List[Any]):
        for stmt in statements:
            if self.current_frame()['returning']:
                break
            self.execute_ast_statement(stmt)

    def execute_ast_statement(self, node: Any):
        if isinstance(node, Assignment):
            value = self.evaluate_ast(node.value)
            if isinstance(node.target, Identifier):
                idx = self.ensure_var_index(node.target.name)
                self.set_var(idx, value)
            elif isinstance(node.target, IndexAccess):
                target_obj = self.evaluate_ast(node.target.collection)
                index_value = self.evaluate_ast(node.target.index)
                self.store_index(target_obj, index_value, value)
            else:
                raise VMException(f"Unsupported assignment target: {type(node.target).__name__}")
        elif isinstance(node, IfStatement):
            condition = self.evaluate_ast(node.condition)
            if self.is_truthy(condition):
                self.execute_ast_block(node.then_block)
            elif node.else_block:
                self.execute_ast_block(node.else_block)
        elif isinstance(node, LoopStatement):
            start = self.evaluate_ast(node.start)
            end = self.evaluate_ast(node.end)
            loop_var = self.bytecode.var_indices[f"__loop_var_{self.bytecode.var_indices.get('__loop_counter', 0)}"]
        elif isinstance(node, WhileStatement):
            while self.is_truthy(self.evaluate_ast(node.condition)) and not self.current_frame()['returning']:
                self.execute_ast_block(node.body)
        elif isinstance(node, ForInStatement):
            iterable = self.evaluate_ast(node.iterable)
            current_var_idx = self.bytecode.var_indices[node.variable]
            for item in iterable:
                self.set_var(current_var_idx, item)
                if self.current_frame()['returning']:
                    break
        elif isinstance(node, FunctionDef):
            self.bytecode.functions[node.name] = {'params': node.parameters, 'node': node}
        elif isinstance(node, ClassDef):
            self.bytecode.classes[node.name] = {'node': node}
        elif isinstance(node, ReturnStatement):
            self.current_frame()['return_value'] = self.evaluate_ast(node.value) if node.value else None
            self.current_frame()['returning'] = True
        elif isinstance(node, PrintStatement):
            args = [self.evaluate_ast(arg) for arg in node.arguments]
            print(" ".join(str(a) for a in args))
        elif isinstance(node, AskStatement):
            prompt = self.evaluate_ast(node.prompt)
            self.current_frame()['return_value'] = input(str(prompt) + " ")
        elif isinstance(node, ImportStatement):
            path = node.path
            self.import_module(path)
        elif isinstance(node, TryCatchStatement):
            try:
                self.execute_ast_block(node.try_block)
            except Exception as e:
                if node.catch_var:
                    self.set_var(self.bytecode.var_indices[node.catch_var], str(e))
                if node.catch_block:
                    self.execute_ast_block(node.catch_block)
        elif isinstance(node, FunctionCall):
            self.evaluate_ast(node)
        elif isinstance(node, MethodCall):
            self.evaluate_ast(node)
        elif isinstance(node, NewExpression):
            self.evaluate_ast(node)
        elif isinstance(node, BreakStatement):
            raise VMException("Break is not supported in AST execution")
        elif isinstance(node, ContinueStatement):
            raise VMException("Continue is not supported in AST execution")
        else:
            self.evaluate_ast(node)

    def evaluate_ast(self, node: Any):
        if isinstance(node, NumberLiteral):
            return node.value
        if isinstance(node, StringLiteral):
            return node.value
        if isinstance(node, BooleanLiteral):
            return node.value
        if isinstance(node, ListLiteral):
            return [self.evaluate_ast(item) for item in node.elements]
        if isinstance(node, DictLiteral):
            return {key: self.evaluate_ast(value) for key, value in node.pairs}
        if isinstance(node, Identifier):
            return self.get_var(self.ensure_var_index(node.name))
        if isinstance(node, BinaryOp):
            left = self.evaluate_ast(node.left)
            right = self.evaluate_ast(node.right)
            if node.operator == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            if node.operator == '-':
                return left - right
            if node.operator == '*':
                return left * right
            if node.operator == '/':
                if right == 0:
                    raise VMException("Division by zero")
                return left / right
            if node.operator == '%':
                return left % right
        if isinstance(node, UnaryOp):
            operand = self.evaluate_ast(node.operand)
            if node.operator == '-':
                return -operand
            if node.operator == 'not':
                return not operand
        if isinstance(node, Comparison):
            left = self.evaluate_ast(node.left)
            right = self.evaluate_ast(node.right)
            if node.operator == 'equal' or node.operator == 'is':
                return left == right
            if node.operator == 'greater':
                return left > right
            if node.operator == 'less':
                return left < right
            if node.operator == 'and':
                return left and right
            if node.operator == 'or':
                return left or right
        if isinstance(node, IndexAccess):
            collection = self.evaluate_ast(node.collection)
            index = self.evaluate_ast(node.index)
            return self.load_index(collection, index)
        if isinstance(node, FunctionCall):
            args = [self.evaluate_ast(arg) for arg in node.arguments]
            # Check if this is a lambda variable call
            var_idx = self.bytecode.var_indices.get(node.name)
            if var_idx is not None:
                func_obj = self.get_var(var_idx)
                if isinstance(func_obj, dict) and func_obj.get('__lambda__'):
                    return self.call_lambda(func_obj, args)
            return self.call_function(node.name, args)
        if isinstance(node, MethodCall):
            obj = self.evaluate_ast(node.object)
            args = [self.evaluate_ast(arg) for arg in node.arguments]
            return self.call_method(obj, node.method, args)
        if isinstance(node, NewExpression):
            args = [self.evaluate_ast(arg) for arg in node.arguments]
            return self.create_instance(node.class_name, args)
        if isinstance(node, ListComprehension):
            iterable = self.evaluate_ast(node.iterable)
            result = []
            var_idx = self.ensure_var_index(node.variable)
            for item in iterable:
                self.set_var(var_idx, item)
                if node.condition is None or self.is_truthy(self.evaluate_ast(node.condition)):
                    result.append(self.evaluate_ast(node.element))
            return result
        if isinstance(node, LambdaExpression):
            return {'__lambda__': True, 'params': node.parameters, 'body': node.body}

        raise VMException(f"Unsupported AST node type: {type(node).__name__}")

    def http_get(self, url: str, headers: Any = None) -> str:
        if headers is None:
            headers = {}
        if not isinstance(headers, dict):
            raise VMException("http_get headers must be a dictionary")
        request = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(request) as response:
            return response.read().decode('utf-8')

    def http_post(self, url: str, body: Any = '', headers: Any = None) -> str:
        if headers is None:
            headers = {}
        if not isinstance(headers, dict):
            raise VMException("http_post headers must be a dictionary")
        if isinstance(body, dict):
            data = json.dumps(body).encode('utf-8')
            headers.setdefault('Content-Type', 'application/json')
        else:
            data = str(body).encode('utf-8')
        request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(request) as response:
            return response.read().decode('utf-8')

    def http_request(self, url: str, body: Any = '', headers: Any = None, method: str = 'GET') -> str:
        if headers is None:
            headers = {}
        if not isinstance(headers, dict):
            raise VMException('http_request headers must be a dictionary')
        data = None
        if method in ('POST', 'PUT', 'PATCH'):
            if isinstance(body, dict):
                data = json.dumps(body).encode('utf-8')
                headers.setdefault('Content-Type', 'application/json')
            else:
                data = str(body).encode('utf-8')
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(request) as response:
            return response.read().decode('utf-8')

    def openai_request(self, api_key: str, prompt: str, model: str = 'gpt-4.1-mini', temperature: float = 0.7) -> str:
        payload = {
            'model': model,
            'input': prompt,
            'temperature': float(temperature),
        }
        return self.call_openai_api(api_key, payload)

    def openai_chat(self, api_key: str, messages: Any, model: str = 'gpt-4.1-mini', temperature: float = 0.7) -> str:
        if not isinstance(messages, list):
            raise VMException('openai_chat messages must be a list of dictionaries')
        payload = {
            'model': model,
            'messages': messages,
            'temperature': float(temperature),
        }
        return self.call_openai_api(api_key, payload)

    def env(self, name: str, default: Any = None) -> Any:
        return os.environ.get(name, default)

    def http_route(self, method: str, path: str, handler_name: str) -> str:
        self.http_routes.append((method.upper(), path, handler_name))
        return f"route registered {method.upper()} {path} -> {handler_name}"

    def http_response(self, status: int, body: Any, headers: Any = None) -> dict:
        if headers is None:
            headers = {}
        return {'status': status, 'body': body, 'headers': headers}

    def http_listen(self, host: str, port: Any) -> str:
        port = int(port)
        handler_class = self.make_http_handler()
        with socketserver.ThreadingTCPServer((host, port), handler_class) as httpd:
            self.http_server = httpd
            message = f"Listening on http://{host}:{port}"
            print(message)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.shutdown()
                print('Server stopped')
            return message

    def http_listen_async(self, host: str, port: Any) -> str:
        port = int(port)
        handler_class = self.make_http_handler()
        self.http_server = socketserver.ThreadingTCPServer((host, port), handler_class)
        thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
        thread.start()
        return f"Listening asynchronously on http://{host}:{port}"

    def http_middleware(self, handler_name: str) -> str:
        self.http_middlewares.append(handler_name)
        return f"middleware registered {handler_name}"

    def http_static(self, mount: str, directory: str) -> str:
        mount = mount.rstrip('/') or '/'
        self.http_static.append((mount, directory))
        return f"static route registered {mount} -> {directory}"

    def normalize_path(self, path: str) -> str:
        if not path.startswith('/'):
            path = '/' + path
        return path.rstrip('/') or '/'

    def match_route_pattern(self, route_path: str, request_path: str) -> Any:
        route_path = self.normalize_path(route_path)
        request_path = self.normalize_path(request_path)

        route_segments = route_path.strip('/').split('/') if route_path != '/' else []
        request_segments = request_path.strip('/').split('/') if request_path != '/' else []

        if len(route_segments) != len(request_segments):
            return None

        params: Dict[str, str] = {}
        for route_segment, request_segment in zip(route_segments, request_segments):
            if route_segment.startswith(':'):
                params[route_segment[1:]] = request_segment
            elif route_segment != request_segment:
                return None

        return params

    def serve_static_file(self, mount: str, directory: str, request_path: str) -> Any:
        mount = self.normalize_path(mount)
        if not request_path.startswith(mount):
            return None
        relative_path = request_path[len(mount):]
        if relative_path.startswith('/'):
            relative_path = relative_path[1:]
        file_path = os.path.normpath(os.path.join(directory, relative_path))
        directory_path = os.path.abspath(directory)
        if not file_path.startswith(directory_path):
            return {'status': 403, 'body': 'Forbidden', 'headers': {'Content-Type': 'text/plain'}}
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return None
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            content_type = self.guess_content_type(file_path)
            body = content.decode('utf-8', errors='replace')
            return {'status': 200, 'body': body, 'headers': {'Content-Type': content_type}}
        except Exception as e:
            return {'status': 500, 'body': f'Error reading static file: {str(e)}', 'headers': {'Content-Type': 'text/plain'}}

    def guess_content_type(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        return {
            '.html': 'text/html; charset=utf-8',
            '.htm': 'text/html; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.json': 'application/json; charset=utf-8',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.svg': 'image/svg+xml',
            '.txt': 'text/plain; charset=utf-8',
        }.get(ext, 'application/octet-stream')

    def make_http_handler(self):
        vm = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def handle_request(self, method: str):
                parsed = urllib.parse.urlparse(self.path)
                query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
                query = {k: v[0] if len(v) == 1 else v for k, v in query.items()}
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length).decode('utf-8') if length else ''
                request = {
                    'method': method,
                    'path': parsed.path,
                    'raw_path': self.path,
                    'query': query,
                    'headers': dict(self.headers),
                    'body': body,
                }
                response = vm.dispatch_http_request(method, parsed.path, request)
                self.send_response(response.get('status', 200))
                for header, value in response.get('headers', {}).items():
                    self.send_header(header, str(value))
                if 'Content-Type' not in response.get('headers', {}):
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                body_output = response.get('body', '')
                if isinstance(body_output, dict) or isinstance(body_output, list):
                    body_output = json.dumps(body_output)
                self.wfile.write(str(body_output).encode('utf-8'))

            def do_GET(self):
                self.handle_request('GET')

            def do_POST(self):
                self.handle_request('POST')

            def do_PUT(self):
                self.handle_request('PUT')

            def do_DELETE(self):
                self.handle_request('DELETE')

            def log_message(self, format, *args):
                pass

        return Handler

    def dispatch_http_request(self, method: str, path: str, request: dict) -> dict:
        route = None
        for route_method, route_path, handler_name in self.http_routes:
            if route_method == method and route_path == path:
                route = handler_name
                break
        # Static file handling takes precedence before dynamic routes
        for mount, directory in self.http_static:
            static_response = self.serve_static_file(mount, directory, path)
            if static_response is not None:
                return static_response

        matched_handler = None
        params: Dict[str, str] = {}

        for route_method, route_path, handler_name in self.http_routes:
            if route_method != method:
                continue
            route_params = self.match_route_pattern(route_path, path)
            if route_params is not None:
                matched_handler = handler_name
                params = route_params
                break

        if matched_handler is None:
            return {'status': 404, 'body': f'No route for {method} {path}', 'headers': {'Content-Type': 'text/plain'}}

        request['params'] = params
        self.current_http_request = request
        with self.http_lock:
            for middleware_name in self.http_middlewares:
                middleware_result = self.call_function(middleware_name, [request])
                if isinstance(middleware_result, dict) and 'body' in middleware_result:
                    self.current_http_request = {}
                    return middleware_result
                if isinstance(middleware_result, dict):
                    request = middleware_result
                    self.current_http_request = request
            result = self.call_function(matched_handler, [request])
        self.current_http_request = {}

        if isinstance(result, dict) and 'body' in result:
            return result
        if result is None:
            return {'status': 204, 'body': '', 'headers': {'Content-Type': 'text/plain'}}
        return {'status': 200, 'body': result, 'headers': {'Content-Type': 'text/plain'}}

    def request_body(self) -> str:
        return self.current_http_request.get('body', '')

    def request_json(self) -> Any:
        body = self.current_http_request.get('body', '')
        try:
            return json.loads(body) if body else None
        except json.JSONDecodeError:
            raise VMException('Request body is not valid JSON')

    def request_query(self) -> dict:
        return self.current_http_request.get('query', {})

    def request_headers(self) -> dict:
        return self.current_http_request.get('headers', {})

    def request_method(self) -> str:
        return self.current_http_request.get('method', '')

    def request_path(self) -> str:
        return self.current_http_request.get('path', '')

    def file_read(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def file_write(self, path: str, content: Any) -> str:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(content))
        return path

    def file_exists(self, path: str) -> bool:
        return os.path.exists(path)

    def path_join(self, *parts: Any) -> str:
        return os.path.join(*(str(part) for part in parts))

    def sleep(self, seconds: Any) -> None:
        time.sleep(float(seconds))
        return None

    def call_python(self, script_path: str, args: Any = None) -> str:
        if args is None:
            args = []
        if isinstance(args, str):
            args = [args]
        if not isinstance(args, list):
            raise VMException('call_python args must be a list or string')
        result = subprocess.run([
            'python',
            script_path,
            *[str(arg) for arg in args]
        ], capture_output=True, text=True)
        if result.returncode != 0:
            raise VMException(f"Python script failed: {result.stderr.strip()}")
        return result.stdout.strip()

    # Python interop helpers
    def _to_python_arg(self, value: Any):
        # Convert Human runtime values into Python-friendly types
        if isinstance(value, dict):
            # detect bytes wrapper
            if '__bytes__' in value:
                return base64.b64decode(value['__bytes__'])
            # detect pickled object wrapper
            if '__pickle__' in value:
                try:
                    return pickle.loads(base64.b64decode(value['__pickle__']))
                except Exception:
                    return value
            return {k: self._to_python_arg(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._to_python_arg(v) for v in value]
        return value

    def _from_python_result(self, value: Any):
        # Convert Python objects to Human-friendly JSON-serializable types
        try:
            import numpy as _np
        except Exception:
            _np = None
        try:
            import pandas as _pd
        except Exception:
            _pd = None

        if _np is not None and hasattr(value, 'tolist'):
            try:
                return value.tolist()
            except Exception:
                pass

        if isinstance(value, bytes):
            return {'__bytes__': base64.b64encode(value).decode('ascii')}
        if isinstance(value, _dt.datetime):
            return {'__datetime__': value.isoformat()}
        if _pd is not None and isinstance(value, (_pd.DataFrame, _pd.Series)):
            try:
                return {'__pandas__': value.to_dict()}
            except Exception:
                pass
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return [self._from_python_result(v) for v in value]
        if isinstance(value, dict):
            return {k: self._from_python_result(v) for k, v in value.items()}
        # For arbitrary objects, attempt to pickle and base64-encode
        try:
            pickled = pickle.dumps(value)
            return {'__pickle__': base64.b64encode(pickled).decode('ascii'), '__type__': type(value).__name__}
        except Exception:
            return {'__repr__': repr(value), '__type__': type(value).__name__}

    def log(self, level: str, message: Any) -> None:
        print(f"[{level.upper()}] {message}")

    def call_openai_api(self, api_key: str, payload: dict) -> str:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }
        url = 'https://api.openai.com/v1/responses'
        request = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        try:
            with urllib.request.urlopen(request) as response:
                result = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            raise VMException(f'OpenAI API request failed: {str(e)}')

        if 'output' in result and isinstance(result['output'], list) and result['output']:
            first_output = result['output'][0]
            if isinstance(first_output, dict) and 'content' in first_output:
                content = first_output['content']
                if isinstance(content, list) and content:
                    first_content = content[0]
                    if isinstance(first_content, dict) and 'text' in first_content:
                        return first_content['text']
        if 'choices' in result and isinstance(result['choices'], list) and result['choices']:
            choice = result['choices'][0]
            if isinstance(choice, dict) and 'message' in choice:
                message = choice['message']
                if isinstance(message, dict) and 'content' in message:
                    content = message['content']
                    if isinstance(content, str):
                        return content
        return json.dumps(result)

    def call_builtin(self, name: str, args: List[Any]):
        if name == 'len':
            return self.get_length(args[0])
        if name == 'range':
            if len(args) == 1:
                start, end = 0, args[0]
            elif len(args) == 2:
                start, end = args[0], args[1]
            else:
                raise VMException("range() expects 1 or 2 arguments")
            return [i for i in range(start, end + 1)]
        if name == 'str':
            return str(args[0])
        if name == 'int':
            return int(args[0])
        if name == 'float':
            return float(args[0])
        if name == 'type':
            return type(args[0]).__name__
        if name == 'http_get':
            url = args[0]
            headers = args[1] if len(args) > 1 else {}
            return self.http_get(url, headers)
        if name == 'http_post':
            url = args[0]
            body = args[1] if len(args) > 1 else ''
            headers = args[2] if len(args) > 2 else {}
            return self.http_post(url, body, headers)
        if name == 'json_parse':
            return json.loads(args[0])
        if name == 'json_stringify':
            return json.dumps(args[0])
        if name == 'py_import':
            # args[0]: module name string
            mod_name = args[0]
            if not self.py_import_enabled:
                raise VMException('py_import is disabled by runtime configuration')
            if self.py_import_allowlist and mod_name not in self.py_import_allowlist:
                raise VMException(f"py_import not allowed for module '{mod_name}' by allowlist")
            try:
                module = importlib.import_module(mod_name)
            except Exception as e:
                # If this module is allowed to fallback, register a proxy and return the name
                if mod_name in self.py_fallback_modules:
                    self.py_modules[mod_name] = {'__fallback__': True, '__name__': mod_name}
                    return mod_name
                raise VMException(f"py_import failed: {str(e)}")
            self.py_modules[mod_name] = module
            return mod_name

        if name == 'py_call':
            # args: module_name, func_name, [arg1, arg2, ...]
            if len(args) < 2:
                raise VMException('py_call requires at least module and function name')
            mod_name = args[0]
            func_name = args[1]
            py_args = []
            if len(args) > 2:
                py_args = [self._to_python_arg(a) for a in args[2]] if isinstance(args[2], list) else [self._to_python_arg(args[2])]
            module = self.py_modules.get(mod_name)
            if module is None:
                try:
                    module = importlib.import_module(mod_name)
                    self.py_modules[mod_name] = module
                except Exception as e:
                    # If allowed fallback, register proxy
                    if mod_name in self.py_fallback_modules:
                        self.py_modules[mod_name] = {'__fallback__': True, '__name__': mod_name}
                        module = self.py_modules[mod_name]
                    else:
                        raise VMException(f"py_call import failed: {str(e)}")

            # If module is a fallback proxy, route to subprocess wrapper for supported ops
            if isinstance(module, dict) and module.get('__fallback__'):
                fallback_name = module.get('__name__')
                if fallback_name == 'numpy':
                    # Use tools/np_wrapper.py for numpy fallback
                    # Supported func_names: sum, mean, matmul, reshape, dot, transpose
                    if func_name in ('sum', 'mean', 'matmul', 'dot', 'transpose'):
                        # payload can be either a single argument (e.g., [[a,b]]) or multiple args ([a,b])
                        if not py_args:
                            payload = None
                        elif len(py_args) == 1:
                            payload = py_args[0]
                        else:
                            payload = py_args
                        arg_json = json.dumps(payload)
                        out = self.call_python('tools/np_wrapper.py', [func_name, arg_json])
                        try:
                            parsed = json.loads(out)
                        except Exception:
                            parsed = out
                        return parsed
                    elif func_name == 'reshape':
                        payload = py_args[0] if py_args else None
                        shape = py_args[1] if len(py_args) > 1 else None
                        arg_json = json.dumps({'data': payload, 'shape': shape})
                        out = self.call_python('tools/np_wrapper.py', ['reshape', arg_json])
                        try:
                            parsed = json.loads(out)
                        except Exception:
                            parsed = out
                        return parsed
                    else:
                        raise VMException(f"py_call fallback: unsupported function {func_name} for module {fallback_name}")
                else:
                    raise VMException(f"py_call fallback: no wrapper for {fallback_name}")

            try:
                func = getattr(module, func_name)
            except Exception:
                raise VMException(f"py_call: function {func_name} not found on module {mod_name}")

            # Normalize common vararg patterns from Human wrappers
            # e.g., np_matmul passes a single [[a,b]] argument in Human; unwrap to func(a,b)
            try:
                norm_args = py_args
                if func_name in ('matmul', 'dot') and len(py_args) == 1 and isinstance(py_args[0], list) and len(py_args[0]) == 2:
                    norm_args = py_args[0]
                if func_name == 'reshape' and len(py_args) == 1 and isinstance(py_args[0], dict) and 'data' in py_args[0] and 'shape' in py_args[0]:
                    norm_args = [py_args[0]['data'], py_args[0]['shape']]

                res = func(*norm_args)
            except Exception as e:
                raise VMException(f"py_call execution failed: {str(e)}")
            return self._from_python_result(res)
        if name == 'openai_request':
            api_key = args[0]
            prompt = args[1]
            model = args[2] if len(args) > 2 else 'gpt-4.1-mini'
            temperature = args[3] if len(args) > 3 else 0.7
            return self.openai_request(api_key, prompt, model, temperature)
        if name == 'openai_chat':
            api_key = args[0]
            messages = args[1]
            model = args[2] if len(args) > 2 else 'gpt-4.1-mini'
            temperature = args[3] if len(args) > 3 else 0.7
            return self.openai_chat(api_key, messages, model, temperature)
        if name == 'env':
            if len(args) == 0:
                raise VMException('env() requires at least one argument')
            return self.env(args[0], args[1] if len(args) > 1 else None)
        if name == 'http_route':
            return self.http_route(args[0], args[1], args[2])
        if name == 'http_listen':
            return self.http_listen(args[0], args[1])
        if name == 'http_listen_async':
            return self.http_listen_async(args[0], args[1])
        if name == 'http_response':
            headers = args[2] if len(args) > 2 else {}
            return self.http_response(args[0], args[1], headers)
        if name == 'http_middleware':
            return self.http_middleware(args[0])
        if name == 'http_static':
            return self.http_static(args[0], args[1])
        if name == 'request_body':
            return self.request_body()
        if name == 'request_json':
            return self.request_json()
        if name == 'request_query':
            return self.request_query()
        if name == 'request_headers':
            return self.request_headers()
        if name == 'request_method':
            return self.request_method()
        if name == 'request_path':
            return self.request_path()
        if name == 'http_put':
            url = args[0]
            body = args[1] if len(args) > 1 else ''
            headers = args[2] if len(args) > 2 else {}
            return self.http_request(url, body, headers, 'PUT')
        if name == 'http_delete':
            url = args[0]
            headers = args[1] if len(args) > 1 else {}
            return self.http_request(url, '', headers, 'DELETE')
        if name == 'file_read':
            return self.file_read(args[0])
        if name == 'file_write':
            return self.file_write(args[0], args[1])
        if name == 'file_exists':
            return self.file_exists(args[0])
        if name == 'path_join':
            return self.path_join(*args)
        if name == 'sleep':
            return self.sleep(args[0])
        if name == 'call_python':
            return self.call_python(args[0], args[1] if len(args) > 1 else None)
        if name == 'log':
            return self.log(args[0], args[1])
        if name == 'map':
            func_name = args[0]
            items = args[1]
            return [self.call_function(func_name, [item]) for item in items]
        if name == 'filter':
            func_name = args[0]
            items = args[1]
            return [item for item in items if self.call_function(func_name, [item])]
        if name == 'reduce':
            func_name = args[0]
            items = args[1]
            accumulator = args[2] if len(args) > 2 else None
            result = accumulator
            for item in items:
                if result is None:
                    result = item
                else:
                    result = self.call_function(func_name, [result, item])
            return result
        
        # New builtin functions
        if name == 'sorted':
            if not args:
                raise VMException("sorted() requires at least 1 argument")
            items = args[0]
            if not isinstance(items, list):
                raise VMException("sorted() requires a list")
            return sorted(items)
        
        if name == 'min':
            if not args:
                raise VMException("min() requires at least 1 argument")
            if isinstance(args[0], list):
                return min(args[0]) if args[0] else None
            return min(args)
        
        if name == 'max':
            if not args:
                raise VMException("max() requires at least 1 argument")
            if isinstance(args[0], list):
                return max(args[0]) if args[0] else None
            return max(args)
        
        if name == 'enumerate':
            if not args:
                raise VMException("enumerate() requires 1 argument")
            items = args[0]
            if not isinstance(items, list):
                raise VMException("enumerate() requires a list")
            return [[i, item] for i, item in enumerate(items)]
        
        if name == 'zip':
            if not args:
                raise VMException("zip() requires at least 1 argument")
            # Check all arguments are lists
            for arg in args:
                if not isinstance(arg, list):
                    raise VMException("zip() requires all arguments to be lists")
            # Zip the lists together
            return [[item[i] if i < len(item) else None for item in args] for i in range(max(len(arg) for arg in args))]
        
        if name == 'sum':
            if not args:
                raise VMException("sum() requires at least 1 argument")
            items = args[0]
            if not isinstance(items, list):
                raise VMException("sum() requires a list")
            total = 0
            for item in items:
                total += item
            return total
        
        if name == 'all':
            if not args:
                raise VMException("all() requires 1 argument")
            items = args[0]
            if not isinstance(items, list):
                raise VMException("all() requires a list")
            return all(self.is_truthy(item) for item in items)
        
        if name == 'any':
            if not args:
                raise VMException("any() requires 1 argument")
            items = args[0]
            if not isinstance(items, list):
                raise VMException("any() requires a list")
            return any(self.is_truthy(item) for item in items)
        
        if name == 'reversed':
            if not args:
                raise VMException("reversed() requires 1 argument")
            items = args[0]
            if not isinstance(items, list):
                raise VMException("reversed() requires a list")
            return list(reversed(items))

        raise VMException(f"Undefined function '{name}'")
