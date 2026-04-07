"""
File Searcher Tool
Searches through files and directories using pattern matching.
Simulates ripgrep-style search for code and log analysis.
"""

import os
import re
from typing import Any


def search_files(search_path: str, pattern: str, file_glob: str = "*.py", 
                 case_insensitive: bool = True, max_results: int = 50) -> dict:
    """
    Tool entry point: Search for a pattern in files under search_path.
    
    Args:
        search_path: Directory or file to search in
        pattern: Regex pattern to search for
        file_glob: File extension filter (e.g., "*.py", "*.txt")
        case_insensitive: Whether to do case-insensitive search
        max_results: Maximum number of matches to return
    """
    matches = []
    files_searched = 0
    files_with_matches = 0
    
    flags = re.IGNORECASE if case_insensitive else 0
    
    try:
        compiled_pattern = re.compile(pattern, flags)
    except re.error as e:
        return {"tool": "file_searcher", "error": f"Invalid regex pattern: {e}"}
    
    if os.path.isfile(search_path):
        # Search single file
        file_matches = _search_file(search_path, compiled_pattern)
        matches.extend(file_matches)
        files_searched = 1
        if file_matches:
            files_with_matches = 1
    else:
        # Search directory
        ext = file_glob.replace("*", "")
        for root, dirs, files in os.walk(search_path):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for fname in files:
                if ext and not fname.endswith(ext):
                    continue
                
                filepath = os.path.join(root, fname)
                files_searched += 1
                
                try:
                    file_matches = _search_file(filepath, compiled_pattern)
                    if file_matches:
                        files_with_matches += 1
                        matches.extend(file_matches)
                        
                        if len(matches) >= max_results:
                            break
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            if len(matches) >= max_results:
                break
    
    return {
        "tool": "file_searcher",
        "search_path": search_path,
        "pattern": pattern,
        "files_searched": files_searched,
        "files_with_matches": files_with_matches,
        "total_matches": len(matches),
        "matches": matches[:max_results]
    }


def _search_file(filepath: str, pattern: re.Pattern) -> list:
    """Search a single file for pattern matches."""
    matches = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if pattern.search(line):
                    matches.append({
                        "file": filepath,
                        "line_number": line_num,
                        "line_content": line.rstrip()[:300],
                        "context": _get_context(filepath, line_num)
                    })
    except Exception:
        pass
    
    return matches


def _get_context(filepath: str, line_num: int, context_lines: int = 2) -> list:
    """Get surrounding context lines for a match."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        
        return [
            {"line": i + 1, "content": lines[i].rstrip()[:200]}
            for i in range(start, end)
        ]
    except Exception:
        return []


def read_file_content(filepath: str) -> dict:
    """
    Read and return the full content of a file.
    Useful for agents to inspect specific source files.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        return {
            "tool": "file_searcher",
            "action": "read_file",
            "filepath": filepath,
            "total_lines": len(lines),
            "content": content,
            "size_bytes": len(content.encode('utf-8'))
        }
    except FileNotFoundError:
        return {"tool": "file_searcher", "error": f"File not found: {filepath}"}
    except Exception as e:
        return {"tool": "file_searcher", "error": f"Error reading file: {e}"}
