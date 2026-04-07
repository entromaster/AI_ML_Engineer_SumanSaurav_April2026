"""
Code Analyzer Tool
Parses Python AST, finds function definitions, analyzes code structure,
and traces call chains for debugging.
"""

import ast
import os
from typing import Any


def analyze_file(filepath: str) -> dict:
    """
    Tool entry point: Analyze a Python source file's structure.
    Returns functions, classes, imports, and complexity information.
    """
    if not os.path.exists(filepath):
        return {"tool": "code_analyzer", "error": f"File not found: {filepath}"}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(_analyze_function(node, source))
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": node.end_lineno,
                    "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    "decorators": [_get_decorator_name(d) for d in node.decorator_list]
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(_analyze_import(node))
        
        return {
            "tool": "code_analyzer",
            "filepath": filepath,
            "total_lines": len(source.split('\n')),
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "complexity_indicators": _analyze_complexity(tree)
        }
        
    except SyntaxError as e:
        return {
            "tool": "code_analyzer",
            "filepath": filepath,
            "error": f"Syntax error: {e}",
            "line": e.lineno
        }
    except Exception as e:
        return {
            "tool": "code_analyzer",
            "filepath": filepath,
            "error": str(e)
        }


def find_function(filepath: str, function_name: str) -> dict:
    """
    Find a specific function in a file and return its source code.
    """
    if not os.path.exists(filepath):
        return {"tool": "code_analyzer", "error": f"File not found: {filepath}"}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        lines = source.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                func_lines = lines[node.lineno - 1:node.end_lineno]
                return {
                    "tool": "code_analyzer",
                    "found": True,
                    "filepath": filepath,
                    "function_name": function_name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                    "source_code": '\n'.join(func_lines),
                    "args": [arg.arg for arg in node.args.args],
                    "has_return": any(isinstance(n, ast.Return) for n in ast.walk(node)),
                    "calls_made": _get_function_calls(node)
                }
        
        return {
            "tool": "code_analyzer",
            "found": False,
            "filepath": filepath,
            "function_name": function_name,
            "error": f"Function '{function_name}' not found in {filepath}"
        }
        
    except Exception as e:
        return {"tool": "code_analyzer", "error": str(e)}


def trace_call_chain(directory: str, function_name: str) -> dict:
    """
    Trace where a function is called from across all Python files in a directory.
    """
    callers = []
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for fname in files:
            if not fname.endswith('.py'):
                continue
            
            filepath = os.path.join(root, fname)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                tree = ast.parse(source)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        call_name = _get_call_name(node)
                        if call_name and function_name in call_name:
                            callers.append({
                                "file": filepath,
                                "line": node.lineno,
                                "caller_function": _find_enclosing_function(tree, node.lineno)
                            })
            except Exception:
                continue
    
    return {
        "tool": "code_analyzer",
        "function": function_name,
        "directory": directory,
        "callers": callers,
        "total_call_sites": len(callers)
    }


def _analyze_function(node: ast.FunctionDef, source: str) -> dict:
    """Analyze a function definition."""
    lines = source.split('\n')
    func_source = '\n'.join(lines[node.lineno - 1:node.end_lineno])
    
    return {
        "name": node.name,
        "line": node.lineno,
        "end_line": node.end_lineno,
        "args": [arg.arg for arg in node.args.args],
        "has_docstring": (isinstance(node.body[0], ast.Expr) and 
                         isinstance(node.body[0].value, ast.Constant) and 
                         isinstance(node.body[0].value.value, str)) if node.body else False,
        "num_lines": node.end_lineno - node.lineno + 1,
        "calls_made": _get_function_calls(node),
        "has_conditionals": any(isinstance(n, (ast.If, ast.IfExp)) for n in ast.walk(node)),
        "has_loops": any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(node)),
        "source_code": func_source[:500]
    }


def _get_function_calls(node: ast.AST) -> list:
    """Get all function calls within a node."""
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = _get_call_name(child)
            if name:
                calls.append(name)
    return list(set(calls))


def _get_call_name(node: ast.Call) -> str:
    """Extract the name from a Call node."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    elif isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name):
            return f"{node.func.value.id}.{node.func.attr}"
        return node.func.attr
    return None


def _get_decorator_name(node: ast.AST) -> str:
    """Get decorator name from a decorator node."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return node.attr
    elif isinstance(node, ast.Call):
        return _get_call_name(node)
    return str(node)


def _analyze_import(node: ast.AST) -> dict:
    """Analyze an import statement."""
    if isinstance(node, ast.Import):
        return {"type": "import", "names": [a.name for a in node.names], "line": node.lineno}
    elif isinstance(node, ast.ImportFrom):
        return {"type": "from_import", "module": node.module, 
                "names": [a.name for a in node.names], "line": node.lineno}
    return {}


def _analyze_complexity(tree: ast.AST) -> dict:
    """Analyze code complexity indicators."""
    indicators = {
        "conditionals": sum(1 for _ in ast.walk(tree) if isinstance(_, (ast.If, ast.IfExp))),
        "loops": sum(1 for _ in ast.walk(tree) if isinstance(_, (ast.For, ast.While))),
        "try_except": sum(1 for _ in ast.walk(tree) if isinstance(_, ast.Try)),
        "function_defs": sum(1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef)),
        "class_defs": sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))
    }
    return indicators


def _find_enclosing_function(tree: ast.AST, line: int) -> str:
    """Find which function encloses a given line number."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.lineno <= line <= (node.end_lineno or float('inf')):
                return node.name
    return "<module>"
