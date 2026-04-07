"""
Test Runner Tool
Executes Python tests and scripts, captures output, and returns results.
"""

import os
import subprocess
import sys
import tempfile
from typing import Any


def run_test(test_path: str, working_dir: str = None, timeout: int = 30) -> dict:
    """
    Tool entry point: Run a pytest test file and capture results.
    
    Args:
        test_path: Path to the test file to run
        working_dir: Working directory for the test execution
        timeout: Maximum execution time in seconds
    """
    if not os.path.exists(test_path):
        return {
            "tool": "test_runner",
            "error": f"Test file not found: {test_path}",
            "status": "error"
        }
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path, "-v", "--tb=long", "--no-header"],
            capture_output=True,
            text=True,
            cwd=working_dir or os.path.dirname(test_path),
            timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        )
        
        # Parse test results
        output = result.stdout + result.stderr
        passed, failed, errors = _parse_pytest_output(output)
        
        return {
            "tool": "test_runner",
            "test_file": test_path,
            "status": "completed",
            "exit_code": result.returncode,
            "all_passed": result.returncode == 0,
            "summary": {
                "passed": passed,
                "failed": failed,
                "errors": errors
            },
            "stdout": result.stdout[-3000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else ""
        }
        
    except subprocess.TimeoutExpired:
        return {
            "tool": "test_runner",
            "test_file": test_path,
            "status": "timeout",
            "error": f"Test execution timed out after {timeout}s"
        }
    except Exception as e:
        return {
            "tool": "test_runner",
            "test_file": test_path,
            "status": "error",
            "error": str(e)
        }


def run_script(script_path: str, working_dir: str = None, timeout: int = 30) -> dict:
    """
    Run a Python script and capture its output.
    
    Args:
        script_path: Path to the Python script to run
        working_dir: Working directory for execution
        timeout: Maximum execution time in seconds
    """
    if not os.path.exists(script_path):
        return {
            "tool": "test_runner",
            "error": f"Script not found: {script_path}",
            "status": "error"
        }
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=working_dir or os.path.dirname(script_path),
            timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        )
        
        return {
            "tool": "test_runner",
            "script": script_path,
            "status": "completed",
            "exit_code": result.returncode,
            "success": result.returncode == 0,
            "stdout": result.stdout[-3000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else ""
        }
        
    except subprocess.TimeoutExpired:
        return {
            "tool": "test_runner",
            "script": script_path,
            "status": "timeout",
            "error": f"Script execution timed out after {timeout}s"
        }
    except Exception as e:
        return {
            "tool": "test_runner",
            "script": script_path,
            "status": "error",
            "error": str(e)
        }


def run_code_string(code: str, working_dir: str = None, timeout: int = 15) -> dict:
    """
    Execute a string of Python code and capture output.
    Used by agents to test hypotheses.
    """
    # Write code to a temporary file
    try:
        temp_dir = working_dir or tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "_agent_repro_test.py")
        
        with open(temp_path, 'w') as f:
            f.write(code)
        
        result = run_script(temp_path, working_dir, timeout)
        result["code_executed"] = code[:500]
        
        # Clean up
        try:
            os.remove(temp_path)
        except:
            pass
        
        return result
        
    except Exception as e:
        return {
            "tool": "test_runner",
            "status": "error",
            "error": f"Failed to execute code: {e}"
        }


def _parse_pytest_output(output: str) -> tuple:
    """Parse pytest output to extract pass/fail/error counts."""
    import re
    
    passed = 0
    failed = 0
    errors = 0
    
    # Look for summary line like "5 passed, 2 failed"
    summary_match = re.search(r'(\d+)\s+passed', output)
    if summary_match:
        passed = int(summary_match.group(1))
    
    fail_match = re.search(r'(\d+)\s+failed', output)
    if fail_match:
        failed = int(fail_match.group(1))
    
    error_match = re.search(r'(\d+)\s+error', output)
    if error_match:
        errors = int(error_match.group(1))
    
    return passed, failed, errors
