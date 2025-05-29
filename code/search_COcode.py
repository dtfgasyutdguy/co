# -*- coding: utf-8 -*-
"""This script is designed to analyze Python source code files and classify comments into two categories:
natural language comments and code-related comments. It provides functionality to process individual
Python files or entire directories containing Python files. The main features of the script include:
1. Parsing Python source code using the `ast` module to identify valid code structures.
2. Differentiating between natural language comments and comments that contain code-related content.
3. Handling both single-line comments (starting with `#`) and multi-line comments (enclosed in triple quotes).
4. Counting the total number of comment lines, natural language comment lines, and code-related comment lines.
5. Calculating the ratio of code-related comment lines to the total number of comment lines.
6. Supporting error handling for syntax errors, memory errors, and file processing errors.
The script is useful for analyzing the quality and purpose of comments in Python codebases, helping developers
understand the balance between documentation and inline code explanations.
"""
import os
import ast
import re

white = 0
def check_instance(node):
    """
    Check if the node is an instance of the specified types
    """
    if isinstance(node, (ast.FunctionDef,      # Function definition
        ast.ClassDef,         # Class definition
        ast.Assign,           # Assignment statement
        ast.Return,           # Return statement
        ast.If,               # If statement
        ast.While,            # While loop
        ast.For,              # For loop
        ast.Try,              # Try-except statement
        ast.Import,           # Import statement
        ast.Call,             # Function call
        ast.With,             # With statement
        ast.AsyncFunctionDef, # Async function definition
        ast.Await,            # Await expression
        ast.AsyncFor,         # Async for loop
        ast.AsyncWith,        # Async with statement
        ast.Raise,            # Raise statement
        ast.Assert,           # Assert statement
        ast.Delete,           # Delete statement
        ast.Global,           # Global statement
        ast.Nonlocal,         # Nonlocal statement
        ast.Pass,             # Pass statement
        ast.Break,            # Break statement
        ast.Continue,         # Continue statement
        ast.Lambda,           # Lambda expression
        ast.ListComp,         # List comprehension
        ast.SetComp,          # Set comprehension
        ast.DictComp,         # Dictionary comprehension
        ast.GeneratorExp,     # Generator expression
        ast.Yield,            # Yield expression
        ast.YieldFrom,        # Yield from expression
        ast.Attribute,        # Attribute access
        ast.Subscript,        # Subscript access
        ast.Starred,          # Starred expression
        ast.comprehension,    # Comprehension
        ast.ExceptHandler,    # Exception handler
        ast.withitem,         # With statement item
        ast.IfExp,            # If expression
        ast.ExceptHandler,    # Exception handler
        ast.ImportFrom)):     # Import from statement
        return True
    return False

def contains_valid_code(tree):
    """
    Check if the AST tree contains valid code structures
    :param tree: ast.AST, the return value of ast.parse(code)
    :return: True if it contains valid code structures, False if it only contains empty lines, strings, or numbers
    """
    # Traverse the AST tree
    for node in ast.walk(tree):
        # Skip empty modules
        if isinstance(node, (ast.Module, ast.Expr, ast.Name, ast.Load, ast.Constant, ast.Store, ast.AnnAssign)):
            continue
        
        # If it is another valid code structure, return True
        if check_instance(node):
            return True

    return False

def is_code_related_comment(code: str) -> bool:
    """
    Determine if the code string contains AST node types related to code (i.e., valid code).
    If there are no related code nodes (only comments, etc.), it is considered to have no code.
    """

    code = "# -*- coding: utf-8 -*- \n" + code
    
    try:
        # Parse the source code and generate an AST tree
        tree = ast.parse(code)
        
        if contains_valid_code(tree):
            return True  # Found nodes related to code, considered valid code
        
        # If no related code nodes are found, return False
        return False

    except SyntaxError:
        # If there is a syntax error in the code, it is also considered to have no valid code
        return False

def is_mult_code_related_comment(code: str) -> bool:
    """
    Determine if the code string contains AST node types related to code (i.e., valid code).
    If there are no related code nodes (only comments, etc.), it is considered to have no code.
    """
    codes = code
    global white
    code = "# -*- coding: utf-8 -*- \n" + code
    
    try:
        # Parse the source code and generate an AST tree
        try:
            tree = ast.parse(code)
        except MemoryError as e:
            print("MemoryError")
            return 'error'
        
        if contains_valid_code(tree):
            return 'all'  # Found nodes related to code, considered valid code
        
        # If no related code nodes are found, return False
        return 0

    except SyntaxError:
        # Check if there is code-related content in single lines of multi-line comments
        count = 0
        for line in codes.splitlines():
            line = line.strip()
            if line.startswith("#"):
                line = line[1:].strip()
            if line == '' or line.isspace():
                white += 1
                continue
            if is_code_related_comment(line):
                count += 1

        # If there is a syntax error in the code, it is also considered to have no valid code
        return count

