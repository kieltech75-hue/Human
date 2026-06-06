"""
Abstract Syntax Tree (AST) Node Definitions
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Tuple

@dataclass
class ASTNode:
    pass

# Literals
@dataclass
class NumberLiteral(ASTNode):
    value: float

@dataclass
class StringLiteral(ASTNode):
    value: str

@dataclass
class BooleanLiteral(ASTNode):
    value: bool

@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]

@dataclass
class ListComprehension(ASTNode):
    element: ASTNode
    variable: str
    iterable: ASTNode
    condition: Optional[ASTNode] = None

@dataclass
class DictLiteral(ASTNode):
    pairs: List[Tuple[str, ASTNode]]

# Variables and identifiers
@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class Assignment(ASTNode):
    target: ASTNode
    value: ASTNode

# Operators
@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode

@dataclass
class Comparison(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode

@dataclass
class IndexAccess(ASTNode):
    collection: ASTNode
    index: ASTNode


@dataclass
class SliceAccess(ASTNode):
    collection: ASTNode
    start: Optional[ASTNode] = None
    end: Optional[ASTNode] = None
    step: Optional[ASTNode] = None

# Control Flow
@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None

@dataclass
class LoopStatement(ASTNode):
    start: ASTNode
    end: ASTNode
    body: List[ASTNode]

@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: List[ASTNode]

@dataclass
class ForInStatement(ASTNode):
    variable: str
    iterable: ASTNode
    body: List[ASTNode]

@dataclass
class TryCatchStatement(ASTNode):
    try_block: List[ASTNode]
    catch_var: Optional[str]
    catch_block: Optional[List[ASTNode]]

@dataclass
class BreakStatement(ASTNode):
    pass

@dataclass
class ContinueStatement(ASTNode):
    pass

@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: List[ASTNode]

@dataclass
class MethodCall(ASTNode):
    object: ASTNode
    method: str
    arguments: List[ASTNode]

@dataclass
class NewExpression(ASTNode):
    class_name: str
    arguments: List[ASTNode]

@dataclass
class LambdaExpression(ASTNode):
    parameters: List[str]
    body: ASTNode

# Functions and Classes
@dataclass
class FunctionDef(ASTNode):
    name: str
    parameters: List[str]
    body: List[ASTNode]

@dataclass
class ClassDef(ASTNode):
    name: str
    body: List[ASTNode]

@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode] = None

# Built-in Functions
@dataclass
class PrintStatement(ASTNode):
    arguments: List[ASTNode]

@dataclass
class AskStatement(ASTNode):
    prompt: ASTNode

@dataclass
class ImportStatement(ASTNode):
    path: str

# Program
@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
