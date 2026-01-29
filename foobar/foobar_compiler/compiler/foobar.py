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

def compile_foobar(input_file: str, output_file: str = None, keep_c: bool = False, verbose: bool = False):
    """
    Compile a .foob file to an executable
    """
    # Read the source file
    try:
        with open(input_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
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
        # Lexical analysis
        if verbose:
            print("  [1/4] Lexical analysis...")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Parsing
        if verbose:
            print("  [2/4] Parsing...")
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Code generation
        if verbose:
            print("  [3/4] Generating C code...")
        codegen = CCodeGenerator()
        c_code = codegen.generate(ast)
        
        # Write C file
        with open(c_file, 'w') as f:
            f.write(c_code)
        
        # Compile with gcc
        if verbose:
            print("  [4/4] Compiling C code with gcc...")
        
        # Compile with gcc
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
