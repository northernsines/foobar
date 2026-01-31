"""
FOOBAR to C Code Generator
Transpiles FOOBAR AST to C source code
"""

from foobar_ast import *
from typing import Set, Dict, List as ListType

class CCodeGenerator:
    def __init__(self):
        self.output = []
        self.indent_level = 0
        self.temp_var_counter = 0
        self.lambda_counter = 0
        self.generated_lambdas = []
        self.lambda_generation_mode = False
        self.classes = {}  # name -> ClassDecl
        self.current_class = None
        self.current_method = None
        # Type tracking
        self.global_symbols = {}  # var_name -> type_name
        self.local_symbols = []  # Stack of scopes, each is {var_name -> type_name}
        self.method_signatures = {}  # (class_name, method_name) -> return_type
        
    def mangle_method_name(self, class_name: str, method_name: str, parameters: list) -> str:
        """Generate a unique mangled name for methods to support overloading"""
        if not parameters:
            return f"{class_name}_{method_name}_void"
        
        # Build type suffix from parameter types
        type_suffix = "_".join([self.c_type(p.param_type).replace("*", "ptr").replace(" ", "_") for p in parameters])
        return f"{class_name}_{method_name}_{type_suffix}"
    
    def find_method_overload(self, class_name: str, method_name: str, arguments: list) -> str:
        """Find the correct method overload based on argument types and return mangled name"""
        if class_name not in self.classes:
            # Fallback for unknown classes
            return f"{class_name}_{method_name}"
        
        cls = self.classes[class_name]
        matching_methods = []
        
        # Find all methods with this name
        for member in cls.members:
            if isinstance(member, MethodDecl) and member.name == method_name:
                # Check if parameter count matches
                if len(member.parameters) == len(arguments):
                    matching_methods.append(member)
        
        # If we found exactly one match, use it
        if len(matching_methods) == 1:
            return self.mangle_method_name(class_name, method_name, matching_methods[0].parameters)
        elif len(matching_methods) > 1:
            # Multiple overloads - try to find best match based on argument types
            # For now, just use the first one (type checking would be better)
            return self.mangle_method_name(class_name, method_name, matching_methods[0].parameters)
        else:
            # No exact match - might be inherited method
            # Try parent classes
            for parent_name in cls.parent_classes:
                if parent_name in self.classes:
                    result = self.find_method_overload(parent_name, method_name, arguments)
                    if result != f"{parent_name}_{method_name}":  # Found something
                        # Return mangled name for this class calling parent method
                        parent_cls = self.classes[parent_name]
                        for member in parent_cls.members:
                            if isinstance(member, MethodDecl) and member.name == method_name and len(member.parameters) == len(arguments):
                                return self.mangle_method_name(class_name, method_name, member.parameters)
            
            # Fallback
            return f"{class_name}_{method_name}"
    
    def push_scope(self):
        """Enter a new scope"""
        self.local_symbols.append({})
    
    def pop_scope(self):
        """Exit current scope"""
        if self.local_symbols:
            self.local_symbols.pop()
    
    def add_symbol(self, name: str, type_name: str):
        """Add a variable to current scope"""
        if self.local_symbols:
            self.local_symbols[-1][name] = type_name
        else:
            self.global_symbols[name] = type_name
    
    def get_symbol_type(self, name: str) -> Optional[str]:
        """Get type of a variable"""
        # Search local scopes from innermost to outermost
        for scope in reversed(self.local_symbols):
            if name in scope:
                return scope[name]
        # Search global scope
        if name in self.global_symbols:
            return self.global_symbols[name]
        return None
    
    def infer_expression_type(self, expr: Expression) -> Optional[str]:
        """Infer the type of an expression"""
        if isinstance(expr, Literal):
            val = expr.value
            if isinstance(val, bool):
                return "boolean"
            elif isinstance(val, int):
                return "integer"
            elif isinstance(val, float):
                return "float"
            elif isinstance(val, str):
                return "string"
        elif isinstance(expr, Identifier):
            result = self.get_symbol_type(expr.name)
            return result
        elif isinstance(expr, NewInstance):
            return expr.class_name
        elif isinstance(expr, ThisClass):
            return self.current_class
        elif isinstance(expr, MethodCall):
            # Try to infer return type from method signature
            if expr.object:
                obj_type = self.infer_expression_type(expr.object)
                
                # Special handling for array transformation methods
                if obj_type and '[]' in obj_type:
                    if expr.method_name == 'map':
                        # map returns same array type
                        return obj_type
                    elif expr.method_name == 'filter':
                        # filter returns same array type
                        return obj_type
                    elif expr.method_name == 'sort':
                        # sort returns same array type
                        return obj_type
                    elif expr.method_name == 'unique':
                        # unique returns same array type
                        return obj_type
                    elif expr.method_name == 'reduce':
                        # reduce returns the element type (not array)
                        return obj_type.replace('[]', '')
                    elif expr.method_name == 'find':
                        # find returns the element type
                        return obj_type.replace('[]', '')
                
                if obj_type and (obj_type, expr.method_name) in self.method_signatures:
                    return self.method_signatures[(obj_type, expr.method_name)]
            return None
        elif isinstance(expr, BinaryOp):
            # Check if either operand is an array
            left_type = self.infer_expression_type(expr.left)
            right_type = self.infer_expression_type(expr.right)
            if left_type and '[]' in left_type:
                return left_type
            if right_type and '[]' in right_type:
                return right_type
            # For now, assume arithmetic returns integer
            return "integer"
        elif isinstance(expr, ArrayLiteral):
            # Infer array type from first element
            if expr.elements:
                first_elem_type = self.infer_expression_type(expr.elements[0])
                if first_elem_type:
                    return f"{first_elem_type}[]"
            return "integer[]"  # Default fallback
        return None
        
    def collect_all_lambdas(self, program: Program):
        """First pass: walk the AST and collect all lambda expressions"""
        self.lambda_generation_mode = True
        for decl in program.declarations:
            if isinstance(decl, MethodDecl):
                self.collect_lambdas_from_block(decl.body)
        self.lambda_generation_mode = False
    
    def collect_lambdas_from_block(self, block: Block):
        """Recursively collect lambdas from a block"""
        for stmt in block.statements:
            self.collect_lambdas_from_statement(stmt)
    
    def collect_lambdas_from_statement(self, stmt: Statement):
        """Recursively collect lambdas from a statement"""
        if isinstance(stmt, VarDecl):
            # Add variable to symbol table so type inference works
            type_name = stmt.var_type.name
            if stmt.var_type.is_array:
                type_name = type_name + "[]"
            self.add_symbol(stmt.name, type_name)
            # Then process its initial value
            if stmt.initial_value:
                self.collect_lambdas_from_expression(stmt.initial_value)
        elif isinstance(stmt, ExpressionStmt):
            self.collect_lambdas_from_expression(stmt.expression)
        elif isinstance(stmt, ReturnStmt) and stmt.value:
            self.collect_lambdas_from_expression(stmt.value)
        elif isinstance(stmt, IfStmt):
            self.collect_lambdas_from_expression(stmt.condition)
            self.collect_lambdas_from_block(stmt.then_block)
            for cond, block in stmt.elseif_parts:
                self.collect_lambdas_from_expression(cond)
                self.collect_lambdas_from_block(block)
            if stmt.else_block:
                self.collect_lambdas_from_block(stmt.else_block)
        elif isinstance(stmt, LoopForStmt):
            self.collect_lambdas_from_expression(stmt.count)
            self.collect_lambdas_from_block(stmt.body)
        elif isinstance(stmt, LoopUntilStmt):
            self.collect_lambdas_from_expression(stmt.condition)
            self.collect_lambdas_from_block(stmt.body)
    
    def collect_lambdas_from_expression(self, expr: Expression, context_type: Optional[str] = None):
        """Recursively collect lambdas from an expression
        context_type: The array element type if this expression is in an array operation context
        """
        if isinstance(expr, Lambda):
            # Generate with context if available, otherwise default to int
            if context_type:
                param_type = self.get_c_element_type(context_type)
                return_type = param_type  # For now, assume same type (works for map)
                self.generate_lambda_definition(expr, param_type, return_type)
            else:
                # Default to int if no context
                self.generate_lambda_definition(expr, "int", "int")
        elif isinstance(expr, MethodCall):
            # Check if this is an array operation - if so, pass context to lambda arguments
            if expr.object:
                obj_type = self.infer_expression_type(expr.object)
                if obj_type and '[]' in obj_type and expr.method_name in ['map', 'filter', 'reduce', 'find']:
                    base_type = obj_type.replace('[]', '')
                    # Process lambda arguments with context
                    for i, arg in enumerate(expr.arguments):
                        if isinstance(arg, Lambda):
                            if expr.method_name == 'map':
                                self.collect_lambdas_from_expression(arg, base_type)
                            elif expr.method_name == 'filter' or expr.method_name == 'find':
                                # filter/find: elem_type -> bool
                                param_type = self.get_c_element_type(base_type)
                                self.generate_lambda_definition(arg, param_type, "int")
                            elif expr.method_name == 'reduce' and i == 0:
                                # reduce: (acc_type, elem_type) -> acc_type
                                param_type = self.get_c_element_type(base_type)
                                self.generate_lambda_definition(arg, param_type, param_type)
                        else:
                            self.collect_lambdas_from_expression(arg, context_type)
                    # Process the object too
                    self.collect_lambdas_from_expression(expr.object, context_type)
                else:
                    # Not an array operation, process normally
                    self.collect_lambdas_from_expression(expr.object, context_type)
                    for arg in expr.arguments:
                        self.collect_lambdas_from_expression(arg, context_type)
            else:
                for arg in expr.arguments:
                    self.collect_lambdas_from_expression(arg, context_type)
        elif isinstance(expr, BinaryOp):
            self.collect_lambdas_from_expression(expr.left)
            self.collect_lambdas_from_expression(expr.right)
        elif isinstance(expr, UnaryOp):
            self.collect_lambdas_from_expression(expr.operand)
        elif isinstance(expr, Assignment):
            self.collect_lambdas_from_expression(expr.target)
            self.collect_lambdas_from_expression(expr.value)
        elif isinstance(expr, ArrayLiteral):
            for elem in expr.elements:
                self.collect_lambdas_from_expression(elem)
        elif isinstance(expr, ArrayAccess):
            self.collect_lambdas_from_expression(expr.array)
            self.collect_lambdas_from_expression(expr.index)
        elif isinstance(expr, MethodCall):
            if expr.object:
                self.collect_lambdas_from_expression(expr.object)
            for arg in expr.arguments:
                self.collect_lambdas_from_expression(arg)
        elif isinstance(expr, MemberAccess):
            self.collect_lambdas_from_expression(expr.object)
    
    def generate_lambda_definition(self, expr: Lambda, param_type: str = "int", return_type: str = "int"):
        """Generate a lambda function definition with specified types"""
        lambda_name = f"lambda_{self.lambda_counter}"
        self.lambda_counter += 1
        
        # Use provided types or default to int
        params = ', '.join([f"{param_type} {p}" for p in expr.parameters])
        
        # Generate the body expression
        # We need to temporarily generate this to get the C code
        saved_mode = self.lambda_generation_mode
        self.lambda_generation_mode = False
        body_expr = self.generate_expression(expr.body)
        self.lambda_generation_mode = saved_mode
        
        lambda_def = f"static {return_type} {lambda_name}({params}) {{\n"
        lambda_def += f"    return {body_expr};\n"
        lambda_def += "}"
        
        # Insert lambda at the remembered position (after "// Lambda functions" header)
        self.output.insert(self.lambda_section_index, lambda_def)
        self.output.insert(self.lambda_section_index + 1, "")
        self.lambda_section_index += 2  # Account for the lines we just added
        
        # Store the lambda name for later use
        if not hasattr(expr, '_generated_name'):
            expr._generated_name = lambda_name
        
    def generate(self, program: Program) -> str:
        # Header
        self.emit("#include <stdio.h>")
        self.emit("#include <stdlib.h>")
        self.emit("#include <stdbool.h>")
        self.emit("#include <string.h>")
        self.emit("#include <math.h>")
        self.emit("#include <time.h>")
        self.emit("#include <ctype.h>")
        self.emit("")
        self.emit("// Simple GC replacement (no actual GC)")
        self.emit("#define GC_INIT()")
        self.emit("#define GC_MALLOC malloc")
        self.emit("")
        
        # FIRST: collect class definitions and build method signatures
        # This must happen BEFORE forward declarations!
        for decl in program.declarations:
            if isinstance(decl, ClassDecl):
                self.classes[decl.name] = decl
                # Register method signatures
                for member in decl.members:
                    if isinstance(member, MethodDecl):
                        return_type = member.return_type.name if member.return_type else "void"
                        self.method_signatures[(decl.name, member.name)] = return_type
        
        # NOW generate forward declarations
        self.emit("// Forward declarations")
        self.emit("bool Main_internal(void);")
        
        # Forward declare array types
        self.emit("typedef struct IntArray_s IntArray;")
        self.emit("typedef struct FloatArray_s FloatArray;")
        self.emit("typedef struct LongFloatArray_s LongFloatArray;")
        self.emit("typedef struct LongIntArray_s LongIntArray;")
        self.emit("typedef struct BoolArray_s BoolArray;")
        self.emit("typedef struct CharArray_s CharArray;")
        self.emit("typedef struct StringArray_s StringArray;")
        self.emit("")
        
        # Forward declare class types
        for class_name in self.classes:
            self.emit(f"typedef struct {class_name}_s {class_name};")
        
        # Forward declare constructors and all class methods
        for class_name, cls in self.classes.items():
            # Find ALL Initialize methods (there may be multiple for overloading)
            init_methods = []
            for member in cls.members:
                if isinstance(member, MethodDecl) and member.name == "Initialize":
                    init_methods.append(member)
            
            # Forward declare ALL constructors (one per Initialize overload)
            for init_method in init_methods:
                params = ', '.join([f"{self.c_type(p.param_type)} {p.name}" for p in init_method.parameters])
                mangled_name = self.mangle_method_name(class_name, "new", init_method.parameters)
                if params:
                    self.emit(f"{class_name}* {mangled_name}({params});")
                else:
                    self.emit(f"{class_name}* {mangled_name}(void);")
            
            # If no Initialize methods, forward declare default constructor
            if not init_methods:
                self.emit(f"{class_name}* {class_name}_new_void(void);")
            
            # Forward declare all methods (including Initialize) with mangled names
            for member in cls.members:
                if isinstance(member, MethodDecl):
                    return_type = self.c_type(member.return_type) if member.return_type else "void"
                    params = [f"{class_name}* thisclass"] + [f"{self.c_type(p.param_type)} {p.name}" for p in member.parameters]
                    params_str = ', '.join(params)
                    mangled_name = self.mangle_method_name(class_name, member.name, member.parameters)
                    self.emit(f"{return_type} {mangled_name}({params_str});")
            
            # Forward declare inherited methods (wrappers)
            for parent_name in cls.parent_classes:
                if parent_name in self.classes:
                    parent_cls = self.classes[parent_name]
                    for parent_member in parent_cls.members:
                        if isinstance(parent_member, MethodDecl):
                            # Check if this class overrides it
                            overridden = False
                            for member in cls.members:
                                if isinstance(member, MethodDecl) and member.name == parent_member.name:
                                    # Check if parameters match for exact override
                                    if len(member.parameters) == len(parent_member.parameters):
                                        param_match = all(m.param_type.name == p.param_type.name 
                                                        for m, p in zip(member.parameters, parent_member.parameters))
                                        if param_match:
                                            overridden = True
                                            break
                            
                            # If not overridden and not Initialize, forward declare the wrapper
                            if not overridden and parent_member.name != "Initialize":
                                return_type = self.c_type(parent_member.return_type) if parent_member.return_type else "void"
                                params = [f"{class_name}* thisclass"] + [f"{self.c_type(p.param_type)} {p.name}" for p in parent_member.parameters]
                                params_str = ', '.join(params)
                                mangled_name = self.mangle_method_name(class_name, parent_member.name, parent_member.parameters)
                                self.emit(f"{return_type} {mangled_name}({params_str});")
        
        # Forward declare standalone methods
        for decl in program.declarations:
            if isinstance(decl, MethodDecl) and decl.name != "Main":
                self.generate_method_forward_decl(decl)
        
        # We'll add lambda forward declarations after we know about them
        self.lambda_forward_decls = []
        self.emit("")
        
        # Don't collect lambdas here - do it per-method when symbols are available
        # self.collect_all_lambdas(program)
        
        # Generate lambda functions section header (lambdas will be added as we find them)
        self.emit("// Lambda functions")
        # Placeholder - actual lambdas added during method generation
        self.lambda_section_index = len(self.output)  # Remember where to insert lambdas
        self.emit("")
        
        # CONSOLE implementation
        self.generate_console_class()
        
        # Array helper functions
        self.generate_array_helpers()
        
        # Generate classes, methods, etc.
        for decl in program.declarations:
            if isinstance(decl, ClassDecl):
                self.generate_class(decl)
            elif isinstance(decl, EnumDecl):
                self.generate_enum(decl)
            elif isinstance(decl, MethodDecl):
                if decl.name == "Main":
                    continue  # Handle Main last
                self.generate_method(decl)
        
        # Generate Main
        for decl in program.declarations:
            if isinstance(decl, MethodDecl) and decl.name == "Main":
                self.generate_main(decl)
        
        return '\n'.join(self.output)
    
    def emit(self, code: str = ""):
        if code:
            self.output.append("    " * self.indent_level + code)
        else:
            self.output.append("")
    
    def indent(self):
        self.indent_level += 1
    
    def dedent(self):
        self.indent_level -= 1
    
    def c_type(self, foobar_type: Type) -> str:
        type_map = {
            'boolean': 'bool',
            'integer': 'int',
            'longinteger': 'long long',
            'float': 'float',
            'longfloat': 'double',
            'string': 'char*',
            'character': 'char',
            'void': 'void'
        }
        
        base_type = type_map.get(foobar_type.name, foobar_type.name)
        
        # If it's a user-defined class type, add * for pointer
        if foobar_type.name in self.classes and not foobar_type.is_array:
            base_type = f"{foobar_type.name}*"
        
        if foobar_type.is_array:
            # Return the proper array struct type (e.g., FloatArray* instead of float*)
            array_type = self.get_array_type_name(foobar_type.name)
            return f"{array_type}*"
        
        return base_type
    
    def get_array_type_name(self, base_type: str) -> str:
        """Get the C array struct name for a given FOOBAR type"""
        type_mapping = {
            'integer': 'IntArray',
            'float': 'FloatArray',
            'longfloat': 'LongFloatArray',
            'longinteger': 'LongIntArray',
            'boolean': 'BoolArray',
            'character': 'CharArray',
            'string': 'StringArray'
        }
        # Default to ObjectArray for class types
        return type_mapping.get(base_type, 'ObjectArray')
    
    def get_c_element_type(self, base_type: str) -> str:
        """Get the C type for array elements"""
        type_map = {
            'boolean': 'bool',
            'integer': 'int',
            'longinteger': 'long long',
            'float': 'float',
            'longfloat': 'double',
            'string': 'char*',
            'character': 'char'
        }
        return type_map.get(base_type, 'void*')  # void* for objects
    
    def generate_console_class(self):
        self.emit("// ========================================")
        self.emit("// STANDARD LIBRARY IMPLEMENTATION")
        self.emit("// ========================================")
        self.emit("")
        
        # ===== CONSOLE CLASS =====
        self.emit("// CONSOLE class implementation")
        self.emit("typedef struct {")
        self.indent()
        self.emit("int dummy;  // Placeholder")
        self.dedent()
        self.emit("} CONSOLE_t;")
        self.emit("")
        
        # ANSI color codes
        self.emit("// ANSI color codes for terminal output")
        self.emit("const char* ANSI_COLOR_RED = \"\\033[31m\";")
        self.emit("const char* ANSI_COLOR_GREEN = \"\\033[32m\";")
        self.emit("const char* ANSI_COLOR_YELLOW = \"\\033[33m\";")
        self.emit("const char* ANSI_COLOR_BLUE = \"\\033[34m\";")
        self.emit("const char* ANSI_COLOR_MAGENTA = \"\\033[35m\";")
        self.emit("const char* ANSI_COLOR_CYAN = \"\\033[36m\";")
        self.emit("const char* ANSI_COLOR_WHITE = \"\\033[37m\";")
        self.emit("const char* ANSI_COLOR_BLACK = \"\\033[30m\";")
        self.emit("const char* ANSI_COLOR_RESET = \"\\033[0m\";")
        self.emit("const char* ANSI_BOLD = \"\\033[1m\";")
        self.emit("const char* ANSI_UNDERLINE = \"\\033[4m\";")
        self.emit("")
        
        # Basic Print methods
        self.emit("void CONSOLE_Print(const char* str) {")
        self.indent()
        self.emit("printf(\"%s\\n\", str);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("void CONSOLE_PrintInteger(int val) {")
        self.indent()
        self.emit("printf(\"%d\\n\", val);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("void CONSOLE_PrintBoolean(bool val) {")
        self.indent()
        self.emit("printf(\"%s\\n\", val ? \"true\" : \"false\");")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("void CONSOLE_PrintFloat(float val) {")
        self.indent()
        self.emit("printf(\"%f\\n\", val);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Scan methods
        self.emit("// Read a line of input from the user")
        self.emit("char* CONSOLE_Scan() {")
        self.indent()
        self.emit("char* buffer = (char*)malloc(1024);")
        self.emit("if (fgets(buffer, 1024, stdin) != NULL) {")
        self.indent()
        self.emit("// Remove trailing newline if present")
        self.emit("size_t len = strlen(buffer);")
        self.emit("if (len > 0 && buffer[len-1] == '\\n') {")
        self.indent()
        self.emit("buffer[len-1] = '\\0';")
        self.dedent()
        self.emit("}")
        self.emit("return buffer;")
        self.dedent()
        self.emit("}")
        self.emit("return buffer;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int CONSOLE_ScanInteger() {")
        self.indent()
        self.emit("int val;")
        self.emit("scanf(\"%d\", &val);")
        self.emit("getchar(); // Consume newline")
        self.emit("return val;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("float CONSOLE_ScanFloat() {")
        self.indent()
        self.emit("float val;")
        self.emit("scanf(\"%f\", &val);")
        self.emit("getchar(); // Consume newline")
        self.emit("return val;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool CONSOLE_ScanBoolean() {")
        self.indent()
        self.emit("char* input = CONSOLE_Scan();")
        self.emit("return (strcmp(input, \"true\") == 0 || strcmp(input, \"1\") == 0);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Clear screen
        self.emit("void CONSOLE_Clear() {")
        self.indent()
        self.emit("#ifdef _WIN32")
        self.indent()
        self.emit("system(\"cls\");")
        self.dedent()
        self.emit("#else")
        self.indent()
        self.emit("system(\"clear\");")
        self.dedent()
        self.emit("#endif")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("CONSOLE_t CONSOLE;")
        self.emit("")
        
        # ===== STRING HELPERS =====
        self.emit("// String helper functions")
        self.emit("bool string_equals(const char* s1, const char* s2) {")
        self.indent()
        self.emit("if (s1 == NULL || s2 == NULL) return s1 == s2;")
        self.emit("return strcmp(s1, s2) == 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool string_less_than(const char* s1, const char* s2) {")
        self.indent()
        self.emit("if (s1 == NULL) return s2 != NULL;")
        self.emit("if (s2 == NULL) return false;")
        self.emit("return strcmp(s1, s2) < 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool string_greater_than(const char* s1, const char* s2) {")
        self.indent()
        self.emit("if (s1 == NULL) return false;")
        self.emit("if (s2 == NULL) return s1 != NULL;")
        self.emit("return strcmp(s1, s2) > 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("char* string_concat(const char* s1, const char* s2) {")
        self.indent()
        self.emit("if (s1 == NULL) s1 = \"\";")
        self.emit("if (s2 == NULL) s2 = \"\";")
        self.emit("size_t len1 = strlen(s1);")
        self.emit("size_t len2 = strlen(s2);")
        self.emit("char* result = (char*)malloc(len1 + len2 + 1);")
        self.emit("strcpy(result, s1);")
        self.emit("strcat(result, s2);")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # String instance methods
        self.emit("int string_length(const char* s) {")
        self.indent()
        self.emit("return s ? strlen(s) : 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("char* string_substring(const char* s, int start, int end) {")
        self.indent()
        self.emit("if (!s) return \"\";")
        self.emit("int len = strlen(s);")
        self.emit("if (start < 0) start = 0;")
        self.emit("if (end > len) end = len;")
        self.emit("if (start >= end) return \"\";")
        self.emit("int sub_len = end - start;")
        self.emit("char* result = (char*)malloc(sub_len + 1);")
        self.emit("strncpy(result, s + start, sub_len);")
        self.emit("result[sub_len] = '\\0';")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("char* string_toUpper(const char* s) {")
        self.indent()
        self.emit("if (!s) return \"\";")
        self.emit("int len = strlen(s);")
        self.emit("char* result = (char*)malloc(len + 1);")
        self.emit("for (int i = 0; i < len; i++) {")
        self.indent()
        self.emit("result[i] = toupper(s[i]);")
        self.dedent()
        self.emit("}")
        self.emit("result[len] = '\\0';")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("char* string_toLower(const char* s) {")
        self.indent()
        self.emit("if (!s) return \"\";")
        self.emit("int len = strlen(s);")
        self.emit("char* result = (char*)malloc(len + 1);")
        self.emit("for (int i = 0; i < len; i++) {")
        self.indent()
        self.emit("result[i] = tolower(s[i]);")
        self.dedent()
        self.emit("}")
        self.emit("result[len] = '\\0';")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("char* string_replace(const char* s, const char* old, const char* new) {")
        self.indent()
        self.emit("if (!s || !old || !new) {")
        self.indent()
        self.emit("if (s) {")
        self.indent()
        self.emit("char* copy = (char*)malloc(strlen(s) + 1);")
        self.emit("strcpy(copy, s);")
        self.emit("return copy;")
        self.dedent()
        self.emit("}")
        self.emit("return \"\";")
        self.dedent()
        self.emit("}")
        self.emit("int old_len = strlen(old);")
        self.emit("int new_len = strlen(new);")
        self.emit("int count = 0;")
        self.emit("const char* p = s;")
        self.emit("// Count occurrences")
        self.emit("while ((p = strstr(p, old)) != NULL) {")
        self.indent()
        self.emit("count++;")
        self.emit("p += old_len;")
        self.dedent()
        self.emit("}")
        self.emit("if (count == 0) {")
        self.indent()
        self.emit("char* copy = (char*)malloc(strlen(s) + 1);")
        self.emit("strcpy(copy, s);")
        self.emit("return copy;")
        self.dedent()
        self.emit("}")
        self.emit("// Allocate result")
        self.emit("int result_len = strlen(s) + count * (new_len - old_len);")
        self.emit("char* result = (char*)malloc(result_len + 1);")
        self.emit("char* dest = result;")
        self.emit("p = s;")
        self.emit("while (*p) {")
        self.indent()
        self.emit("const char* match = strstr(p, old);")
        self.emit("if (match == NULL) {")
        self.indent()
        self.emit("strcpy(dest, p);")
        self.emit("break;")
        self.dedent()
        self.emit("}")
        self.emit("// Copy up to match")
        self.emit("int prefix_len = match - p;")
        self.emit("strncpy(dest, p, prefix_len);")
        self.emit("dest += prefix_len;")
        self.emit("// Copy replacement")
        self.emit("strcpy(dest, new);")
        self.emit("dest += new_len;")
        self.emit("p = match + old_len;")
        self.dedent()
        self.emit("}")
        self.emit("*dest = '\\0';")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("char* string_trim(const char* s) {")
        self.indent()
        self.emit("if (!s) return \"\";")
        self.emit("while (*s && isspace(*s)) s++;")
        self.emit("if (*s == 0) return \"\";")
        self.emit("const char* end = s + strlen(s) - 1;")
        self.emit("while (end > s && isspace(*end)) end--;")
        self.emit("int len = end - s + 1;")
        self.emit("char* result = (char*)malloc(len + 1);")
        self.emit("strncpy(result, s, len);")
        self.emit("result[len] = '\\0';")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Type conversions
        self.emit("int string_toInt(const char* s) {")
        self.indent()
        self.emit("return s ? atoi(s) : 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("float string_toFloat(const char* s) {")
        self.indent()
        self.emit("return s ? atof(s) : 0.0f;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("char* int_toString(int val) {")
        self.indent()
        self.emit("char* result = (char*)malloc(32);")
        self.emit("sprintf(result, \"%d\", val);")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("char* float_toString(float val) {")
        self.indent()
        self.emit("char* result = (char*)malloc(32);")
        self.emit("sprintf(result, \"%f\", val);")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("float int_toFloat(int val) {")
        self.indent()
        self.emit("return (float)val;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int float_toInteger(float val) {")
        self.indent()
        self.emit("return (int)val;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # ===== MATH CLASS =====
        self.emit("// MATH class (static)")
        self.emit("const double MATH_PI = 3.14159265358979323846;")
        self.emit("const double MATH_E = 2.71828182845904523536;")
        self.emit("")
        
        self.emit("int MATH_Min(int a, int b) {")
        self.indent()
        self.emit("return (a < b) ? a : b;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int MATH_Max(int a, int b) {")
        self.indent()
        self.emit("return (a > b) ? a : b;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int MATH_Absolute(int val) {")
        self.indent()
        self.emit("return val < 0 ? -val : val;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("double MATH_SquareRoot(double val) {")
        self.indent()
        self.emit("return sqrt(val);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("double MATH_Power(double base, double exp) {")
        self.indent()
        self.emit("return pow(base, exp);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int MATH_Floor(double val) {")
        self.indent()
        self.emit("return (int)floor(val);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int MATH_Ceil(double val) {")
        self.indent()
        self.emit("return (int)ceil(val);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int MATH_Round(double val) {")
        self.indent()
        self.emit("return (int)round(val);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("double MATH_Sine(double val) {")
        self.indent()
        self.emit("return sin(val);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("double MATH_Cosine(double val) {")
        self.indent()
        self.emit("return cos(val);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("double MATH_Tangent(double val) {")
        self.indent()
        self.emit("return tan(val);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("double MATH_Random() {")
        self.indent()
        self.emit("return (double)rand() / RAND_MAX;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int MATH_Clamp(int val, int min_val, int max_val) {")
        self.indent()
        self.emit("if (val < min_val) return min_val;")
        self.emit("if (val > max_val) return max_val;")
        self.emit("return val;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # ===== STRING CLASS (static utilities) =====
        self.emit("// STRING class (static)")
        self.emit("char* STRING_Join(char** arr, int length, const char* delimiter) {")
        self.indent()
        self.emit("if (!arr || length == 0) return \"\";")
        self.emit("int total_len = 0;")
        self.emit("int delim_len = delimiter ? strlen(delimiter) : 0;")
        self.emit("for (int i = 0; i < length; i++) {")
        self.indent()
        self.emit("total_len += arr[i] ? strlen(arr[i]) : 0;")
        self.emit("if (i < length - 1) total_len += delim_len;")
        self.dedent()
        self.emit("}")
        self.emit("char* result = (char*)malloc(total_len + 1);")
        self.emit("result[0] = '\\0';")
        self.emit("for (int i = 0; i < length; i++) {")
        self.indent()
        self.emit("if (arr[i]) strcat(result, arr[i]);")
        self.emit("if (i < length - 1 && delimiter) strcat(result, delimiter);")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool STRING_Contains(const char* s, const char* search) {")
        self.indent()
        self.emit("if (!s || !search) return false;")
        self.emit("return strstr(s, search) != NULL;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool STRING_StartsWith(const char* s, const char* prefix) {")
        self.indent()
        self.emit("if (!s || !prefix) return false;")
        self.emit("return strncmp(s, prefix, strlen(prefix)) == 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool STRING_EndsWith(const char* s, const char* suffix) {")
        self.indent()
        self.emit("if (!s || !suffix) return false;")
        self.emit("int s_len = strlen(s);")
        self.emit("int suffix_len = strlen(suffix);")
        self.emit("if (suffix_len > s_len) return false;")
        self.emit("return strcmp(s + s_len - suffix_len, suffix) == 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int STRING_Length(const char* s) {")
        self.indent()
        self.emit("if (!s) return 0;")
        self.emit("return (int)strlen(s);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # ===== DATETIME CLASS =====
        self.emit("// DATETIME class (static)")
        self.emit("long DATETIME_Now() {")
        self.indent()
        self.emit("return (long)time(NULL);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int DATETIME_Year(long timestamp) {")
        self.indent()
        self.emit("time_t t = (time_t)timestamp;")
        self.emit("struct tm* tm_info = localtime(&t);")
        self.emit("return tm_info->tm_year + 1900;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int DATETIME_Month(long timestamp) {")
        self.indent()
        self.emit("time_t t = (time_t)timestamp;")
        self.emit("struct tm* tm_info = localtime(&t);")
        self.emit("return tm_info->tm_mon + 1;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int DATETIME_Day(long timestamp) {")
        self.indent()
        self.emit("time_t t = (time_t)timestamp;")
        self.emit("struct tm* tm_info = localtime(&t);")
        self.emit("return tm_info->tm_mday;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int DATETIME_Hour(long timestamp) {")
        self.indent()
        self.emit("time_t t = (time_t)timestamp;")
        self.emit("struct tm* tm_info = localtime(&t);")
        self.emit("return tm_info->tm_hour;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int DATETIME_Minute(long timestamp) {")
        self.indent()
        self.emit("time_t t = (time_t)timestamp;")
        self.emit("struct tm* tm_info = localtime(&t);")
        self.emit("return tm_info->tm_min;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int DATETIME_Second(long timestamp) {")
        self.indent()
        self.emit("time_t t = (time_t)timestamp;")
        self.emit("struct tm* tm_info = localtime(&t);")
        self.emit("return tm_info->tm_sec;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # ===== RANDOM CLASS =====
        self.emit("// RANDOM class (static)")
        self.emit("int RANDOM_Integer(int min, int max) {")
        self.indent()
        self.emit("return min + (rand() % (max - min + 1));")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("float RANDOM_Float(float min, float max) {")
        self.indent()
        self.emit("float scale = rand() / (float) RAND_MAX;")
        self.emit("return min + scale * (max - min);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool RANDOM_Boolean() {")
        self.indent()
        self.emit("return rand() % 2 == 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("void RANDOM_Seed(int seed) {")
        self.indent()
        self.emit("srand(seed);")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("char RANDOM_Character() {")
        self.indent()
        self.emit("// Random printable ASCII character (33-126)")
        self.emit("return (char)(33 + (rand() % 94));")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # ===== FILE CLASS =====
        self.emit("// FILE class (static) - using FILECLS to avoid conflict with C FILE")
        self.emit("char* FILECLS_Read(const char* path) {")
        self.indent()
        self.emit("FILE* f = fopen(path, \"r\");")
        self.emit("if (!f) return NULL;")
        self.emit("fseek(f, 0, SEEK_END);")
        self.emit("long size = ftell(f);")
        self.emit("fseek(f, 0, SEEK_SET);")
        self.emit("char* content = (char*)malloc(size + 1);")
        self.emit("fread(content, 1, size, f);")
        self.emit("content[size] = '\\0';")
        self.emit("fclose(f);")
        self.emit("return content;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool FILECLS_Write(const char* path, const char* content) {")
        self.indent()
        self.emit("FILE* f = fopen(path, \"w\");")
        self.emit("if (!f) return false;")
        self.emit("fprintf(f, \"%s\", content);")
        self.emit("fclose(f);")
        self.emit("return true;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool FILECLS_Append(const char* path, const char* content) {")
        self.indent()
        self.emit("FILE* f = fopen(path, \"a\");")
        self.emit("if (!f) return false;")
        self.emit("fprintf(f, \"%s\", content);")
        self.emit("fclose(f);")
        self.emit("return true;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool FILECLS_Exists(const char* path) {")
        self.indent()
        self.emit("FILE* f = fopen(path, \"r\");")
        self.emit("if (f) {")
        self.indent()
        self.emit("fclose(f);")
        self.emit("return true;")
        self.dedent()
        self.emit("}")
        self.emit("return false;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool FILECLS_Delete(const char* path) {")
        self.indent()
        self.emit("return remove(path) == 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # ===== ISA CHECKING =====
        self.emit("// Helper for 'isa' type checking (supports multiple inheritance)")
        self.emit("int _isa_check(const char* obj_class, const char* p0, const char* p1, const char* p2, const char* p3, const char* target_class) {")
        self.indent()
        self.emit("if (strcmp(obj_class, target_class) == 0) return 1;")
        self.emit("if (p0 && strcmp(p0, target_class) == 0) return 1;")
        self.emit("if (p1 && strcmp(p1, target_class) == 0) return 1;")
        self.emit("if (p2 && strcmp(p2, target_class) == 0) return 1;")
        self.emit("if (p3 && strcmp(p3, target_class) == 0) return 1;")
        self.emit("return 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
    
    def generate_array_helpers(self):
        self.emit("// Array helper structures")
        self.emit("struct IntArray_s {")
        self.indent()
        self.emit("int* data;")
        self.emit("int length;")
        self.emit("int capacity;")
        self.dedent()
        self.emit("};")
        self.emit("")
        
        self.emit("IntArray* IntArray_new(int capacity) {")
        self.indent()
        self.emit("IntArray* arr = GC_MALLOC(sizeof(IntArray));")
        self.emit("arr->data = GC_MALLOC(sizeof(int) * capacity);")
        self.emit("arr->length = 0;")
        self.emit("arr->capacity = capacity;")
        self.emit("return arr;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("IntArray* IntArray_from_literal(int* values, int length) {")
        self.indent()
        self.emit("IntArray* arr = IntArray_new(length);")
        self.emit("memcpy(arr->data, values, sizeof(int) * length);")
        self.emit("arr->length = length;")
        self.emit("return arr;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("void IntArray_append(IntArray* arr, int value) {")
        self.indent()
        self.emit("if (arr->length >= arr->capacity) {")
        self.indent()
        self.emit("arr->capacity *= 2;")
        self.emit("int* new_data = GC_MALLOC(sizeof(int) * arr->capacity);")
        self.emit("memcpy(new_data, arr->data, sizeof(int) * arr->length);")
        self.emit("arr->data = new_data;")
        self.dedent()
        self.emit("}")
        self.emit("arr->data[arr->length++] = value;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Map function
        self.emit("IntArray* IntArray_map(IntArray* arr, int (*func)(int)) {")
        self.indent()
        self.emit("IntArray* result = IntArray_new(arr->length);")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("IntArray_append(result, func(arr->data[i]));")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Filter function
        self.emit("IntArray* IntArray_filter(IntArray* arr, int (*func)(int)) {")
        self.indent()
        self.emit("IntArray* result = IntArray_new(arr->length);")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("if (func(arr->data[i])) {")
        self.indent()
        self.emit("IntArray_append(result, arr->data[i]);")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Reduce function
        self.emit("int IntArray_reduce(IntArray* arr, int (*func)(int, int), int initial) {")
        self.indent()
        self.emit("int result = initial;")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("result = func(result, arr->data[i]);")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Sort function (bubble sort for simplicity)
        self.emit("IntArray* IntArray_sort(IntArray* arr) {")
        self.indent()
        self.emit("IntArray* result = IntArray_new(arr->length);")
        self.emit("memcpy(result->data, arr->data, sizeof(int) * arr->length);")
        self.emit("result->length = arr->length;")
        self.emit("for (int i = 0; i < result->length - 1; i++) {")
        self.indent()
        self.emit("for (int j = 0; j < result->length - i - 1; j++) {")
        self.indent()
        self.emit("if (result->data[j] > result->data[j + 1]) {")
        self.indent()
        self.emit("int temp = result->data[j];")
        self.emit("result->data[j] = result->data[j + 1];")
        self.emit("result->data[j + 1] = temp;")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Unique function
        self.emit("IntArray* IntArray_unique(IntArray* arr) {")
        self.indent()
        self.emit("IntArray* result = IntArray_new(arr->length);")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("int found = 0;")
        self.emit("for (int j = 0; j < result->length; j++) {")
        self.indent()
        self.emit("if (result->data[j] == arr->data[i]) {")
        self.indent()
        self.emit("found = 1;")
        self.emit("break;")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.emit("if (!found) {")
        self.indent()
        self.emit("IntArray_append(result, arr->data[i]);")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Find function (returns first match or -1)
        self.emit("int IntArray_find(IntArray* arr, int (*func)(int)) {")
        self.indent()
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("if (func(arr->data[i])) {")
        self.indent()
        self.emit("return arr->data[i];")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.emit("return -1;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Helper to print IntArray
        self.emit("void IntArray_print(IntArray* arr) {")
        self.indent()
        self.emit("printf(\"[\");")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("printf(\"%d\", arr->data[i]);")
        self.emit("if (i < arr->length - 1) printf(\", \");")
        self.dedent()
        self.emit("}")
        self.emit("printf(\"]\\n\");")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Array concatenation helper
        self.emit("// Array concatenation")
        self.emit("IntArray* IntArray_concat(IntArray* arr1, IntArray* arr2) {")
        self.indent()
        self.emit("if (!arr1) return arr2;")
        self.emit("if (!arr2) return arr1;")
        self.emit("IntArray* result = IntArray_new(arr1->length + arr2->length);")
        self.emit("memcpy(result->data, arr1->data, sizeof(int) * arr1->length);")
        self.emit("memcpy(result->data + arr1->length, arr2->data, sizeof(int) * arr2->length);")
        self.emit("result->length = arr1->length + arr2->length;")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Add ARRAY class static methods here (after IntArray is defined)
        self.emit("// ARRAY class (static) - works with IntArray")
        self.emit("int ARRAY_Length(IntArray* arr) {")
        self.indent()
        self.emit("return arr ? arr->length : 0;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("bool ARRAY_Contains(IntArray* arr, int element) {")
        self.indent()
        self.emit("if (!arr) return false;")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("if (arr->data[i] == element) return true;")
        self.dedent()
        self.emit("}")
        self.emit("return false;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("int ARRAY_IndexOf(IntArray* arr, int element) {")
        self.indent()
        self.emit("if (!arr) return -1;")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("if (arr->data[i] == element) return i;")
        self.dedent()
        self.emit("}")
        self.emit("return -1;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # ==================== FLOAT ARRAY SUPPORT ====================
        self.emit("// FloatArray support (for float[] arrays)")
        self.emit("struct FloatArray_s {")
        self.indent()
        self.emit("float* data;")
        self.emit("int length;")
        self.emit("int capacity;")
        self.dedent()
        self.emit("};")
        self.emit("")
        
        self.emit("FloatArray* FloatArray_new(int capacity) {")
        self.indent()
        self.emit("FloatArray* arr = GC_MALLOC(sizeof(FloatArray));")
        self.emit("arr->data = GC_MALLOC(sizeof(float) * capacity);")
        self.emit("arr->length = 0;")
        self.emit("arr->capacity = capacity;")
        self.emit("return arr;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("FloatArray* FloatArray_from_literal(float* values, int length) {")
        self.indent()
        self.emit("FloatArray* arr = FloatArray_new(length);")
        self.emit("memcpy(arr->data, values, sizeof(float) * length);")
        self.emit("arr->length = length;")
        self.emit("return arr;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("FloatArray* FloatArray_map(FloatArray* arr, float (*func)(float)) {")
        self.indent()
        self.emit("FloatArray* result = FloatArray_new(arr->length);")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("result->data[result->length++] = func(arr->data[i]);")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("FloatArray* FloatArray_filter(FloatArray* arr, int (*func)(float)) {")
        self.indent()
        self.emit("FloatArray* result = FloatArray_new(arr->length);")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("if (func(arr->data[i])) {")
        self.indent()
        self.emit("result->data[result->length++] = arr->data[i];")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("float FloatArray_reduce(FloatArray* arr, float (*func)(float, float), float initial) {")
        self.indent()
        self.emit("float result = initial;")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("result = func(result, arr->data[i]);")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("FloatArray* FloatArray_sort(FloatArray* arr) {")
        self.indent()
        self.emit("FloatArray* result = FloatArray_new(arr->length);")
        self.emit("memcpy(result->data, arr->data, sizeof(float) * arr->length);")
        self.emit("result->length = arr->length;")
        self.emit("for (int i = 0; i < result->length - 1; i++) {")
        self.indent()
        self.emit("for (int j = 0; j < result->length - i - 1; j++) {")
        self.indent()
        self.emit("if (result->data[j] > result->data[j + 1]) {")
        self.indent()
        self.emit("float temp = result->data[j];")
        self.emit("result->data[j] = result->data[j + 1];")
        self.emit("result->data[j + 1] = temp;")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("FloatArray* FloatArray_unique(FloatArray* arr) {")
        self.indent()
        self.emit("FloatArray* result = FloatArray_new(arr->length);")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("int found = 0;")
        self.emit("for (int j = 0; j < result->length; j++) {")
        self.indent()
        self.emit("if (result->data[j] == arr->data[i]) {")
        self.indent()
        self.emit("found = 1;")
        self.emit("break;")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.emit("if (!found) {")
        self.indent()
        self.emit("result->data[result->length++] = arr->data[i];")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("float FloatArray_find(FloatArray* arr, int (*func)(float)) {")
        self.indent()
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("if (func(arr->data[i])) {")
        self.indent()
        self.emit("return arr->data[i];")
        self.dedent()
        self.emit("}")
        self.dedent()
        self.emit("}")
        self.emit("return 0.0f;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("void FloatArray_print(FloatArray* arr) {")
        self.indent()
        self.emit("printf(\"[\");")
        self.emit("for (int i = 0; i < arr->length; i++) {")
        self.indent()
        self.emit("printf(\"%f\", arr->data[i]);")
        self.emit("if (i < arr->length - 1) printf(\", \");")
        self.dedent()
        self.emit("}")
        self.emit("printf(\"]\\n\");")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        self.emit("FloatArray* FloatArray_concat(FloatArray* arr1, FloatArray* arr2) {")
        self.indent()
        self.emit("if (!arr1) return arr2;")
        self.emit("if (!arr2) return arr1;")
        self.emit("FloatArray* result = FloatArray_new(arr1->length + arr2->length);")
        self.emit("memcpy(result->data, arr1->data, sizeof(float) * arr1->length);")
        self.emit("memcpy(result->data + arr1->length, arr2->data, sizeof(float) * arr2->length);")
        self.emit("result->length = arr1->length + arr2->length;")
        self.emit("return result;")
        self.dedent()
        self.emit("}")
        self.emit("")
        
        # Note: Similar implementations would be added for BoolArray, LongFloatArray,
        # LongIntArray, CharArray, StringArray, and ObjectArray
        # The pattern is identical, just with different types
    
    def generate_method_forward_decl(self, method: MethodDecl):
        return_type = "bool" if method.return_type is None else self.c_type(method.return_type)
        params = ', '.join([f"{self.c_type(p.param_type)} {p.name}" for p in method.parameters])
        if not params:
            params = "void"
        self.emit(f"{return_type} {method.name}({params});")
    
    def generate_class(self, cls: ClassDecl):
        self.emit(f"// Class {cls.name}")
        if cls.parent_classes:
            self.emit(f"// Inherits from: {', '.join(cls.parent_classes)}")
        
        self.emit(f"typedef struct {cls.name}_s {{")
        self.indent()
        
        # Add parent class fields first (for multiple inheritance)
        # We inline parent fields so they're accessible directly
        for parent_name in cls.parent_classes:
            if parent_name in self.classes:
                parent_cls = self.classes[parent_name]
                self.emit(f"// Fields from parent {parent_name}")
                # Recursively include grandparent fields
                for grandparent in parent_cls.parent_classes:
                    if grandparent in self.classes:
                        gp_cls = self.classes[grandparent]
                        for member in gp_cls.members:
                            if isinstance(member, FieldDecl):
                                self.emit(f"{self.c_type(member.field_type)} {member.name};")
                # Include parent's own fields
                for member in parent_cls.members:
                    if isinstance(member, FieldDecl):
                        self.emit(f"{self.c_type(member.field_type)} {member.name};")
        
        # Add this class's fields
        for member in cls.members:
            if isinstance(member, FieldDecl):
                self.emit(f"{self.c_type(member.field_type)} {member.name};")
        
        # Add type information for runtime type checking
        self.emit("const char* _class_name;")
        if cls.parent_classes:
            # Store all parent class names (up to 4 for simplicity)
            for i in range(min(len(cls.parent_classes), 4)):
                self.emit(f"const char* _parent_class_{i};")
        
        self.dedent()
        self.emit(f"}} {cls.name};")
        self.emit("")
        
        # Generate constructor (Initialize method or default)
        self.generate_class_constructor(cls)
        
        # Generate methods
        self.current_class = cls.name
        for member in cls.members:
            if isinstance(member, MethodDecl):
                # Generate all methods including Initialize
                self.generate_class_method(cls.name, member)
        
        # Generate inherited methods (wrappers that call parent methods)
        for parent_name in cls.parent_classes:
            if parent_name in self.classes:
                parent_cls = self.classes[parent_name]
                # For each parent method, check if this class overrides it
                for parent_member in parent_cls.members:
                    if isinstance(parent_member, MethodDecl):
                        # Check if this class already defines this method
                        overridden = False
                        for member in cls.members:
                            if isinstance(member, MethodDecl) and member.name == parent_member.name:
                                overridden = True
                                break
                        
                        # If not overridden, generate a wrapper
                        if not overridden and parent_member.name != "Initialize":
                            self.generate_inherited_method_wrapper(cls.name, parent_name, parent_member)
        
        self.current_class = None
    
    def generate_class_constructor(self, cls: ClassDecl):
        """Generate constructor function(s) for a class - one per Initialize overload"""
        # Find ALL Initialize methods
        init_methods = []
        for member in cls.members:
            if isinstance(member, MethodDecl) and member.name == "Initialize":
                init_methods.append(member)
        
        # Generate one constructor per Initialize overload
        if init_methods:
            for init_method in init_methods:
                params = ', '.join([f"{self.c_type(p.param_type)} {p.name}" for p in init_method.parameters])
                mangled_name = self.mangle_method_name(cls.name, "new", init_method.parameters)
                
                if params:
                    self.emit(f"{cls.name}* {mangled_name}({params}) {{")
                else:
                    self.emit(f"{cls.name}* {mangled_name}(void) {{")
                self.indent()
                
                self.emit(f"{cls.name}* obj = GC_MALLOC(sizeof({cls.name}));")
                self.emit(f"obj->_class_name = \"{cls.name}\";")
                if cls.parent_classes:
                    for i, parent in enumerate(cls.parent_classes[:4]):  # Support up to 4 parents
                        self.emit(f"obj->_parent_class_{i} = \"{parent}\";")
                
                # Initialize parent fields if any
                for parent_name in cls.parent_classes:
                    if parent_name in self.classes:
                        parent_cls = self.classes[parent_name]
                        for member in parent_cls.members:
                            if isinstance(member, FieldDecl) and member.initial_value:
                                init_val = self.generate_expression(member.initial_value)
                                self.emit(f"obj->{member.name} = {init_val};")
                
                # Initialize fields with default values
                for member in cls.members:
                    if isinstance(member, FieldDecl) and member.initial_value:
                        init_val = self.generate_expression(member.initial_value)
                        self.emit(f"obj->{member.name} = {init_val};")
                
                # Call Initialize method
                mangled_init = self.mangle_method_name(cls.name, "Initialize", init_method.parameters)
                args = ', '.join(['obj'] + [p.name for p in init_method.parameters])
                self.emit(f"{mangled_init}({args});")
                
                self.emit("return obj;")
                self.dedent()
                self.emit("}")
                self.emit("")
        else:
            # Generate default constructor (no Initialize method)
            self.emit(f"{cls.name}* {cls.name}_new_void(void) {{")
            self.indent()
            
            self.emit(f"{cls.name}* obj = GC_MALLOC(sizeof({cls.name}));")
            self.emit(f"obj->_class_name = \"{cls.name}\";")
            if cls.parent_classes:
                for i, parent in enumerate(cls.parent_classes[:4]):
                    self.emit(f"obj->_parent_class_{i} = \"{parent}\";")
            
            # Initialize parent fields if any
            for parent_name in cls.parent_classes:
                if parent_name in self.classes:
                    parent_cls = self.classes[parent_name]
                    for member in parent_cls.members:
                        if isinstance(member, FieldDecl) and member.initial_value:
                            init_val = self.generate_expression(member.initial_value)
                            self.emit(f"obj->{member.name} = {init_val};")
            
            # Initialize fields with default values
            for member in cls.members:
                if isinstance(member, FieldDecl) and member.initial_value:
                    init_val = self.generate_expression(member.initial_value)
                    self.emit(f"obj->{member.name} = {init_val};")
            
            self.emit("return obj;")
            self.dedent()
            self.emit("}")
            self.emit("")
    
    def generate_inherited_method_wrapper(self, class_name: str, parent_name: str, method: MethodDecl):
        """Generate a wrapper method that delegates to the parent class method"""
        return_type = self.c_type(method.return_type) if method.return_type else "void"
        params = [f"{class_name}* thisclass"] + [f"{self.c_type(p.param_type)} {p.name}" for p in method.parameters]
        params_str = ', '.join(params)
        
        mangled_name = self.mangle_method_name(class_name, method.name, method.parameters)
        self.emit(f"{return_type} {mangled_name}({params_str}) {{")
        self.indent()
        
        # Cast thisclass to parent type and call parent method
        parent_mangled = self.mangle_method_name(parent_name, method.name, method.parameters)
        param_names = ', '.join([p.name for p in method.parameters])
        if param_names:
            if return_type != "void":
                self.emit(f"return {parent_mangled}(({parent_name}*)thisclass, {param_names});")
            else:
                self.emit(f"{parent_mangled}(({parent_name}*)thisclass, {param_names});")
        else:
            if return_type != "void":
                self.emit(f"return {parent_mangled}(({parent_name}*)thisclass);")
            else:
                self.emit(f"{parent_mangled}(({parent_name}*)thisclass);")
        
        self.dedent()
        self.emit("}")
        self.emit("")
    
    def generate_class_method(self, class_name: str, method: MethodDecl):
        return_type = self.c_type(method.return_type) if method.return_type else "void"
        params = [f"{class_name}* thisclass"] + [f"{self.c_type(p.param_type)} {p.name}" for p in method.parameters]
        params_str = ', '.join(params)
        
        mangled_name = self.mangle_method_name(class_name, method.name, method.parameters)
        self.emit(f"{return_type} {mangled_name}({params_str}) {{")
        self.indent()
        
        # Set current class and method context
        self.current_class = class_name
        self.current_method = method.name
        
        # Push new scope and add thisclass + parameters to symbol table
        self.push_scope()
        self.add_symbol("thisclass", class_name)
        for param in method.parameters:
            # Include [] suffix for array types
            type_name = param.param_type.name
            if param.param_type.is_array:
                type_name = type_name + "[]"
            self.add_symbol(param.name, type_name)
        
        # Collect lambdas for this method
        self.collect_lambdas_from_block(method.body)
        
        self.generate_block(method.body)
        
        self.pop_scope()
        self.current_class = None
        self.current_method = None
        
        self.dedent()
        self.emit("}")
        self.emit("")
    
    def generate_enum(self, enum: EnumDecl):
        self.emit(f"// Enum {enum.name}")
        self.emit(f"typedef enum {{")
        self.indent()
        for i, value in enumerate(enum.values):
            comma = "," if i < len(enum.values) - 1 else ""
            self.emit(f"{enum.name}_{value}{comma}")
        self.dedent()
        self.emit(f"}} {enum.name};")
        self.emit("")
    
    def generate_method(self, method: MethodDecl):
        return_type = self.c_type(method.return_type) if method.return_type else "void"
        params = ', '.join([f"{self.c_type(p.param_type)} {p.name}" for p in method.parameters])
        if not params:
            params = "void"
        
        self.emit(f"{return_type} {method.name}({params}) {{")
        self.indent()
        
        # Push new scope and add parameters to symbol table
        self.push_scope()
        for param in method.parameters:
            # Include [] suffix for array types
            type_name = param.param_type.name
            if param.param_type.is_array:
                type_name = type_name + "[]"
            self.add_symbol(param.name, type_name)
        
        # NOW collect lambdas for this method (symbols are available)
        self.collect_lambdas_from_block(method.body)
        
        self.generate_block(method.body)
        
        self.pop_scope()
        self.dedent()
        self.emit("}")
        self.emit("")
    
    def generate_main(self, method: MethodDecl):
        self.emit("int main(void) {")
        self.indent()
        self.emit("GC_INIT();")
        self.emit("bool result = Main_internal();")
        self.emit("return result ? 0 : 1;")
        self.dedent()
        self.emit("}")
        self.emit("")
        self.emit("bool Main_internal(void) {")
        self.indent()
        
        # Push scope for Main
        self.push_scope()
        
        # Collect lambdas for Main
        self.collect_lambdas_from_block(method.body)
        
        self.generate_block(method.body)
        self.pop_scope()
        
        self.dedent()
        self.emit("}")
    
    def generate_block(self, block: Block):
        for stmt in block.statements:
            self.generate_statement(stmt)
    
    def generate_statement(self, stmt: Statement):
        if isinstance(stmt, VarDecl):
            # Track the variable type
            type_name = stmt.var_type.name
            # For array types, append [] to the type name for symbol table
            if stmt.var_type.is_array:
                type_name = type_name + "[]"
            self.add_symbol(stmt.name, type_name)
            
            c_type = self.c_type(stmt.var_type)
            
            # Special handling for array types - use appropriate array type
            if stmt.var_type.is_array:
                array_type_name = self.get_array_type_name(stmt.var_type.name)
                c_type = f"{array_type_name}*"
            # Handle class types
            elif stmt.var_type.name in self.classes:
                c_type = f"{stmt.var_type.name}*"
            
            if stmt.initial_value:
                # For array literals, we need to pass the expected type context
                if stmt.var_type.is_array and isinstance(stmt.initial_value, ArrayLiteral):
                    # Generate array literal with type context
                    if not stmt.initial_value.elements:
                        # Empty array - use the declared type
                        array_type_name = self.get_array_type_name(stmt.var_type.name)
                        c_elem_type = self.get_c_element_type(stmt.var_type.name)
                        init_expr = f"{array_type_name}_from_literal(({c_elem_type}[]){{}}, 0)"
                    else:
                        init_expr = self.generate_expression(stmt.initial_value)
                else:
                    init_expr = self.generate_expression(stmt.initial_value)
                self.emit(f"{c_type} {stmt.name} = {init_expr};")
            else:
                self.emit(f"{c_type} {stmt.name};")
        
        elif isinstance(stmt, ExpressionStmt):
            expr = self.generate_expression(stmt.expression)
            self.emit(f"{expr};")
        
        elif isinstance(stmt, ReturnStmt):
            if stmt.value:
                value_expr = self.generate_expression(stmt.value)
                self.emit(f"return {value_expr};")
            else:
                self.emit("return;")
        
        elif isinstance(stmt, IfStmt):
            condition = self.generate_expression(stmt.condition)
            self.emit(f"if ({condition}) {{")
            self.indent()
            self.push_scope()
            self.generate_block(stmt.then_block)
            self.pop_scope()
            self.dedent()
            self.emit("}")
            
            for elseif_cond, elseif_block in stmt.elseif_parts:
                elseif_cond_expr = self.generate_expression(elseif_cond)
                self.emit(f"else if ({elseif_cond_expr}) {{")
                self.indent()
                self.push_scope()
                self.generate_block(elseif_block)
                self.pop_scope()
                self.dedent()
                self.emit("}")
            
            if stmt.else_block:
                self.emit("else {")
                self.indent()
                self.push_scope()
                self.generate_block(stmt.else_block)
                self.pop_scope()
                self.dedent()
                self.emit("}")
        
        elif isinstance(stmt, LoopForStmt):
            count_expr = self.generate_expression(stmt.count)
            loop_var = f"_loop_{self.temp_var_counter}"
            self.temp_var_counter += 1
            self.emit(f"for (int {loop_var} = 0; {loop_var} < {count_expr}; {loop_var}++) {{")
            self.indent()
            self.push_scope()
            self.generate_block(stmt.body)
            self.pop_scope()
            self.dedent()
            self.emit("}")
        
        elif isinstance(stmt, LoopUntilStmt):
            condition = self.generate_expression(stmt.condition)
            self.emit(f"while (!({condition})) {{")
            self.indent()
            self.push_scope()
            self.generate_block(stmt.body)
            self.pop_scope()
            self.dedent()
            self.emit("}")
    
    def generate_expression(self, expr: Expression) -> str:
        if isinstance(expr, Literal):
            if isinstance(expr.value, bool):
                return "true" if expr.value else "false"
            elif isinstance(expr.value, str):
                # Escape the string
                escaped = expr.value.replace('\\', '\\\\').replace('"', '\\"')
                return f'"{escaped}"'
            else:
                return str(expr.value)
        
        elif isinstance(expr, Identifier):
            return expr.name
        
        elif isinstance(expr, BinaryOp):
            left = self.generate_expression(expr.left)
            right = self.generate_expression(expr.right)
            
            # Infer types to handle string operations specially
            left_type = self.infer_expression_type(expr.left)
            right_type = self.infer_expression_type(expr.right)
            
            # Special handling for string operations
            if left_type == 'string' or right_type == 'string':
                if expr.operator == '==':
                    return f"string_equals({left}, {right})"
                elif expr.operator == '+':
                    return f"string_concat({left}, {right})"
                elif expr.operator == '<':
                    return f"string_less_than({left}, {right})"
                elif expr.operator == '>':
                    return f"string_greater_than({left}, {right})"
                elif expr.operator == '<=':
                    return f"(!string_greater_than({left}, {right}))"
                elif expr.operator == '>=':
                    return f"(!string_less_than({left}, {right}))"
            
            # Special handling for array concatenation
            if (left_type and '[]' in left_type) or (right_type and '[]' in right_type):
                if expr.operator == '+':
                    # Get the base type for the array
                    base_type = (left_type or right_type).replace('[]', '')
                    array_type_name = self.get_array_type_name(base_type)
                    return f"{array_type_name}_concat({left}, {right})"
            
            op_map = {
                '+': '+',
                '-': '-',
                '*': '*',
                '/': '/',
                '%': '%',
                '^': 'pow',  # Will need to handle this specially
                '==': '==',
                '>': '>',
                '<': '<',
                '>=': '>=',
                '<=': '<=',
                '&': '&&',
                'V': '||',
                'VV': '^'  # Bitwise XOR in C
            }
            
            if expr.operator == '^':
                return f"pow({left}, {right})"
            
            c_op = op_map.get(expr.operator, expr.operator)
            return f"({left} {c_op} {right})"
        
        elif isinstance(expr, UnaryOp):
            operand = self.generate_expression(expr.operand)
            
            if expr.operator == 'not':
                return f"(!{operand})"
            elif expr.operator == '++':
                return f"++{operand}" if expr.is_prefix else f"{operand}++"
            elif expr.operator == '--':
                return f"--{operand}" if expr.is_prefix else f"{operand}--"
        
        elif isinstance(expr, Assignment):
            target = self.generate_expression(expr.target)
            value = self.generate_expression(expr.value)
            return f"{target} = {value}"
        
        elif isinstance(expr, ArrayLiteral):
            # Generate array initialization - infer type from elements
            if not expr.elements:
                # Empty array - default to IntArray
                return f"IntArray_from_literal((int[]){{}}, 0)"
            
            # Infer type from first element
            first_elem_type = self.infer_expression_type(expr.elements[0])
            if not first_elem_type:
                first_elem_type = "integer"  # Default fallback
            
            # Get the appropriate array type and C element type
            array_type_name = self.get_array_type_name(first_elem_type)
            c_elem_type = self.get_c_element_type(first_elem_type)
            
            elements = ', '.join([self.generate_expression(e) for e in expr.elements])
            count = len(expr.elements)
            
            return f"{array_type_name}_from_literal(({c_elem_type}[]){{{elements}}}, {count})"
        
        elif isinstance(expr, ArrayAccess):
            array = self.generate_expression(expr.array)
            index = self.generate_expression(expr.index)
            return f"{array}->data[{index}]"
        
        elif isinstance(expr, MethodCall):
            # Special handling for static library classes
            if isinstance(expr.object, Identifier):
                static_classes = ["CONSOLE", "MATH", "STRING", "ARRAY", "DATETIME", "RANDOM", "FILE"]
                if expr.object.name in static_classes:
                    args = ', '.join([self.generate_expression(arg) for arg in expr.arguments])
                    
                    # CONSOLE methods need special Print overload handling
                    if expr.object.name == "CONSOLE":
                        # Determine which overload to use based on argument type
                        if expr.arguments and isinstance(expr.arguments[0], Literal):
                            arg_val = expr.arguments[0].value
                            if isinstance(arg_val, str):
                                return f"CONSOLE_Print({args})"
                            elif isinstance(arg_val, bool):
                                return f"CONSOLE_PrintBoolean({args})"
                            elif isinstance(arg_val, int):
                                return f"CONSOLE_PrintInteger({args})"
                        return f"CONSOLE_{expr.method_name}({args})"
                    
                    # FILE class maps to FILECLS to avoid C FILE conflict
                    elif expr.object.name == "FILE":
                        return f"FILECLS_{expr.method_name}({args})"
                    
                    # All other static classes (MATH, STRING, ARRAY, DATETIME, RANDOM)
                    else:
                        return f"{expr.object.name}_{expr.method_name}({args})"
            
            # Handle instance methods on primitive types (string methods, int.toString(), etc.)
            if expr.object:
                obj = self.generate_expression(expr.object)
                obj_type = self.infer_expression_type(expr.object)
                
                # String instance methods
                if obj_type == 'string':
                    if expr.method_name in ['length', 'substring', 'toUpper', 'toLower', 'replace', 'trim', 'toInteger', 'toFloat']:
                        args = ', '.join([self.generate_expression(arg) for arg in expr.arguments])
                        # Map toInteger to C function toInt
                        c_method_name = 'toInt' if expr.method_name == 'toInteger' else expr.method_name
                        if args:
                            return f"string_{c_method_name}({obj}, {args})"
                        else:
                            return f"string_{c_method_name}({obj})"
                
                # Integer instance methods
                if obj_type == 'integer':
                    if expr.method_name == 'toString':
                        return f"int_toString({obj})"
                    if expr.method_name == 'toFloat':
                        return f"int_toFloat({obj})"
                
                # Float instance methods
                if obj_type == 'float':
                    if expr.method_name == 'toString':
                        return f"float_toString({obj})"
                    if expr.method_name == 'toInteger':
                        return f"float_toInteger({obj})"
                
                # Check if it's a parent method call
                is_parent_call = isinstance(expr.object, Parent)
                
                # Special case: array.length property access
                if obj_type and '[]' in obj_type and expr.method_name == 'length':
                    return f"{obj}->length"
                
                # Special case: string.length property access
                if obj_type == 'string' and expr.method_name == 'length':
                    return f"STRING_Length({obj})"
                
                # Array transformation methods - work with all array types
                if obj_type and '[]' in obj_type and expr.method_name in ['map', 'filter', 'reduce', 'sort', 'unique', 'find', 'print']:
                    # Extract base type from array type (e.g., "integer[]" -> "integer")
                    base_type = obj_type.replace('[]', '')
                    array_type_name = self.get_array_type_name(base_type)
                    c_elem_type = self.get_c_element_type(base_type)
                    
                    # Get lambda function names for arguments
                    lambda_funcs = []
                    for i, arg in enumerate(expr.arguments):
                        if isinstance(arg, Lambda):
                            # Lambda should already be generated in collection pass
                            if hasattr(arg, '_generated_name'):
                                lambda_funcs.append(arg._generated_name)
                            else:
                                # Fallback: shouldn't happen but generate if needed
                                c_elem_type = self.get_c_element_type(base_type)
                                if expr.method_name == 'map':
                                    param_type = c_elem_type
                                    return_type = c_elem_type
                                elif expr.method_name == 'filter' or expr.method_name == 'find':
                                    param_type = c_elem_type
                                    return_type = "int"
                                elif expr.method_name == 'reduce' and i == 0:
                                    param_type = c_elem_type
                                    return_type = c_elem_type
                                else:
                                    param_type = "int"
                                    return_type = "int"
                                self.generate_lambda_definition(arg, param_type, return_type)
                                lambda_funcs.append(arg._generated_name)
                        else:
                            lambda_funcs.append(self.generate_expression(arg))
                    
                    if expr.method_name == 'map':
                        return f"{array_type_name}_map({obj}, {lambda_funcs[0]})"
                    elif expr.method_name == 'filter':
                        return f"{array_type_name}_filter({obj}, {lambda_funcs[0]})"
                    elif expr.method_name == 'reduce':
                        # Reduce needs initial value
                        if len(lambda_funcs) > 1:
                            return f"{array_type_name}_reduce({obj}, {lambda_funcs[0]}, {lambda_funcs[1]})"
                        else:
                            # Default initial value of 0
                            return f"{array_type_name}_reduce({obj}, {lambda_funcs[0]}, 0)"
                    elif expr.method_name == 'sort':
                        return f"{array_type_name}_sort({obj})"
                    elif expr.method_name == 'unique':
                        return f"{array_type_name}_unique({obj})"
                    elif expr.method_name == 'find':
                        return f"{array_type_name}_find({obj}, {lambda_funcs[0]})"
                    elif expr.method_name == 'print':
                        return f"{array_type_name}_print({obj})"
                
                # Handle parent method calls
                if is_parent_call:
                    # Get the parent class name
                    if self.current_class and self.current_class in self.classes:
                        cls = self.classes[self.current_class]
                        if cls.parent_classes:
                            parent_class = cls.parent_classes[0]  # Use first parent
                            # Cast thisclass to parent type
                            mangled_name = self.find_method_overload(parent_class, expr.method_name, expr.arguments)
                            args_list = [f"({parent_class}*)thisclass"] + [self.generate_expression(arg) for arg in expr.arguments]
                            args_str = ', '.join(args_list)
                            return f"{mangled_name}({args_str})"
                    # Fallback if we can't determine parent
                    return f"/* ERROR: Cannot resolve parent.{expr.method_name}() */"
                
                # Class instance method call
                # Use type inference to determine the class
                obj_type = self.infer_expression_type(expr.object)
                
                if obj_type and obj_type in self.classes:
                    # This is a class instance method call
                    mangled_name = self.find_method_overload(obj_type, expr.method_name, expr.arguments)
                    args_list = [obj] + [self.generate_expression(arg) for arg in expr.arguments]
                    args_str = ', '.join(args_list)
                    return f"{mangled_name}({args_str})"
                else:
                    # Unknown type or not a class - fall back to regular call
                    args = ', '.join([self.generate_expression(arg) for arg in expr.arguments])
                    return f"{obj}->{expr.method_name}({args})"
            else:
                # Standalone function call
                args = ', '.join([self.generate_expression(arg) for arg in expr.arguments])
                return f"{expr.method_name}({args})"
        
        elif isinstance(expr, MemberAccess):
            obj = self.generate_expression(expr.object)
            # Check if it's a class instance or array
            obj_type = self.infer_expression_type(expr.object)
            
            # Special case: string.length property
            if obj_type == 'string' and expr.member_name == 'length':
                return f"STRING_Length({obj})"
            
            # Special case: array.length property
            if obj_type and '[]' in obj_type and expr.member_name == 'length':
                return f"{obj}->length"
            
            if obj_type and (obj_type in self.classes or '[]' in obj_type):
                # Use -> for pointer member access (classes and arrays)
                return f"{obj}->{expr.member_name}"
            else:
                # Regular member access
                return f"{obj}.{expr.member_name}"
        
        elif isinstance(expr, Lambda):
            # Lambda should have been pre-generated in the collection pass
            if hasattr(expr, '_generated_name'):
                return expr._generated_name
            else:
                # Fallback: generate it now (shouldn't happen with proper collection)
                self.generate_lambda_definition(expr)
                return expr._generated_name
        
        elif isinstance(expr, NewInstance):
            # Generate call to constructor - find the right overload
            if expr.class_name in self.classes:
                # Create a fake parameter list to match against
                # We'll find the Initialize method with matching argument count
                cls = self.classes[expr.class_name]
                matching_init = None
                for member in cls.members:
                    if isinstance(member, MethodDecl) and member.name == "Initialize":
                        if len(member.parameters) == len(expr.arguments):
                            matching_init = member
                            break
                
                if matching_init:
                    mangled_name = self.mangle_method_name(expr.class_name, "new", matching_init.parameters)
                else:
                    # No Initialize method
                    mangled_name = f"{expr.class_name}_new_void"
            else:
                # Unknown class, use default
                mangled_name = f"{expr.class_name}_new"
            
            args = ', '.join([self.generate_expression(arg) for arg in expr.arguments])
            if args:
                return f"{mangled_name}({args})"
            else:
                return f"{mangled_name}()"
        
        elif isinstance(expr, ThisClass):
            # Reference to current instance
            return "thisclass"
        
        elif isinstance(expr, Parent):
            # For parent references in member access/method calls
            # Return the thisclass pointer - the method call will handle parent logic
            return "thisclass"
        
        elif isinstance(expr, IsA):
            # Type checking using helper function (supports multiple inheritance)
            obj_expr = self.generate_expression(expr.object)
            obj_type = self.infer_expression_type(expr.object)
            
            # Build parent class arguments
            parent_args = ["NULL", "NULL", "NULL", "NULL"]
            if obj_type and obj_type in self.classes:
                cls = self.classes[obj_type]
                for i in range(min(len(cls.parent_classes), 4)):
                    parent_args[i] = f"{obj_expr}->_parent_class_{i}"
            
            return f"_isa_check({obj_expr}->_class_name, {', '.join(parent_args)}, \"{expr.class_name}\")"
        
        return "/* UNIMPLEMENTED EXPRESSION */"

# Test the code generator
if __name__ == '__main__':
    from foobar_lexer import Lexer
    from foobar_parser import Parser
    
    test_code = '''
    Main() {
        integer x = 42;
        CONSOLE.Print("Hello, World!");
        
        if(x > 40) {
            CONSOLE.Print("x is greater than 40");
        }
        
        return true;
    }
    '''
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    codegen = CCodeGenerator()
    c_code = codegen.generate(ast)
    
    print(c_code)
