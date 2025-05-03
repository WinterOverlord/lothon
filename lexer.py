import re

class TokenType:
    IMPORT = 'IMPORT'
    AS = 'AS'
    DEF = 'DEF'
    VIO = 'VIO'
    PRINTFS = 'PRINTFS'
    INPUT = 'INPUT'
    ID = 'ID'
    INT = 'INT'
    FLOAT = 'FLOAT'
    STRING = 'STRING'
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    COMMA = ','
    DOT = '.'
    EQ = '='
    PLUS = '+'
    MINUS = '-'
    MULT = '*'
    DIV = '/'
    COLON = ':'
    SEMI = ';'
    RETURN = 'RETURN'
    EOF = 'EOF'

TOKEN_REGEX = [
    (r'\bimport\b', TokenType.IMPORT),
    (r'\bas\b', TokenType.AS),
    (r'\bdef\b', TokenType.DEF),
    (r'\bvio\b', TokenType.VIO),
    (r'\bprintfs\b', TokenType.PRINTFS),
    (r'\binput\b', TokenType.INPUT),
    (r'\breturn\b', TokenType.RETURN),
    (r'\d+\.\d+', TokenType.FLOAT),
    (r'\d+', TokenType.INT),
    (r'"[^"]*"', TokenType.STRING),
    (r'\(', TokenType.LPAREN),
    (r'\)', TokenType.RPAREN),
    (r'\{', TokenType.LBRACE),
    (r'\}', TokenType.RBRACE),
    (r',', TokenType.COMMA),
    (r'\.', TokenType.DOT),
    (r'=', TokenType.EQ),
    (r'\+', TokenType.PLUS),
    (r'-', TokenType.MINUS),
    (r'\*', TokenType.MULT),
    (r'/', TokenType.DIV),
    (r':', TokenType.COLON),
    (r';', TokenType.SEMI),
    (r'[a-zA-Z_]\w*', TokenType.ID),
]

class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
    
    def tokenize(self):
        tokens = []
        while self.pos < len(self.code):
            match = None
            for pattern, token_type in TOKEN_REGEX:
                regex = re.compile(pattern)
                match = regex.match(self.code, self.pos)
                if match:
                    value = match.group(0)
                    if token_type == TokenType.STRING:
                        value = value[1:-1]
                    elif token_type in (TokenType.INT, TokenType.FLOAT):
                        value = eval(value)
                    tokens.append(Token(token_type, value, self.line))
                    self.pos = match.end()
                    break
            if not match:
                char = self.code[self.pos]
                if char == '\n': self.line += 1
                self.pos += 1
        tokens.append(Token(TokenType.EOF, None, self.line))
        return tokens