"""
Human Language Compiler - Converts AST to bytecode
"""

from ast_nodes import *
from enum import Enum, auto
from typing import List, Dict, Any, Tuple

class Opcode(Enum):
    # Stack operations
    LOAD_CONST = auto()
    LOAD_VAR = auto()
    STORE_VAR = auto()
    MAKE_LIST = auto()
    MAKE_DICT = auto()
    LOAD_INDEX = auto()
    LEN = auto()

    # Arithmetic
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    NEG = auto()

    # Comparison and logic
    COMPARE_EQ = auto()
    COMPARE_GT = auto()
    COMPARE_LT = auto()
    LOGIC_AND = auto()
    LOGIC_OR = auto()
    LOGIC_NOT = auto()

    # Control flow
    JUMP = auto()
    JUMP_IF_FALSE = auto()
    JUMP_IF_TRUE = auto()
    PUSH_HANDLER = auto()
    POP_HANDLER = auto()

    # Functions and objects
    CALL = auto()
    CALL_METHOD = auto()
    NEW = auto()
    STORE_INDEX = auto()
    RETURN = auto()
    MAKE_LAMBDA = auto()
    LIST_COMP = auto()

    # Imports
    IMPORT = auto()

    # I/O
    PRINT = auto()
    INPUT = auto()

    # Misc
    POP = auto()
    NOP = auto()
    HALT = auto()

class Bytecode:
    def __init__(self):
        self.instructions = []
        self.constants = []
        self.functions = {}
        self.classes = {}
        self.var_indices = {}
        self.next_label = 0

    def emit(self, opcode: Opcode, arg: Any = None) -> int:
        pos = len(self.instructions)
        self.instructions.append((opcode, arg))
        return pos

    def add_constant(self, value: Any) -> int:
        self.constants.append(value)
        return len(self.constants) - 1

    def get_label(self) -> int:
        label = self.next_label
        self.next_label += 1
        return label

    def patch_jump(self, pos: int, target: int):
        opcode, _ = self.instructions[pos]
        self.instructions[pos] = (opcode, target)

