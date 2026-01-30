#!/usr/bin/env python3
"""
FOOBAR Compiler
Transpiles .foob files to C and compiles them with gcc
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

from foobar_lexer import Lexer
from foobar_parser import Parser
from foobar_codegen import CCodeGenerator
from foobar_ast import Program, ImportDecl, ClassDecl, MethodDecl, EnumDecl

def resolve_import_path(current_file: str, import_path: str) -> str:
    """Resolve import path relative to current file"""
    current_dir = os.path.dirname(os.path.abspath(current_file))
    resolved = os.path.normpath(os.path.join(current_dir, import_path))
    
    # Add .foob extension if not present
    if not resolved.endswith('.foob'):
        resolved += '.foob'
    
    return resolved

def parse_file(filepath: str, verbose: bool = False) -> Program:
    """Parse a single FOOBAR file and return its AST"""
    if verbose:
        print(f"  Parsing {filepath}...")
    
    try:
        with open(filepath, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        raise ImportError(f"Cannot find file: {filepath}")
    except Exception as e:
        raise ImportError(f"Error reading file {filepath}: {e}")
    
    # Tokenize
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    
    # Parse
    parser = Parser(tokens)
    ast = parser.parse()
    
    return ast

def collect_imports(base_file: str, verbose: bool = False) -> dict:
    """
    Recursively collect all import files starting from base_file
    Returns a dict of {filepath: AST}
    """
    all_asts = {}
    to_process = [base_file]
    processed = set()
    
    while to_process:
        current_file = to_process.pop()
        
        if current_file in processed:
            continue
        
        processed.add(current_file)
        
        # Parse this file
        ast = parse_file(current_file, verbose)
        all_asts[current_file] = ast
        
        # Collect imports from this file
        for import_decl in ast.imports:
            import_path = resolve_import_path(current_file, import_decl.filepath)
            
            if not os.path.exists(import_path):
                raise ImportError(
                    f"Cannot find imported file: '{import_decl.filepath}'\n"
                    f"  Referenced in: {current_file}\n"
                    f"  Searched for: {import_path}"
                )
            
            if import_path not in processed:
                to_process.append(import_path)
    
    return all_asts

def check_circular_imports(all_asts: dict) -> None:
    """Detect circular import dependencies"""
    # Build dependency graph
    graph = {}
    for filepath, ast in all_asts.items():
        graph[filepath] = [
            resolve_import_path(filepath, imp.filepath) 
            for imp in ast.imports
        ]
    
    # DFS to detect cycles
    def has_cycle(node, visited, rec_stack, path):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack, path):
                    return True
            elif neighbor in rec_stack:
                # Found cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycle_str = "\n  -> ".join(cycle)
                raise ImportError(
                    f"Circular import detected:\n  -> {cycle_str}"
                )
        
        path.pop()
        rec_stack.remove(node)
        return False
    
    visited = set()
    for node in graph:
        if node not in visited:
            has_cycle(node, visited, set(), [])

def check_duplicate_names(all_declarations: list) -> None:
    """Check for duplicate class/enum/function names across files"""
    class_names = {}
    enum_names = {}
    function_names = {}
    
    for decl_info in all_declarations:
        decl, filepath = decl_info
        
        if isinstance(decl, ClassDecl):
            if decl.name in class_names:
                raise SyntaxError(
                    f"Duplicate class definition: '{decl.name}'\n"
                    f"  First defined in: {class_names[decl.name]}\n"
                    f"  Also defined in: {filepath}"
                )
            class_names[decl.name] = filepath
        
        elif isinstance(decl, EnumDecl):
            if decl.name in enum_names:
                raise SyntaxError(
                    f"Duplicate enumeration definition: '{decl.name}'\n"
                    f"  First defined in: {enum_names[decl.name]}\n"
                    f"  Also defined in: {filepath}"
                )
            enum_names[decl.name] = filepath
        
        elif isinstance(decl, MethodDecl):
            # Only check top-level functions (Main, etc.)
            if decl.name in function_names and decl.name != "Main":
                raise SyntaxError(
                    f"Duplicate function definition: '{decl.name}'\n"
                    f"  First defined in: {function_names[decl.name]}\n"
                    f"  Also defined in: {filepath}"
                )
            function_names[decl.name] = filepath

def combine_programs(all_asts: dict, main_file: str, verbose: bool = False) -> Program:
    """
    Combine multiple FOOBAR program ASTs into a single Program
    main_file is used to determine which file's Main() to use
    """
    combined_declarations = []
    all_decl_info = []  # For duplicate checking: (decl, filepath)
    main_found = False
    
    # Process main file first to ensure its Main() is used
    if main_file in all_asts:
        for decl in all_asts[main_file].declarations:
            combined_declarations.append(decl)
            all_decl_info.append((decl, main_file))
            if isinstance(decl, MethodDecl) and decl.name == "Main":
                main_found = True
    
    # Then process all other files
    for filepath, ast in all_asts.items():
        if filepath == main_file:
            continue  # Already processed
        
        for decl in ast.declarations:
            # Skip Main() from non-main files
            if isinstance(decl, MethodDecl) and decl.name == "Main":
                if verbose:
                    print(f"  Warning: Skipping Main() from {filepath} (using Main() from {main_file})")
                continue
            
            combined_declarations.append(decl)
            all_decl_info.append((decl, filepath))
    
    # Check for duplicates
    check_duplicate_names(all_decl_info)
    
    if not main_found:
        raise SyntaxError(f"No Main() function found in {main_file}")
    
    # Return combined program with no imports (already resolved)
    return Program(imports=[], declarations=combined_declarations)

def compile_foobar(input_file: str, output_file: str = None, keep_c: bool = False, verbose: bool = False):
    """
    Compile a .foob file to an executable
    Handles multi-file compilation with imports
    """
    # Normalize the input file path
    input_file = os.path.abspath(input_file)
    
    # Determine output file name
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.with_suffix(''))
    
    c_file = output_file + '.c'
    
    if verbose:
        print(f"Compiling {input_file}...")
        print(f"  C output: {c_file}")
        print(f"  Executable: {output_file}")
    
    try:
        # Collect all files (main + imports)
        if verbose:
            print("  [1/5] Collecting imports...")
        all_asts = collect_imports(input_file, verbose)
        
        if verbose and len(all_asts) > 1:
            print(f"  Found {len(all_asts)} file(s) to compile:")
            for filepath in all_asts.keys():
                print(f"    - {filepath}")
        
        # Check for circular imports
        if verbose:
            print("  [2/5] Checking for circular imports...")
        check_circular_imports(all_asts)
        
        # Combine all programs into one
        if verbose:
            print("  [3/5] Combining programs...")
        combined_ast = combine_programs(all_asts, input_file, verbose)
        
        # Code generation
        if verbose:
            print("  [4/5] Generating C code...")
        codegen = CCodeGenerator()
        c_code = codegen.generate(combined_ast)
        
        # Write C file
        with open(c_file, 'w') as f:
            f.write(c_code)
        
        # Compile with gcc
        if verbose:
            print("  [5/5] Compiling C code with gcc...")
        
        compile_cmd = [
            'gcc',
            '-o', output_file,
            c_file,
            '-lm',  # For math functions like pow()
            '-std=c99'
        ]
        
        if verbose:
            print(f"  Running: {' '.join(compile_cmd)}")
        
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error compiling C code:")
            print(result.stderr)
            return False
        
        # Clean up C file unless --keep-c
        if not keep_c:
            os.remove(c_file)
            if verbose:
                print(f"  Cleaned up {c_file}")
        
        if verbose:
            print(f"✓ Successfully compiled to {output_file}")
        else:
            print(f"✓ Successfully compiled to {output_file}")
        
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return False
    except Exception as e:
        print(f"Error during compilation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description='FOOBAR Compiler - Transpile .foob files to native executables',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  foobar compile program.foob              # Compile to 'program'
  foobar compile program.foob -o myapp     # Compile to 'myapp'
  foobar compile program.foob --keep-c     # Keep the generated C file
  foobar compile program.foob -v           # Verbose output
        '''
    )
    
    parser.add_argument('command', choices=['compile'], help='Command to execute')
    parser.add_argument('input', help='Input .foob file')
    parser.add_argument('-o', '--output', help='Output executable name')
    parser.add_argument('--keep-c', action='store_true', help='Keep the generated C file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.command == 'compile':
        success = compile_foobar(
            args.input,
            args.output,
            args.keep_c,
            args.verbose
        )
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
