"""
Human Language Lexer - Tokenizes source code
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Keywords
    SET = auto()
    TO = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    END = auto()
    LOOP = auto()
    FROM = auto()
    DO = auto()
    DEFINE = auto()
    WITH = auto()
    RETURN = auto()
    PRINT = auto()
    ASK = auto()
    CLASS = auto()
    NEW = auto()
    THIS = auto()
    TRUE = auto()
    FALSE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    IS = auto()
    GREATER = auto()
    LESS = auto()
    EQUAL = auto()
    THAN = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    TRY = auto()
    CATCH = auto()
    IMPORT = auto()
    BREAK = auto()
    CONTINUE = auto()
    LAMBDA = auto()
    FN = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()

    # Special
    EOF = auto()
    NEWLINE = auto()

@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

class Lexer:
    def __init__(self, source: str):
        self.source = source.lstrip('\ufeff')
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def error(self, message: str):
        raise SyntaxError(f"Lexer error at line {self.line}, column {self.column}: {message}")

    def peek(self, offset: int = 0) -> Optional[str]:
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return None

    def advance(self) -> Optional[str]:
        if self.pos < len(self.source):
            char = self.source[self.pos]
            self.pos += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return char
        return None

    def skip_whitespace(self):
        while self.peek() and self.peek() in ' \t\r':
            self.advance()

    def skip_comment(self):
        if self.peek() == '-' and self.peek(1) == '-':
            self.advance()
            self.advance()
            while self.peek() and self.peek() != '\n':
                self.advance()

    def read_string(self, quote: str) -> str:
        self.advance()
        value = ""
        while self.peek() and self.peek() != quote:
            if self.peek() == '\\':
                self.advance()
                next_char = self.advance()
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                elif next_char == '"':
                    value += '"'
                elif next_char == "'":
                    value += "'"
                else:
                    value += next_char
            else:
                value += self.advance()

        if not self.peek():
            self.error("Unterminated string literal")
        self.advance()
        return value

    def read_number(self) -> float:
        value = ""
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            value += self.advance()

        if '.' in value:
            return float(value)
        return int(value)

    def read_identifier(self) -> str:
        value = ""
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            value += self.advance()
        return value

    def get_keyword_type(self, word: str) -> Optional[TokenType]:
        keywords = {
            'set': TokenType.SET,
            'to': TokenType.TO,
            'if': TokenType.IF,
            'then': TokenType.THEN,
            'else': TokenType.ELSE,
            'end': TokenType.END,
            'loop': TokenType.LOOP,
            'from': TokenType.FROM,
            'do': TokenType.DO,
            'define': TokenType.DEFINE,
            'with': TokenType.WITH,
            'return': TokenType.RETURN,
            'print': TokenType.PRINT,
            'ask': TokenType.ASK,
            'class': TokenType.CLASS,
            'new': TokenType.NEW,
            'this': TokenType.THIS,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            'is': TokenType.IS,
            'greater': TokenType.GREATER,
            'less': TokenType.LESS,
            'equal': TokenType.EQUAL,
            'than': TokenType.THAN,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'in': TokenType.IN,
            'try': TokenType.TRY,
            'catch': TokenType.CATCH,
            'import': TokenType.IMPORT,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
            'lambda': TokenType.LAMBDA,
            'fn': TokenType.FN,
        }
        return keywords.get(word.lower())

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()

            if self.peek() is None:
                break

            if self.peek() == '-' and self.peek(1) == '-':
                self.skip_comment()
                continue

            line = self.line
            column = self.column
            char = self.peek()

            if char == '\n':
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\n', line, column))
            elif char == '"':
                value = self.read_string('"')
                self.tokens.append(Token(TokenType.STRING, value, line, column))
            elif char == "'":
                value = self.read_string("'")
                self.tokens.append(Token(TokenType.STRING, value, line, column))
            elif char.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, line, column))
            elif char.isalpha() or char == '_':
                word = self.read_identifier()
                token_type = self.get_keyword_type(word)
                if token_type:
                    self.tokens.append(Token(token_type, word, line, column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, word, line, column))
            elif char == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', line, column))
            elif char == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, '-', line, column))
            elif char == '*':
                self.advance()
                self.tokens.append(Token(TokenType.STAR, '*', line, column))
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.SLASH, '/', line, column))
            elif char == '%':
                self.advance()
                self.tokens.append(Token(TokenType.PERCENT, '%', line, column))
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', line, column))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', line, column))
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', line, column))
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', line, column))
            elif char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', line, column))
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', line, column))
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', line, column))
            elif char == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', line, column))
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', line, column))
            else:
                self.error(f"Unexpected character: '{char}'")

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