class Compiler:
    def __init__(self):
        self.bytecode = Bytecode()
        self.functions = {}
        self.classes = {}
        self.var_counter = 0

    def compile(self, ast: Program) -> Bytecode:
        for stmt in ast.statements:
            self.compile_statement(stmt)
        self.bytecode.emit(Opcode.HALT)
        self.bytecode.functions.update(self.functions)
        self.bytecode.classes.update(self.classes)
        return self.bytecode

    def compile_statement(self, node: ASTNode):
        if isinstance(node, Assignment):
            self.compile_assignment(node)
        elif isinstance(node, IfStatement):
            self.compile_if_statement(node)
        elif isinstance(node, LoopStatement):
            self.compile_loop_statement(node)
        elif isinstance(node, WhileStatement):
            self.compile_while_statement(node)
        elif isinstance(node, ForInStatement):
            self.compile_for_statement(node)
        elif isinstance(node, FunctionDef):
            self.compile_function_def(node)
        elif isinstance(node, ClassDef):
            self.compile_class_def(node)
        elif isinstance(node, ReturnStatement):
            self.compile_return_statement(node)
        elif isinstance(node, PrintStatement):
            self.compile_print_statement(node)
        elif isinstance(node, AskStatement):
            self.compile_ask_statement(node)
        elif isinstance(node, ImportStatement):
            self.compile_import_statement(node)
        elif isinstance(node, TryCatchStatement):
            self.compile_try_statement(node)
        elif isinstance(node, FunctionCall):
            self.compile_expression(node)
            self.bytecode.emit(Opcode.POP)
        else:
            self.compile_expression(node)

    def compile_assignment(self, node: Assignment):
        if isinstance(node.target, Identifier):
            self.compile_expression(node.value)
            var_idx = self.get_var_index(node.target.name)
            self.bytecode.emit(Opcode.STORE_VAR, var_idx)
        elif isinstance(node.target, IndexAccess):
            self.compile_expression(node.target.collection)
            self.compile_expression(node.target.index)
            self.compile_expression(node.value)
            self.bytecode.emit(Opcode.STORE_INDEX)
        else:
            raise ValueError(f"Unsupported assignment target: {type(node.target).__name__}")

    def compile_if_statement(self, node: IfStatement):
        self.compile_expression(node.condition)
        jump_if_false_pos = self.bytecode.emit(Opcode.JUMP_IF_FALSE, None)

        for stmt in node.then_block:
            self.compile_statement(stmt)

        if node.else_block:
            jump_pos = self.bytecode.emit(Opcode.JUMP, None)
            self.bytecode.patch_jump(jump_if_false_pos, len(self.bytecode.instructions))
            for stmt in node.else_block:
                self.compile_statement(stmt)
            self.bytecode.patch_jump(jump_pos, len(self.bytecode.instructions))
        else:
            self.bytecode.patch_jump(jump_if_false_pos, len(self.bytecode.instructions))

    def compile_loop_statement(self, node: LoopStatement):
        loop_var = self.get_var_index(f"__loop_var_{self.var_counter}")
        self.var_counter += 1
        end_var = self.get_var_index(f"__loop_end_{self.var_counter}")
        self.var_counter += 1

        self.compile_expression(node.start)
        self.bytecode.emit(Opcode.STORE_VAR, loop_var)
        self.compile_expression(node.end)
        self.bytecode.emit(Opcode.STORE_VAR, end_var)

        loop_check_pos = len(self.bytecode.instructions)
        self.bytecode.emit(Opcode.LOAD_VAR, loop_var)
        self.bytecode.emit(Opcode.LOAD_VAR, end_var)
        const_idx = self.bytecode.add_constant(1)
        self.bytecode.emit(Opcode.LOAD_CONST, const_idx)
        self.bytecode.emit(Opcode.ADD)
        self.bytecode.emit(Opcode.COMPARE_LT)

        jump_out_pos = self.bytecode.emit(Opcode.JUMP_IF_FALSE, None)

        for stmt in node.body:
            self.compile_statement(stmt)

        self.bytecode.emit(Opcode.LOAD_VAR, loop_var)
        self.bytecode.emit(Opcode.LOAD_CONST, const_idx)
        self.bytecode.emit(Opcode.ADD)
        self.bytecode.emit(Opcode.STORE_VAR, loop_var)
        self.bytecode.emit(Opcode.JUMP, loop_check_pos)
        self.bytecode.patch_jump(jump_out_pos, len(self.bytecode.instructions))

    def compile_while_statement(self, node: WhileStatement):
        loop_start = len(self.bytecode.instructions)
        self.compile_expression(node.condition)
        jump_out_pos = self.bytecode.emit(Opcode.JUMP_IF_FALSE, None)

        for stmt in node.body:
            self.compile_statement(stmt)

        self.bytecode.emit(Opcode.JUMP, loop_start)
        self.bytecode.patch_jump(jump_out_pos, len(self.bytecode.instructions))

    def compile_for_statement(self, node: ForInStatement):
        iterable_var = self.get_var_index(f"__for_iter_{self.var_counter}")
        self.var_counter += 1
        index_var = self.get_var_index(f"__for_index_{self.var_counter}")
        self.var_counter += 1

        self.compile_expression(node.iterable)
        self.bytecode.emit(Opcode.STORE_VAR, iterable_var)
        self.bytecode.emit(Opcode.LOAD_CONST, self.bytecode.add_constant(0))
        self.bytecode.emit(Opcode.STORE_VAR, index_var)

        loop_start = len(self.bytecode.instructions)
        self.bytecode.emit(Opcode.LOAD_VAR, index_var)
        self.bytecode.emit(Opcode.LOAD_VAR, iterable_var)
        self.bytecode.emit(Opcode.LEN)
        self.bytecode.emit(Opcode.COMPARE_LT)

        jump_out_pos = self.bytecode.emit(Opcode.JUMP_IF_FALSE, None)

        self.bytecode.emit(Opcode.LOAD_VAR, iterable_var)
        self.bytecode.emit(Opcode.LOAD_VAR, index_var)
        self.bytecode.emit(Opcode.LOAD_INDEX)

        loop_var_idx = self.get_var_index(node.variable)
        self.bytecode.emit(Opcode.STORE_VAR, loop_var_idx)

        for stmt in node.body:
            self.compile_statement(stmt)

        self.bytecode.emit(Opcode.LOAD_VAR, index_var)
        self.bytecode.emit(Opcode.LOAD_CONST, self.bytecode.add_constant(1))
        self.bytecode.emit(Opcode.ADD)
        self.bytecode.emit(Opcode.STORE_VAR, index_var)
        self.bytecode.emit(Opcode.JUMP, loop_start)
        self.bytecode.patch_jump(jump_out_pos, len(self.bytecode.instructions))

    def compile_function_def(self, node: FunctionDef):
        self.functions[node.name] = {
            'params': node.parameters,
            'node': node
        }

    def compile_class_def(self, node: ClassDef):
        self.classes[node.name] = {
            'node': node
        }

    def compile_return_statement(self, node: ReturnStatement):
        if node.value:
            self.compile_expression(node.value)
        self.bytecode.emit(Opcode.RETURN)

    def compile_print_statement(self, node: PrintStatement):
        for arg in node.arguments:
            self.compile_expression(arg)
        self.bytecode.emit(Opcode.PRINT, len(node.arguments))

    def compile_ask_statement(self, node: AskStatement):
        self.compile_expression(node.prompt)
        self.bytecode.emit(Opcode.INPUT)

    def compile_import_statement(self, node: ImportStatement):
        const_idx = self.bytecode.add_constant(node.path)
        self.bytecode.emit(Opcode.LOAD_CONST, const_idx)
        self.bytecode.emit(Opcode.IMPORT)

    def compile_try_statement(self, node: TryCatchStatement):
        handler_pos = self.bytecode.emit(Opcode.PUSH_HANDLER, None)
        for stmt in node.try_block:
            self.compile_statement(stmt)

        self.bytecode.emit(Opcode.POP_HANDLER)
        jump_after_catch = self.bytecode.emit(Opcode.JUMP, None)

        catch_pos = len(self.bytecode.instructions)
        self.bytecode.patch_jump(handler_pos, catch_pos)

        if node.catch_var:
            var_idx = self.get_var_index(node.catch_var)
            self.bytecode.emit(Opcode.STORE_VAR, var_idx)

        if node.catch_block:
            for stmt in node.catch_block:
                self.compile_statement(stmt)

        self.bytecode.patch_jump(jump_after_catch, len(self.bytecode.instructions))

    def compile_expression(self, node: ASTNode):
        if isinstance(node, NumberLiteral):
            const_idx = self.bytecode.add_constant(node.value)
            self.bytecode.emit(Opcode.LOAD_CONST, const_idx)

        elif isinstance(node, StringLiteral):
            const_idx = self.bytecode.add_constant(node.value)
            self.bytecode.emit(Opcode.LOAD_CONST, const_idx)

        elif isinstance(node, BooleanLiteral):
            const_idx = self.bytecode.add_constant(node.value)
            self.bytecode.emit(Opcode.LOAD_CONST, const_idx)

        elif isinstance(node, ListLiteral):
            for element in node.elements:
                self.compile_expression(element)
            self.bytecode.emit(Opcode.MAKE_LIST, len(node.elements))

        elif isinstance(node, ListComprehension):
            # Compile list comprehension as a special builtin
            self.compile_expression(node.iterable)
            # Pass parameters for comprehension evaluation
            self.bytecode.emit(Opcode.LIST_COMP, (node.variable, node.element, node.condition))

        elif isinstance(node, DictLiteral):
            for key, value in node.pairs:
                key_idx = self.bytecode.add_constant(key)
                self.bytecode.emit(Opcode.LOAD_CONST, key_idx)
                self.compile_expression(value)
            self.bytecode.emit(Opcode.MAKE_DICT, len(node.pairs))

        elif isinstance(node, Identifier):
            var_idx = self.get_var_index(node.name)
            self.bytecode.emit(Opcode.LOAD_VAR, var_idx)

        elif isinstance(node, BinaryOp):
            self.compile_expression(node.left)
            self.compile_expression(node.right)
            if node.operator == '+':
                self.bytecode.emit(Opcode.ADD)
            elif node.operator == '-':
                self.bytecode.emit(Opcode.SUB)
            elif node.operator == '*':
                self.bytecode.emit(Opcode.MUL)
            elif node.operator == '/':
                self.bytecode.emit(Opcode.DIV)
            elif node.operator == '%':
                self.bytecode.emit(Opcode.MOD)

        elif isinstance(node, UnaryOp):
            self.compile_expression(node.operand)
            if node.operator == '-':
                self.bytecode.emit(Opcode.NEG)
            elif node.operator == 'not':
                self.bytecode.emit(Opcode.LOGIC_NOT)

        elif isinstance(node, Comparison):
            self.compile_expression(node.left)
            self.compile_expression(node.right)
            if node.operator == 'equal':
                self.bytecode.emit(Opcode.COMPARE_EQ)
            elif node.operator == 'greater':
                self.bytecode.emit(Opcode.COMPARE_GT)
            elif node.operator == 'less':
                self.bytecode.emit(Opcode.COMPARE_LT)
            elif node.operator == 'and':
                self.bytecode.emit(Opcode.LOGIC_AND)
            elif node.operator == 'or':
                self.bytecode.emit(Opcode.LOGIC_OR)
            elif node.operator == 'is':
                self.bytecode.emit(Opcode.COMPARE_EQ)

        elif isinstance(node, IndexAccess):
            self.compile_expression(node.collection)
            self.compile_expression(node.index)
            self.bytecode.emit(Opcode.LOAD_INDEX)

        elif isinstance(node, FunctionCall):
            for arg in node.arguments:
                self.compile_expression(arg)
            self.bytecode.emit(Opcode.CALL, (node.name, len(node.arguments)))

        elif isinstance(node, MethodCall):
            self.compile_expression(node.object)
            for arg in node.arguments:
                self.compile_expression(arg)
            self.bytecode.emit(Opcode.CALL_METHOD, (node.method, len(node.arguments)))

        elif isinstance(node, NewExpression):
            for arg in node.arguments:
                self.compile_expression(arg)
            self.bytecode.emit(Opcode.NEW, (node.class_name, len(node.arguments)))

        elif isinstance(node, LambdaExpression):
            self.bytecode.emit(Opcode.MAKE_LAMBDA, (node.parameters, node.body))

    def get_var_index(self, name: str) -> int:
        if name not in self.bytecode.var_indices:
            self.bytecode.var_indices[name] = len(self.bytecode.var_indices)
        return self.bytecode.var_indices[name]
