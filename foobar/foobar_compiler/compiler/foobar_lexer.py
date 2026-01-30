"""
FOOBAR Lexer
Tokenizes .foob source files into a stream of tokens
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Keywords
    CLASS = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    STATIC = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    ELSEIF = auto()
    LOOP = auto()
    FOR = auto()
    UNTIL = auto()
    NEW = auto()
    INHERITS = auto()
    THISCLASS = auto()
    PARENT = auto()
    ISA = auto()
    IMPORT = auto()
    
    # Types
    BOOLEAN = auto()
    INTEGER = auto()
    LONGINTEGER = auto()
    FLOAT = auto()
    LONGFLOAT = auto()
    STRING = auto()
    CHARACTER = auto()
    VOID = auto()
    ENUMERATED = auto()
    
    # Literals
    TRUE = auto()
    FALSE = auto()
    NUMBER = auto()
    STRING_LITERAL = auto()
    CHAR_LITERAL = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Operators
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULUS = auto()        # %
    POWER = auto()          # ^
    INCREMENT = auto()      # ++
    DECREMENT = auto()      # --
    
    EQUAL = auto()          # ==
    GREATER = auto()        # >
    LESS = auto()           # <
    GREATER_EQUAL = auto()  # >=
    LESS_EQUAL = auto()     # <=<
    
    AND = auto()            # &
    OR = auto()             # V
    XOR = auto()            # VV
    NOT = auto()            # not
    
    ASSIGN = auto()         # =
    
    # Punctuation
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    SEMICOLON = auto()      # ;
    COMMA = auto()          # ,
    DOT = auto()            # .
    ARROW = auto()          # ->
    
    # Array slicing
    SLICE_INC_EXC = auto()  # .,
    SLICE_EXC_EXC = auto()  # ,,
    SLICE_INC_INC = auto()  # ..
    
    # Special
    EOF = auto()
    NEWLINE = auto()

@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        # Keywords mapping
        self.keywords = {
            'class': TokenType.CLASS,
            'public': TokenType.PUBLIC,
            'private': TokenType.PRIVATE,
            'static': TokenType.STATIC,
            'return': TokenType.RETURN,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'elseif': TokenType.ELSEIF,
            'loop': TokenType.LOOP,
            'for': TokenType.FOR,
            'until': TokenType.UNTIL,
            'new': TokenType.NEW,
            'not': TokenType.NOT,
            'inherits': TokenType.INHERITS,
            'thisclass': TokenType.THISCLASS,
            'parent': TokenType.PARENT,
            'isa': TokenType.ISA,
            'import': TokenType.IMPORT,
            
            # Types
            'boolean': TokenType.BOOLEAN,
            'integer': TokenType.INTEGER,
            'longinteger': TokenType.LONGINTEGER,
            'float': TokenType.FLOAT,
            'longfloat': TokenType.LONGFLOAT,
            'string': TokenType.STRING,
            'character': TokenType.CHARACTER,
            'void': TokenType.VOID,
            'enumerated': TokenType.ENUMERATED,
            
            # Boolean literals
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
        }
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset=1) -> Optional[str]:
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self):
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r\n':
            self.advance()
    
    def skip_comment(self):
        # Single-line comment //
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
            self.advance()  # Skip the newline
            return True
        
        # Multi-line comment /* */
        if self.current_char() == '/' and self.peek_char() == '*':
            self.advance()  # Skip /
            self.advance()  # Skip *
            while self.current_char():
                if self.current_char() == '*' and self.peek_char() == '/':
                    self.advance()  # Skip *
                    self.advance()  # Skip /
                    return True
                self.advance()
            raise SyntaxError(
                f"Unclosed multi-line comment starting at line {self.line}, column {self.column}\n"
                f"Multi-line comments must be closed with */."
            )
        
        return False
    
    def read_number(self) -> Token:
        start_line = self.line
        start_col = self.column
        num_str = ''
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                # Check if it's a slice operator
                next_char = self.peek_char()
                if next_char in '.,':
                    break
                if has_dot:
                    break
                has_dot = True
            num_str += self.current_char()
            self.advance()
        
        value = float(num_str) if has_dot else int(num_str)
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_string(self) -> Token:
        start_line = self.line
        start_col = self.column
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        string_val = ''
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                # Handle escape sequences
                escape_char = self.current_char()
                if escape_char == 'n':
                    string_val += '\n'
                elif escape_char == 't':
                    string_val += '\t'
                elif escape_char == '\\':
                    string_val += '\\'
                elif escape_char == quote_char:
                    string_val += quote_char
                else:
                    string_val += escape_char
                self.advance()
            else:
                string_val += self.current_char()
                self.advance()
        
        if not self.current_char():
            raise SyntaxError(
                f"Unterminated string starting at line {start_line}, column {start_col}\n"
                f"Strings must be closed with a matching quote ({quote_char})."
            )
        
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING_LITERAL, string_val, start_line, start_col)
    
    def read_identifier(self) -> Token:
        start_line = self.line
        start_col = self.column
        identifier = ''
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            identifier += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
        return Token(token_type, identifier, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            # Skip comments
            if self.skip_comment():
                continue
            
            char = self.current_char()
            line = self.line
            col = self.column
            
            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Strings
            if char in '"\'':
                self.tokens.append(self.read_string())
                continue
            
            # Special check for V and VV operators (must come before identifier check)
            # But only if V is not part of a larger identifier
            if char == 'V':
                next_ch = self.peek_char()
                # Check if next char could be part of an identifier
                if next_ch and (next_ch.isalnum() or next_ch == '_'):
                    # V is part of an identifier, let it be handled below
                    pass
                elif next_ch == 'V':
                    # VV operator
                    self.tokens.append(Token(TokenType.XOR, 'VV', line, col))
                    self.advance()
                    self.advance()
                    continue
                else:
                    # V operator (OR)
                    self.tokens.append(Token(TokenType.OR, 'V', line, col))
                    self.advance()
                    continue
            
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Two-character operators
            next_char = self.peek_char()
            
            # Arrow ->
            if char == '-' and next_char == '>':
                self.tokens.append(Token(TokenType.ARROW, '->', line, col))
                self.advance()
                self.advance()
                continue
            
            # Increment ++
            if char == '+' and next_char == '+':
                self.tokens.append(Token(TokenType.INCREMENT, '++', line, col))
                self.advance()
                self.advance()
                continue
            
            # Decrement --
            if char == '-' and next_char == '-':
                self.tokens.append(Token(TokenType.DECREMENT, '--', line, col))
                self.advance()
                self.advance()
                continue
            
            # Equal ==
            if char == '=' and next_char == '=':
                self.tokens.append(Token(TokenType.EQUAL, '==', line, col))
                self.advance()
                self.advance()
                continue
            
            # Greater or equal >=
            if char == '>' and next_char == '=':
                self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', line, col))
                self.advance()
                self.advance()
                continue
            
            # Less or equal <=
            if char == '<' and next_char == '=':
                self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', line, col))
                self.advance()
                self.advance()
                continue
            
            # Slice operators ., ,, ..
            if char == '.':
                if next_char == ',':
                    self.tokens.append(Token(TokenType.SLICE_INC_EXC, '.,', line, col))
                    self.advance()
                    self.advance()
                    continue
                elif next_char == '.':
                    self.tokens.append(Token(TokenType.SLICE_INC_INC, '..', line, col))
                    self.advance()
                    self.advance()
                    continue
            
            if char == ',' and next_char == ',':
                self.tokens.append(Token(TokenType.SLICE_EXC_EXC, ',,', line, col))
                self.advance()
                self.advance()
                continue
            
            # Single-character operators
            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '%': TokenType.MODULUS,
                '^': TokenType.POWER,
                '>': TokenType.GREATER,
                '<': TokenType.LESS,
                '&': TokenType.AND,
                '=': TokenType.ASSIGN,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                '.': TokenType.DOT,
            }
            
            if char in single_char_tokens:
                self.tokens.append(Token(single_char_tokens[char], char, line, col))
                self.advance()
                continue
            
            # Unknown character
            raise SyntaxError(
                f"Unexpected character '{char}' at line {line}, column {col}\n"
                f"This character is not recognized by FOOBAR. Check for typos or invalid symbols."
            )
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

# Test the lexer
if __name__ == '__main__':
    test_code = '''
    Main() {
        integer x = 42;
        CONSOLE.Print("Hello, World!");
        return true;
    }
    '''
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    for token in tokens:
        print(token)
