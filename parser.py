"""
Human Language Parser - Converts tokens to AST
"""

from lexer import TokenType, Token
from ast_nodes import *
from typing import List, Optional

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def error(self, message: str):
        token = self.current_token()
        raise SyntaxError(f"Parse error at line {token.line}, column {token.column}: {message}")

    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def peek(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]

    def advance(self):
        if self.pos < len(self.tokens):
            self.pos += 1

    def expect(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != token_type:
            self.error(f"Expected {token_type}, got {token.type}")
        self.advance()
        return token

    def skip_newlines(self):
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()

    def parse(self) -> Program:
        statements = []
        self.skip_newlines()

        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()

        return Program(statements)

    def parse_statement(self) -> Optional[ASTNode]:
        self.skip_newlines()
        token = self.current_token()

        if token.type == TokenType.SET:
            return self.parse_assignment()
        elif token.type == TokenType.IF:
            return self.parse_if_statement()
        elif token.type == TokenType.LOOP:
            return self.parse_loop_statement()
        elif token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif token.type == TokenType.FOR:
            return self.parse_for_statement()
        elif token.type == TokenType.DEFINE:
            return self.parse_function_def()
        elif token.type == TokenType.CLASS:
            return self.parse_class_def()
        elif token.type == TokenType.RETURN:
            return self.parse_return_statement()
        elif token.type == TokenType.PRINT:
            return self.parse_print_statement()
        elif token.type == TokenType.ASK:
            return self.parse_ask_statement()
        elif token.type == TokenType.IMPORT:
            return self.parse_import_statement()
        elif token.type == TokenType.TRY:
            return self.parse_try_statement()
        elif token.type == TokenType.BREAK:
            self.advance()
            return BreakStatement()
        elif token.type == TokenType.CONTINUE:
            self.advance()
            return ContinueStatement()
        elif token.type == TokenType.IDENTIFIER:
            expr = self.parse_expression()
            return expr
        elif token.type == TokenType.EOF:
            return None
        else:
            self.error(f"Unexpected token: {token.type}")

    def parse_assignment(self) -> Assignment:
        self.expect(TokenType.SET)
        self.skip_newlines()

        target = self.parse_assignment_target()
        self.skip_newlines()
        self.expect(TokenType.TO)
        self.skip_newlines()

        value = self.parse_expression()
        return Assignment(target, value)

    def parse_assignment_target(self) -> ASTNode:
        token = self.current_token()
        if token.type not in (TokenType.IDENTIFIER, TokenType.THIS):
            self.error("Expected assignment target")

        if token.type == TokenType.THIS:
            self.advance()
            target: ASTNode = Identifier('this')
        else:
            target = Identifier(self.expect(TokenType.IDENTIFIER).value)

        while self.current_token().type == TokenType.LBRACKET:
            self.advance()
            index = self.parse_expression()
            self.expect(TokenType.RBRACKET)
            target = IndexAccess(target, index)

        return target

    def parse_if_statement(self) -> IfStatement:
        self.expect(TokenType.IF)
        self.skip_newlines()

        condition = self.parse_expression()

        self.skip_newlines()
        if self.current_token().type == TokenType.THEN:
            self.advance()
            self.skip_newlines()

        then_block = self.parse_block()

        else_block = None
        if self.current_token().type == TokenType.ELSE:
            self.advance()
            self.skip_newlines()
            else_block = self.parse_block()

        self.skip_newlines()
        self.expect(TokenType.END)
        self.skip_newlines()
        if self.current_token().type == TokenType.IF:
            self.advance()

        return IfStatement(condition, then_block, else_block)

    def parse_loop_statement(self) -> LoopStatement:
        self.expect(TokenType.LOOP)
        self.skip_newlines()
        self.expect(TokenType.FROM)
        self.skip_newlines()

        start = self.parse_expression()

        self.skip_newlines()
        self.expect(TokenType.TO)
        self.skip_newlines()

        end = self.parse_expression()

        self.skip_newlines()
        self.expect(TokenType.DO)
        self.skip_newlines()

        body = self.parse_block()

        self.skip_newlines()
        self.expect(TokenType.END)
        self.skip_newlines()
        if self.current_token().type == TokenType.LOOP:
            self.advance()

        return LoopStatement(start, end, body)

    def parse_while_statement(self) -> WhileStatement:
        self.expect(TokenType.WHILE)
        self.skip_newlines()

        condition = self.parse_expression()

        self.skip_newlines()
        self.expect(TokenType.DO)
        self.skip_newlines()

        body = self.parse_block()

        self.skip_newlines()
        self.expect(TokenType.END)
        self.skip_newlines()
        if self.current_token().type == TokenType.WHILE:
            self.advance()

        return WhileStatement(condition, body)

    def parse_for_statement(self) -> ForInStatement:
        self.expect(TokenType.FOR)
        self.skip_newlines()

        var_token = self.expect(TokenType.IDENTIFIER)
        variable = var_token.value
        self.skip_newlines()

        self.expect(TokenType.IN)
        self.skip_newlines()

        iterable = self.parse_expression()

        self.skip_newlines()
        self.expect(TokenType.DO)
        self.skip_newlines()

        body = self.parse_block()

        self.skip_newlines()
        self.expect(TokenType.END)
        self.skip_newlines()
        if self.current_token().type == TokenType.FOR:
            self.advance()

        return ForInStatement(variable, iterable, body)

    def parse_function_def(self) -> FunctionDef:
        self.expect(TokenType.DEFINE)
        self.skip_newlines()

        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value

        parameters = []
        if self.current_token().type == TokenType.WITH:
            self.advance()
            self.skip_newlines()

            while True:
                param_token = self.expect(TokenType.IDENTIFIER)
                parameters.append(param_token.value)

                self.skip_newlines()
                if self.current_token().type != TokenType.COMMA:
                    break
                self.advance()
                self.skip_newlines()

        self.skip_newlines()
        body = self.parse_block()

        self.skip_newlines()
        self.expect(TokenType.END)
        self.skip_newlines()
        if self.current_token().type == TokenType.DEFINE:
            self.advance()

        return FunctionDef(name, parameters, body)

    def parse_class_def(self) -> ClassDef:
        self.expect(TokenType.CLASS)
        self.skip_newlines()

        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value

        self.skip_newlines()
        body = self.parse_block()

        self.skip_newlines()
        self.expect(TokenType.END)
        self.skip_newlines()
        if self.current_token().type == TokenType.CLASS:
            self.advance()

        return ClassDef(name, body)

    def parse_return_statement(self) -> ReturnStatement:
        self.expect(TokenType.RETURN)

        if self.current_token().type in (TokenType.NEWLINE, TokenType.EOF, TokenType.END):
            return ReturnStatement(None)

        self.skip_newlines()
        value = self.parse_expression()
        return ReturnStatement(value)

    def parse_print_statement(self) -> PrintStatement:
        self.expect(TokenType.PRINT)
        self.skip_newlines()

        arguments = []
        while self.current_token().type not in (TokenType.NEWLINE, TokenType.EOF):
            arguments.append(self.parse_expression())

            if self.current_token().type == TokenType.COMMA:
                self.advance()
                self.skip_newlines()

        return PrintStatement(arguments)

    def parse_ask_statement(self) -> AskStatement:
        self.expect(TokenType.ASK)
        self.skip_newlines()

        prompt = self.parse_expression()
        return AskStatement(prompt)

    def parse_import_statement(self) -> ImportStatement:
        self.expect(TokenType.IMPORT)
        self.skip_newlines()

        token = self.current_token()
        if token.type == TokenType.STRING:
            path = token.value
            self.advance()
        elif token.type == TokenType.IDENTIFIER:
            path = token.value
            self.advance()
        else:
            self.error("Expected module name or string path after import")

        return ImportStatement(path)

    def parse_try_statement(self) -> TryCatchStatement:
        self.expect(TokenType.TRY)
        self.skip_newlines()

        try_block = self.parse_block()

        catch_var = None
        catch_block = None
        if self.current_token().type == TokenType.CATCH:
            self.advance()
            self.skip_newlines()
            catch_var = self.expect(TokenType.IDENTIFIER).value
            self.skip_newlines()
            catch_block = self.parse_block()

        self.skip_newlines()
        self.expect(TokenType.END)
        self.skip_newlines()
        if self.current_token().type == TokenType.TRY:
            self.advance()

        return TryCatchStatement(try_block, catch_var, catch_block)

    def parse_block(self) -> List[ASTNode]:
        statements = []
        self.skip_newlines()

        while self.current_token().type not in (TokenType.END, TokenType.ELSE, TokenType.CATCH, TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()

        return statements

    def parse_expression(self) -> ASTNode:
        return self.parse_or()

    def parse_or(self) -> ASTNode:
        left = self.parse_and()

        while self.current_token().type == TokenType.OR:
            self.advance()
            self.skip_newlines()
            right = self.parse_and()
            left = Comparison(left, "or", right)

        return left

    def parse_and(self) -> ASTNode:
        left = self.parse_comparison()

        while self.current_token().type == TokenType.AND:
            self.advance()
            self.skip_newlines()
            right = self.parse_comparison()
            left = Comparison(left, "and", right)

        return left

    def parse_comparison(self) -> ASTNode:
        left = self.parse_additive()

        while self.current_token().type == TokenType.IS:
            self.advance()
            self.skip_newlines()

            op = "equal"
            if self.current_token().type == TokenType.GREATER:
                self.advance()
                op = "greater"
                if self.current_token().type == TokenType.THAN:
                    self.advance()
            elif self.current_token().type == TokenType.LESS:
                self.advance()
                op = "less"
                if self.current_token().type == TokenType.THAN:
                    self.advance()
            elif self.current_token().type == TokenType.EQUAL:
                self.advance()
                op = "equal"
                if self.current_token().type == TokenType.TO:
                    self.advance()

            self.skip_newlines()
            right = self.parse_additive()
            left = Comparison(left, op, right)

        return left

    def parse_additive(self) -> ASTNode:
        left = self.parse_multiplicative()

        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token().value
            self.advance()
            self.skip_newlines()
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)

        return left

    def parse_multiplicative(self) -> ASTNode:
        left = self.parse_unary()

        while self.current_token().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.current_token().value
            self.advance()
            self.skip_newlines()
            right = self.parse_unary()
            left = BinaryOp(left, op, right)

        return left

    def parse_unary(self) -> ASTNode:
        if self.current_token().type == TokenType.NOT:
            self.advance()
            self.skip_newlines()
            operand = self.parse_unary()
            return UnaryOp("not", operand)
        elif self.current_token().type == TokenType.MINUS:
            self.advance()
            self.skip_newlines()
            operand = self.parse_unary()
            return UnaryOp("-", operand)

        return self.parse_postfix()

    def parse_postfix(self) -> ASTNode:
        left = self.parse_primary()

        while self.current_token().type in (TokenType.DOT, TokenType.LBRACKET):
            if self.current_token().type == TokenType.DOT:
                self.advance()
                method_name = self.expect(TokenType.IDENTIFIER).value

                arguments = []
                if self.current_token().type == TokenType.LPAREN:
                    self.advance()
                    while self.current_token().type != TokenType.RPAREN:
                        arguments.append(self.parse_expression())
                        if self.current_token().type == TokenType.COMMA:
                            self.advance()
                        else:
                            break
                    self.expect(TokenType.RPAREN)

                left = MethodCall(left, method_name, arguments)
            else:
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                left = IndexAccess(left, index)

        return left

    def parse_primary(self) -> ASTNode:
        token = self.current_token()

        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberLiteral(token.value)

        elif token.type == TokenType.STRING:
            self.advance()
            return StringLiteral(token.value)

        elif token.type == TokenType.TRUE:
            self.advance()
            return BooleanLiteral(True)

        elif token.type == TokenType.FALSE:
            self.advance()
            return BooleanLiteral(False)

        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        elif token.type == TokenType.LBRACKET:
            return self.parse_list_literal()

        elif token.type == TokenType.LBRACE:
            return self.parse_dict_literal()

        elif token.type == TokenType.NEW:
            self.advance()
            class_name = self.expect(TokenType.IDENTIFIER).value
            arguments = []
            if self.current_token().type == TokenType.LPAREN:
                self.advance()
                while self.current_token().type != TokenType.RPAREN:
                    arguments.append(self.parse_expression())
                    if self.current_token().type == TokenType.COMMA:
                        self.advance()
                    else:
                        break
                self.expect(TokenType.RPAREN)
            return NewExpression(class_name, arguments)

        elif token.type == TokenType.FN or token.type == TokenType.LAMBDA:
            return self.parse_lambda()

        elif token.type == TokenType.THIS:
            self.advance()
            return Identifier('this')

        elif token.type == TokenType.IDENTIFIER:
            name = token.value
            self.advance()
            if self.current_token().type == TokenType.LPAREN:
                self.advance()
                arguments = []
                while self.current_token().type != TokenType.RPAREN:
                    arguments.append(self.parse_expression())
                    if self.current_token().type == TokenType.COMMA:
                        self.advance()
                    else:
                        break
                self.expect(TokenType.RPAREN)
                return FunctionCall(name, arguments)
            return Identifier(name)

        else:
            self.error(f"Unexpected token: {token.type}")

    def parse_list_literal(self) -> ASTNode:
        self.expect(TokenType.LBRACKET)
        self.skip_newlines()
        
        if self.current_token().type == TokenType.RBRACKET:
            self.advance()
            return ListLiteral([])
        
        element = self.parse_expression()
        
        # Check for list comprehension: [expr from var in iterable]
        if self.current_token().type == TokenType.FROM:
            self.advance()
            self.skip_newlines()
            var_token = self.expect(TokenType.IDENTIFIER)
            variable = var_token.value
            self.skip_newlines()
            self.expect(TokenType.IN)
            self.skip_newlines()
            iterable = self.parse_expression()
            
            condition = None
            if self.current_token().type == TokenType.IF:
                self.advance()
                self.skip_newlines()
                condition = self.parse_expression()
            
            self.skip_newlines()
            self.expect(TokenType.RBRACKET)
            return ListComprehension(element, variable, iterable, condition)
        
        # Regular list literal
        elements = [element]
        while self.current_token().type == TokenType.COMMA:
            self.advance()
            self.skip_newlines()
            if self.current_token().type == TokenType.RBRACKET:
                break
            elements.append(self.parse_expression())
        
        self.skip_newlines()
        self.expect(TokenType.RBRACKET)
        return ListLiteral(elements)

    def parse_dict_literal(self) -> DictLiteral:
        self.expect(TokenType.LBRACE)
        pairs = []
        self.skip_newlines()
        while self.current_token().type != TokenType.RBRACE:
            key_token = self.current_token()
            if key_token.type == TokenType.STRING:
                key = key_token.value
                self.advance()
            elif key_token.type == TokenType.IDENTIFIER:
                key = key_token.value
                self.advance()
            else:
                self.error("Dictionary keys must be strings or identifiers")

            self.skip_newlines()
            self.expect(TokenType.COLON)
            self.skip_newlines()
            value = self.parse_expression()
            pairs.append((key, value))

            if self.current_token().type == TokenType.COMMA:
                self.advance()
                self.skip_newlines()
            else:
                break

        self.expect(TokenType.RBRACE)
        return DictLiteral(pairs)

    def parse_lambda(self) -> LambdaExpression:
        self.advance()  # consume 'fn' or 'lambda'
        self.skip_newlines()
        
        parameters = []
        while self.current_token().type == TokenType.IDENTIFIER:
            parameters.append(self.expect(TokenType.IDENTIFIER).value)
            self.skip_newlines()
            if self.current_token().type == TokenType.COMMA:
                self.advance()
                self.skip_newlines()
            else:
                break
        
        self.expect(TokenType.COLON)
        self.skip_newlines()
        body = self.parse_expression()
        
        return LambdaExpression(parameters, body)
