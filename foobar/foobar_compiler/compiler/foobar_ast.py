"""
FOOBAR AST (Abstract Syntax Tree) Node Definitions
"""

from dataclasses import dataclass
from typing import List, Optional, Any

# Base node
@dataclass
class ASTNode:
    pass

# Program root
@dataclass
class Program(ASTNode):
    imports: List['ImportDecl']  # Import declarations
    declarations: List[ASTNode]  # Classes, methods, enums

# Import declaration
@dataclass
class ImportDecl(ASTNode):
    filepath: str  # The file path to import

# Type reference
@dataclass
class Type(ASTNode):
    name: str
    is_array: bool = False

# Declarations
@dataclass
class ClassDecl(ASTNode):
    name: str
    parent_classes: List[str]  # List of parent class names for multiple inheritance
    members: List[ASTNode]  # Fields and methods

@dataclass
class MethodDecl(ASTNode):
    name: str
    return_type: Optional[Type]  # None for Main()
    parameters: List['Parameter']
    body: 'Block'
    is_public: bool = False

@dataclass
class Parameter(ASTNode):
    name: str
    param_type: Type

@dataclass
class FieldDecl(ASTNode):
    name: str
    field_type: Type
    is_public: bool = False
    initial_value: Optional['Expression'] = None

@dataclass
class EnumDecl(ASTNode):
    name: str
    values: List[str]

# Statements
@dataclass
class Block(ASTNode):
    statements: List['Statement']

@dataclass
class Statement(ASTNode):
    pass

@dataclass
class VarDecl(Statement):
    name: str
    var_type: Type
    initial_value: Optional['Expression'] = None

@dataclass
class ExpressionStmt(Statement):
    expression: 'Expression'

@dataclass
class ReturnStmt(Statement):
    value: Optional['Expression']

@dataclass
class IfStmt(Statement):
    condition: 'Expression'
    then_block: Block
    elseif_parts: List[tuple['Expression', Block]]  # List of (condition, block)
    else_block: Optional[Block]

@dataclass
class LoopForStmt(Statement):
    count: 'Expression'  # Can be a number or variable
    body: Block

@dataclass
class LoopUntilStmt(Statement):
    condition: 'Expression'
    body: Block

# Expressions
@dataclass
class Expression(ASTNode):
    pass

@dataclass
class BinaryOp(Expression):
    left: Expression
    operator: str  # +, -, *, /, ^, ==, >, <, &, V, VV
    right: Expression

@dataclass
class UnaryOp(Expression):
    operator: str  # not, ++, --
    operand: Expression
    is_prefix: bool = True

@dataclass
class Literal(Expression):
    value: Any  # int, float, str, bool

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class ArrayLiteral(Expression):
    elements: List[Expression]

@dataclass
class ArrayAccess(Expression):
    array: Expression
    index: Expression

@dataclass
class ArraySlice(Expression):
    array: Expression
    start: Expression
    end: Expression
    slice_type: str  # '.,', ',,', '..'

@dataclass
class MethodCall(Expression):
    object: Optional[Expression]  # None for standalone functions
    method_name: str
    arguments: List[Expression]

@dataclass
class MemberAccess(Expression):
    object: Expression
    member_name: str

@dataclass
class Lambda(Expression):
    parameters: List[str]  # Simple parameter names (types inferred)
    body: Expression

@dataclass
class Assignment(Expression):
    target: Expression  # Identifier or array access
    value: Expression

@dataclass
class NewInstance(Expression):
    class_name: str
    arguments: List[Expression]

@dataclass
class ThisClass(Expression):
    pass

@dataclass
class NewInstance(Expression):
    class_name: str
    arguments: List[Expression]

@dataclass
class ThisClass(Expression):
    pass

@dataclass
class Parent(Expression):
    pass

@dataclass
class IsA(Expression):
    object: Expression
    class_name: str