def process_python_file(file_path):
    """
    Process a single Python file and count the number of comment lines
    """
    total_comment_lines = 0
    natural_language_comment_lines = 0
    code_related_comment_lines = 0
    comment_block = []
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        code = file.read()
        codes = code.splitlines()
        nums = 0
        for i, line in enumerate(codes):
            line = line.strip()
            if i == 0 and 'coding' in line:
                continue

            if line.startswith("#"):  # This line is a comment
                comment_text = line[2:]
                if comment_text == '' or comment_text.isspace():
                    continue
                total_comment_lines += 1
                comment_block.append(comment_text)
                nums += 1

            else:
                if comment_block:
                    if nums == 1:
                        sums = is_code_related_comment(comment_block[0])
                        if sums:
                            code_related_comment_lines +=1
                        else:
                            natural_language_comment_lines += 1
                        comment_block = []  # Reset comment block
                        nums = 0
                    else:
                        # If there are multiple lines of comments, concatenate these lines
                        full_comment_text = "\n".join(line for line in comment_block)
                        sums = is_mult_code_related_comment(full_comment_text)
                        global white
                        lens = nums - white
                        total_comment_lines -= white
                        white = 0
                        lens = nums
                        if sums == "error":
                            total_comment_lines -= lens
                        elif sums == "all":
                            code_related_comment_lines += lens
                        elif sums > 0:
                            code_related_comment_lines += sums
                            natural_language_comment_lines += lens - sums
                        else:
                            natural_language_comment_lines += lens
                        comment_block = []  # Reset comment block
                        nums = 0
                    
        # Process any remaining comment blocks at the end of the file
        if comment_block:
            if nums == 1:
                sums = is_code_related_comment(comment_block[0])
                if sums:
                    code_related_comment_lines +=1
                else:
                    natural_language_comment_lines += 1
            else:
                # If there are multiple lines of comments, concatenate these lines
                full_comment_text = "\n".join(line for line in comment_block)
                sums = is_mult_code_related_comment(full_comment_text)
                lens = nums - white
                total_comment_lines -= white
                white = 0
                if sums == "err":
                    total_comment_lines -= lens
                elif sums == "all":
                    code_related_comment_lines += lens
                    
                elif sums > 0:
                    code_related_comment_lines += sums
                    natural_language_comment_lines += lens - sums
                else:
                    natural_language_comment_lines += lens

        comment_block = []  # Reset comment block
        nums = 0
        
        multiline_comment_pattern = r"(\'\'\'|\"\"\")(.+?)\1"
        
        # Find all matching comments
        multiline_comments = re.findall(multiline_comment_pattern, code, re.DOTALL)
        multiline_comments = [comment[1] for comment in multiline_comments]

        if multiline_comments:
            for codes in multiline_comments:
                codes = codes.strip('"""').strip("'''")
                # Remove extra blank lines
                codes = codes.splitlines()
                codes = [line for line in codes if line != '' and not line.isspace()]
                codes = "\n".join(codes)
                lens = len(codes.splitlines())
                if lens == 0:
                    continue
                total_comment_lines += lens
                sums = is_mult_code_related_comment(codes)

                lens = lens - white
                total_comment_lines -= white
                white = 0
                if sums == "err":
                    total_comment_lines -= lens
                    continue
                elif sums == "all":
                    code_related_comment_lines += lens
                elif sums > 0:
                    code_related_comment_lines += sums
                    natural_language_comment_lines += lens - sums
                else:
                    natural_language_comment_lines += lens

    return total_comment_lines, natural_language_comment_lines, code_related_comment_lines


def process_directory(directory_path):
    """
    Process all Python files in the directory
    """
    lists = []
    count = 0
    total_comment_lines = 0
    natural_language_comment_lines = 0
    code_related_comment_lines = 0

    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            count += 1
            if file_path.endswith('.py'):
                try:
                    file_comment_lines, file_natural_comment_lines, file_code_related_comment_lines = process_python_file(file_path)
                    total_comment_lines += file_comment_lines
                    natural_language_comment_lines += file_natural_comment_lines
                    code_related_comment_lines += file_code_related_comment_lines
                    if file_code_related_comment_lines > 0:
                        lists.append(file_path)
                except OSError as e:
                    print(f"Error processing file: {file_path}", e)

    return total_comment_lines, natural_language_comment_lines, code_related_comment_lines

if __name__ == "__main__":
    directory_path = r'your path'  # Replace with your directory path
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")
        exit(1)
    
    total_comments, natural_comments, code_related_comments = process_directory(directory_path)

    print(f"Total comment lines: {total_comments}")
    print(f"Natural language comment lines: {natural_comments}")
    print(f"Code-related comment lines: {code_related_comments}")
    print(f"Code-related comment line ratio: {code_related_comments / total_comments:.10f}")
