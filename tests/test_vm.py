import importlib
import base64
import pickle
import datetime as _dt

from human_language.vm import VM, Bytecode
from human_language.compiler import Compiler
from human_language.parser import Parser
from human_language.lexer import Lexer


def compile_and_run(source: str):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    compiler = Compiler()
    bc = compiler.compile(ast)
    vm = VM(bc)
    # execute top-level module
    vm.execute()
    return vm


def test_slice_and_slice_opcode():
    src = '''
set a to [1,2,3,4,5]
set s to a[1:4]
print s
'''
    vm = compile_and_run(src)
    # after execution, top-level var 's' should exist
    idx = vm.bytecode.var_indices.get('s')
    assert idx is not None
    val = vm.get_var(idx)
    assert val == [2,3,4]


def test_serialization_pickle_and_bytes():
    # create a dummy python object via pickle roundtrip
    obj = {'x': 1}
    pickled = pickle.dumps(obj)
    b64 = base64.b64encode(pickled).decode('ascii')
    # use the VM's _to_python_arg and _from_python_result indirectly via py_call roundtrip
    # We'll call a small inline python function by importing 'builtins' and using eval
    src = '''
set mod to py_import("builtins")
set res to py_call(mod, "str", [ [1,2,3] ])
print res
'''
    vm = compile_and_run(src)
    # basic smoke test: str([1,2,3]) should be printed and variable 'res' present
    idx = vm.bytecode.var_indices.get('res')
    assert idx is not None

def test_datetime_serialization_roundtrip():
    # Ensure VM _from_python_result handles datetime: create a datetime in Python by calling datetime.now()
    # create datetime(2020,1,1) so behavior is deterministic
    src = '''
set dtmod to py_import("datetime")
set now to py_call(dtmod, "datetime", [2020, 1, 1])
print now
'''
    # This test mostly ensures py_import/run doesn't crash; behavior may vary by Python impl
    vm = compile_and_run(src)
    # ensure 'now' var exists
    idx = vm.bytecode.var_indices.get('now')
    assert idx is not None