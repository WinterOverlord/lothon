from lexer import TokenType
from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[0]
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
    
    def parse(self):
        statements = []
        while self.current.type != TokenType.EOF:
            stmt = self.parse_statement()
            statements.append(stmt)
        return Program(statements)
    
    def parse_statement(self):
        if self.current.type == TokenType.IMPORT:
            return self.parse_import()
        elif self.current.type == TokenType.DEF:
            return self.parse_function()
        elif self.current.type == TokenType.VIO:
            return self.parse_var_decl()
        elif self.current.type == TokenType.PRINTFS:
            return self.parse_print()
        elif self.current.type == TokenType.RETURN:
            return self.parse_return()
        return self.parse_expr()
    
    def parse_import(self):
        self.advance()  # eat import
        module_path = []
        while self.current.type == TokenType.ID:
            module_path.append(self.current.value)
            self.advance()
            if self.current.type == TokenType.DOT:
                self.advance()
        alias = module_path[-1]
        if self.current.type == TokenType.AS:
            self.advance()
            alias = self.current.value
            self.advance()
        return Import(module_path, alias)
    
    def parse_function(self):
        self.advance()  # eat def
        name = self.current.value
        self.advance()  # eat func name
        self.advance()  # eat (
        params = []
        while self.current.type != TokenType.RPAREN:
            params.append(self.current.value)
            self.advance()
            if self.current.type == TokenType.COMMA:
                self.advance()
        self.advance()  # eat )
        self.advance()  # eat :
        body = []
        while self.current.type not in (TokenType.EOF, TokenType.RBRACE):
            body.append(self.parse_statement())
        return FunctionDef(name, params, body)
    
    def parse_var_decl(self):
        self.advance()  # eat vio
        name = self.current.value
        self.advance()
        value = None
        if self.current.type == TokenType.EQ:
            self.advance()
            value = self.parse_expr()
        return VarDecl(name, value)
    
    def parse_print(self):
        self.advance()  # eat printfs
        self.advance()  # eat (
        args = []
        while self.current.type != TokenType.RPAREN:
            args.append(self.parse_expr())
            if self.current.type == TokenType.COMMA:
                self.advance()
        self.advance()  # eat )
        return Print(args)
    
    def parse_return(self):
        self.advance()  # eat return
        value = self.parse_expr() if self.current.type != TokenType.NEWLINE else None
        return Return(value)
    
    def parse_expr(self):
        return self.parse_add_sub()
    
    def parse_add_sub(self):
        expr = self.parse_mul_div()
        while self.current.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current.type
            self.advance()
            right = self.parse_mul_div()
            expr = BinaryOp(expr, op, right)
        return expr
    
    def parse_mul_div(self):
        expr = self.parse_primary()
        while self.current.type in (TokenType.MULT, TokenType.DIV):
            op = self.current.type
            self.advance()
            right = self.parse_primary()
            expr = BinaryOp(expr, op, right)
        return expr
    
    def parse_primary(self):
        if self.current.type == TokenType.ID:
            name = self.current.value
            self.advance()
            if self.current.type == TokenType.LPAREN:
                return self.parse_call(name)
            return Variable(name)
        elif self.current.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING):
            value = self.current.value
            self.advance()
            return Literal(value)
        elif self.current.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.advance()  # 跳过右括号
            return expr
        else:
            raise SyntaxError(f"Unexpected token {self.current.type}")
    
    def parse_call(self, func_name):
        self.advance()  # eat (
        args = []
        while self.current.type != TokenType.RPAREN:
            args.append(self.parse_expr())
            if self.current.type == TokenType.COMMA:
                self.advance()
        self.advance()  # eat )
        return Call(func_name, args)