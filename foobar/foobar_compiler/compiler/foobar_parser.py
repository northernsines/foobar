"""
FOOBAR Parser
Builds an Abstract Syntax Tree from a stream of tokens
"""

from foobar_lexer import Token, TokenType, Lexer
from foobar_ast import *
from typing import List, Optional

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]
    
    def peek_token(self, offset=1) -> Token:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def expect(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != token_type:
            # Provide helpful error messages
            expected = token_type.name.replace('_', ' ').lower()
            got = token.type.name.replace('_', ' ').lower()
            
            hint = ""
            if token_type == TokenType.SEMICOLON:
                hint = "\nDid you forget a semicolon (;) at the end of the statement?"
            elif token_type == TokenType.RPAREN:
                hint = "\nDid you forget a closing parenthesis )?"
            elif token_type == TokenType.RBRACE:
                hint = "\nDid you forget a closing brace }?"
            elif token_type == TokenType.IDENTIFIER:
                hint = "\nExpected a variable or function name here."
            
            raise SyntaxError(
                f"Syntax error at line {token.line}, column {token.column}\n"
                f"Expected {expected}, but got {got}{hint}"
            )
        self.advance()
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        return self.current_token().type in token_types
    
    def parse(self) -> Program:
        declarations = []
        
        while not self.match(TokenType.EOF):
            if self.match(TokenType.CLASS):
                declarations.append(self.parse_class())
            elif self.match(TokenType.ENUMERATED):
                declarations.append(self.parse_enum())
            else:
                # Check for public/private modifier
                is_public = False
                if self.match(TokenType.PUBLIC):
                    is_public = True
                    self.advance()
                elif self.match(TokenType.PRIVATE):
                    self.advance()
                
                # Top-level method (including Main)
                declarations.append(self.parse_method(is_public))
        
        return Program(declarations)
    
    def parse_class(self) -> ClassDecl:
        self.expect(TokenType.CLASS)
        name = self.expect(TokenType.IDENTIFIER).value
        
        # Check for inheritance
        parent_classes = []
        if self.match(TokenType.INHERITS):
            self.advance()
            # Parse comma-separated list of parent classes
            parent_classes.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                self.advance()
                parent_classes.append(self.expect(TokenType.IDENTIFIER).value)
        
        self.expect(TokenType.LBRACE)
        
        members = []
        while not self.match(TokenType.RBRACE):
            # Check for public/private
            is_public = False
            if self.match(TokenType.PUBLIC):
                is_public = True
                self.advance()
            elif self.match(TokenType.PRIVATE):
                self.advance()
            
            # Now check if it's Initialize (special method with no return type)
            if self.match(TokenType.IDENTIFIER) and self.current_token().value == "Initialize":
                # It's the Initialize method
                method_name = self.current_token().value
                self.advance()
                self.expect(TokenType.LPAREN)
                
                parameters = []
                while not self.match(TokenType.RPAREN):
                    param_type = self.parse_type()
                    param_name = self.expect(TokenType.IDENTIFIER).value
                    parameters.append(Parameter(param_name, param_type))
                    
                    if self.match(TokenType.COMMA):
                        self.advance()
                
                self.expect(TokenType.RPAREN)
                body = self.parse_block()
                # Initialize doesn't have a return type
                members.append(MethodDecl(method_name, None, parameters, body, is_public))
                continue
            
            # Check if it's a method or field
            # Save position and look ahead
            saved_pos = self.pos
            
            # Try to parse as type
            try:
                # Skip type tokens
                type_start = self.pos
                self.parse_type()  # This will consume the type
                
                # Now check if next is identifier followed by (
                if self.match(TokenType.IDENTIFIER):
                    id_name = self.current_token().value
                    self.advance()
                    if self.match(TokenType.LPAREN):
                        # It's a method!
                        self.pos = saved_pos  # Reset
                        members.append(self.parse_method(is_public))
                        continue
                
                # It's a field
                self.pos = saved_pos  # Reset
                members.append(self.parse_field(is_public))
            except:
                # Couldn't parse as type, something's wrong
                raise SyntaxError(f"Expected class member at {self.current_token().line}:{self.current_token().column}")
        
        self.expect(TokenType.RBRACE)
        return ClassDecl(name, parent_classes, members)
    
    def parse_field(self, is_public: bool = False) -> FieldDecl:
        field_type = self.parse_type()
        name = self.expect(TokenType.IDENTIFIER).value
        
        initial_value = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initial_value = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        return FieldDecl(name, field_type, is_public, initial_value)
    
    def parse_enum(self) -> EnumDecl:
        self.expect(TokenType.ENUMERATED)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACE)
        
        values = []
        while not self.match(TokenType.RBRACE):
            values.append(self.expect(TokenType.IDENTIFIER).value)
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.expect(TokenType.RBRACE)
        self.expect(TokenType.SEMICOLON)
        return EnumDecl(name, values)
    
    def parse_method(self, is_public: bool = False) -> MethodDecl:
        # Check if it's Main()
        if self.current_token().value == 'Main':
            name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.LPAREN)
            self.expect(TokenType.RPAREN)
            body = self.parse_block()
            return MethodDecl(name, None, [], body, is_public)
        
        # Regular method with return type
        return_type = self.parse_type()
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        
        parameters = []
        while not self.match(TokenType.RPAREN):
            param_type = self.parse_type()
            param_name = self.expect(TokenType.IDENTIFIER).value
            parameters.append(Parameter(param_name, param_type))
            
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.expect(TokenType.RPAREN)
        body = self.parse_block()
        return MethodDecl(name, return_type, parameters, body, is_public)
    
    def parse_type(self) -> Type:
        # Handle primitive types
        type_tokens = [
            TokenType.BOOLEAN, TokenType.INTEGER, TokenType.LONGINTEGER,
            TokenType.FLOAT, TokenType.LONGFLOAT, TokenType.STRING,
            TokenType.CHARACTER, TokenType.VOID
        ]
        
        type_name = None
        if self.match(*type_tokens):
            type_name = self.current_token().value
            self.advance()
        elif self.match(TokenType.IDENTIFIER):
            # User-defined type (class name)
            type_name = self.current_token().value
            self.advance()
        else:
            raise SyntaxError(
                f"Type error at line {self.current_token().line}, column {self.current_token().column}\n"
                f"Expected a type (like integer, boolean, string, or a class name), but got {self.current_token().type.name.lower()}\n"
                f"Valid types: boolean, integer, longinteger, float, longfloat, string, character, void, or a class name"
            )
        
        # Check for array type
        is_array = False
        if self.match(TokenType.LBRACKET):
            self.advance()
            self.expect(TokenType.RBRACKET)
            is_array = True
        
        return Type(type_name, is_array)
    
    def parse_block(self) -> Block:
        self.expect(TokenType.LBRACE)
        statements = []
        
        while not self.match(TokenType.RBRACE):
            statements.append(self.parse_statement())
        
        self.expect(TokenType.RBRACE)
        return Block(statements)
    
    def parse_statement(self) -> Statement:
        # Return statement
        if self.match(TokenType.RETURN):
            self.advance()
            value = None
            if not self.match(TokenType.SEMICOLON):
                value = self.parse_expression()
            self.expect(TokenType.SEMICOLON)
            return ReturnStmt(value)
        
        # If statement
        if self.match(TokenType.IF):
            return self.parse_if()
        
        # Loop statements
        if self.match(TokenType.LOOP):
            return self.parse_loop()
        
        # Variable declaration (starts with a type or class name)
        type_tokens = [
            TokenType.BOOLEAN, TokenType.INTEGER, TokenType.LONGINTEGER,
            TokenType.FLOAT, TokenType.LONGFLOAT, TokenType.STRING,
            TokenType.CHARACTER
        ]
        
        # Check if it's a type token OR an identifier (could be a class name)
        if self.match(*type_tokens) or (self.match(TokenType.IDENTIFIER) and self.peek_token().type in [TokenType.IDENTIFIER, TokenType.LBRACKET]):
            var_type = self.parse_type()
            name = self.expect(TokenType.IDENTIFIER).value
            
            initial_value = None
            if self.match(TokenType.ASSIGN):
                self.advance()
                initial_value = self.parse_expression()
            
            self.expect(TokenType.SEMICOLON)
            return VarDecl(name, var_type, initial_value)
        
        # Expression statement (assignment, method call, etc.)
        expr = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return ExpressionStmt(expr)
    
    def parse_if(self) -> IfStmt:
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        then_block = self.parse_block()
        
        elseif_parts = []
        while self.match(TokenType.ELSEIF):
            self.advance()
            self.expect(TokenType.LPAREN)
            elseif_condition = self.parse_expression()
            self.expect(TokenType.RPAREN)
            elseif_block = self.parse_block()
            elseif_parts.append((elseif_condition, elseif_block))
        
        else_block = None
        if self.match(TokenType.ELSE):
            self.advance()
            self.expect(TokenType.LPAREN)
            self.expect(TokenType.RPAREN)
            else_block = self.parse_block()
        
        return IfStmt(condition, then_block, elseif_parts, else_block)
    
    def parse_loop(self) -> Statement:
        self.expect(TokenType.LOOP)
        
        if self.match(TokenType.FOR):
            self.advance()
            self.expect(TokenType.LPAREN)
            count = self.parse_expression()
            self.expect(TokenType.RPAREN)
            body = self.parse_block()
            return LoopForStmt(count, body)
        
        if self.match(TokenType.UNTIL):
            self.advance()
            self.expect(TokenType.LPAREN)
            condition = self.parse_expression()
            self.expect(TokenType.RPAREN)
            body = self.parse_block()
            return LoopUntilStmt(condition, body)
        
        raise SyntaxError(
            f"Expected 'for' or 'until' after 'loop' at "
            f"{self.current_token().line}:{self.current_token().column}"
        )
    
    def parse_expression(self) -> Expression:
        return self.parse_assignment()
    
    def parse_assignment(self) -> Expression:
        expr = self.parse_xor()
        
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
            return Assignment(expr, value)
        
        return expr
    
    def parse_xor(self) -> Expression:
        left = self.parse_or()
        
        while self.match(TokenType.XOR):
            op = self.current_token().value
            self.advance()
            right = self.parse_or()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_or(self) -> Expression:
        left = self.parse_and()
        
        while self.match(TokenType.OR):
            op = self.current_token().value
            self.advance()
            right = self.parse_and()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_and(self) -> Expression:
        left = self.parse_comparison()
        
        while self.match(TokenType.AND):
            op = self.current_token().value
            self.advance()
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_comparison(self) -> Expression:
        left = self.parse_additive()
        
        # Handle isa specially (it's not like other comparison operators)
        if self.match(TokenType.ISA):
            self.advance()
            class_name = self.expect(TokenType.IDENTIFIER).value
            return IsA(left, class_name)
        
        while self.match(TokenType.EQUAL, TokenType.GREATER, TokenType.LESS, 
                         TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL):
            op = self.current_token().value
            self.advance()
            right = self.parse_additive()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_additive(self) -> Expression:
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.current_token().value
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_multiplicative(self) -> Expression:
        left = self.parse_power()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULUS):
            op = self.current_token().value
            self.advance()
            right = self.parse_power()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_power(self) -> Expression:
        left = self.parse_unary()
        
        if self.match(TokenType.POWER):
            op = self.current_token().value
            self.advance()
            right = self.parse_power()  # Right associative
            return BinaryOp(left, op, right)
        
        return left
    
    def parse_unary(self) -> Expression:
        # Prefix operators: not, ++, --
        if self.match(TokenType.NOT):
            op = self.current_token().value
            self.advance()
            self.expect(TokenType.LPAREN)
            # Parse the expression up to but not including the closing paren
            operand = self.parse_xor()  # Parse at XOR level to avoid consuming too much
            self.expect(TokenType.RPAREN)
            return UnaryOp(op, operand, True)
        
        if self.match(TokenType.INCREMENT, TokenType.DECREMENT):
            op = self.current_token().value
            self.advance()
            operand = self.parse_postfix()
            return UnaryOp(op, operand, True)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> Expression:
        expr = self.parse_primary()
        
        while True:
            # Array access or slicing
            if self.match(TokenType.LBRACKET):
                self.advance()
                
                # Check for slicing
                if self.match(TokenType.SLICE_INC_EXC, TokenType.SLICE_EXC_EXC, TokenType.SLICE_INC_INC):
                    # Slice starting from 0
                    slice_type = self.current_token().value
                    self.advance()
                    end = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                    expr = ArraySlice(expr, Literal(0), end, slice_type)
                else:
                    index = self.parse_expression()
                    
                    # Check if followed by slice operator
                    if self.match(TokenType.SLICE_INC_EXC, TokenType.SLICE_EXC_EXC, TokenType.SLICE_INC_INC):
                        slice_type = self.current_token().value
                        self.advance()
                        end = self.parse_expression()
                        self.expect(TokenType.RBRACKET)
                        expr = ArraySlice(expr, index, end, slice_type)
                    else:
                        self.expect(TokenType.RBRACKET)
                        expr = ArrayAccess(expr, index)
                
                continue
            
            # Member access or method call
            if self.match(TokenType.DOT):
                self.advance()
                member_name = self.expect(TokenType.IDENTIFIER).value
                
                # Properties that should never be treated as methods (even with parens)
                PROPERTIES = ['length']
                
                # Check if it's a property with optional ()
                if member_name in PROPERTIES:
                    # Allow optional () for properties but ignore them
                    if self.match(TokenType.LPAREN):
                        self.advance()
                        self.expect(TokenType.RPAREN)  # Must be empty parens
                    expr = MemberAccess(expr, member_name)
                # Check if it's a method call
                elif self.match(TokenType.LPAREN):
                    self.advance()
                    args = []
                    while not self.match(TokenType.RPAREN):
                        # Check for lambda - could be:
                        # 1. x -> expr (simple)
                        # 2. (x, y) -> expr (multi-param)
                        
                        # Look for arrow in the next few tokens
                        is_lambda = False
                        if self.current_token().type == TokenType.IDENTIFIER and self.peek_token().type == TokenType.ARROW:
                            # Simple lambda: x -> ...
                            is_lambda = True
                        elif self.current_token().type == TokenType.LPAREN:
                            # Could be multi-param lambda: (x, y) -> ...
                            # Look ahead to find arrow
                            saved_pos = self.pos
                            self.advance()  # Skip (
                            depth = 1
                            while depth > 0 and not self.match(TokenType.EOF):
                                if self.match(TokenType.LPAREN):
                                    depth += 1
                                elif self.match(TokenType.RPAREN):
                                    depth -= 1
                                self.advance()
                            # Now check if next token is arrow
                            if self.match(TokenType.ARROW):
                                is_lambda = True
                            # Restore position
                            self.pos = saved_pos
                        
                        if is_lambda:
                            args.append(self.parse_lambda())
                        else:
                            args.append(self.parse_expression())
                        
                        if self.match(TokenType.COMMA):
                            self.advance()
                    self.expect(TokenType.RPAREN)
                    expr = MethodCall(expr, member_name, args)
                else:
                    expr = MemberAccess(expr, member_name)
                
                continue
            
            # Postfix increment/decrement
            if self.match(TokenType.INCREMENT, TokenType.DECREMENT):
                op = self.current_token().value
                self.advance()
                expr = UnaryOp(op, expr, False)
                continue
            
            break
        
        return expr
    
    def parse_lambda(self) -> Lambda:
        # Simple lambda: x -> expr
        # Or multi-param: (x, y) -> expr
        
        params = []
        if self.match(TokenType.LPAREN):
            self.advance()
            while not self.match(TokenType.RPAREN):
                params.append(self.expect(TokenType.IDENTIFIER).value)
                if self.match(TokenType.COMMA):
                    self.advance()
            self.expect(TokenType.RPAREN)
        else:
            params.append(self.expect(TokenType.IDENTIFIER).value)
        
        self.expect(TokenType.ARROW)
        body = self.parse_expression()
        
        return Lambda(params, body)
    
    def parse_primary(self) -> Expression:
        # new keyword for instance creation
        if self.match(TokenType.NEW):
            self.advance()
            class_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.LPAREN)
            args = []
            while not self.match(TokenType.RPAREN):
                args.append(self.parse_expression())
                if self.match(TokenType.COMMA):
                    self.advance()
            self.expect(TokenType.RPAREN)
            return NewInstance(class_name, args)
        
        # thisclass keyword
        if self.match(TokenType.THISCLASS):
            self.advance()
            return ThisClass()
        
        # parent keyword
        if self.match(TokenType.PARENT):
            self.advance()
            return Parent()
        
        # Literals
        if self.match(TokenType.TRUE):
            self.advance()
            return Literal(True)
        
        if self.match(TokenType.FALSE):
            self.advance()
            return Literal(False)
        
        if self.match(TokenType.NUMBER):
            value = self.current_token().value
            self.advance()
            return Literal(value)
        
        if self.match(TokenType.STRING_LITERAL):
            value = self.current_token().value
            self.advance()
            return Literal(value)
        
        # Array literal
        if self.match(TokenType.LBRACKET):
            self.advance()
            elements = []
            while not self.match(TokenType.RBRACKET):
                elements.append(self.parse_expression())
                if self.match(TokenType.COMMA):
                    self.advance()
            self.expect(TokenType.RBRACKET)
            return ArrayLiteral(elements)
        
        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()
            
            # Check for lambda with typed parameters
            # This would be like: (integer x) -> ...
            # For now, we'll handle simple lambdas only
            
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        # Identifier or method call
        if self.match(TokenType.IDENTIFIER):
            name = self.current_token().value
            self.advance()
            
            # Check for method call
            if self.match(TokenType.LPAREN):
                self.advance()
                args = []
                while not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    if self.match(TokenType.COMMA):
                        self.advance()
                self.expect(TokenType.RPAREN)
                return MethodCall(None, name, args)
            
            return Identifier(name)
        
        raise SyntaxError(
            f"Unexpected token {self.current_token().type.name} "
            f"at {self.current_token().line}:{self.current_token().column}"
        )

# Test the parser
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
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    print(ast)
