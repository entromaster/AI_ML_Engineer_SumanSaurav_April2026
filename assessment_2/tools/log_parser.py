"""
Log Parser Tool
Parses application logs, extracts stack traces, error signatures,
timestamps, and performs frequency analysis.
"""

import re
from collections import Counter
from typing import Any


def parse_logs(filepath: str) -> dict:
    """
    Tool entry point: Parse and analyze application logs.
    Extracts errors, warnings, stack traces, and patterns.
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    log_entries = []
    errors = []
    warnings = []
    stack_traces = []
    current_trace = []
    in_trace = False
    
    for i, line in enumerate(lines):
        line = line.rstrip()
        entry = _parse_log_line(line, i + 1)
        log_entries.append(entry)
        
        if entry["level"] == "ERROR":
            errors.append(entry)
            
            # Check for stack trace start
            if "Traceback" in line or "ASSERTION FAILED" in line:
                in_trace = True
                current_trace = [entry]
            elif in_trace:
                current_trace.append(entry)
                # Check for end of trace (assertion error or end pattern)
                if "Error:" in line or "Exception:" in line or ("assert" in line.lower() and "Error" in line):
                    stack_traces.append({
                        "lines": [t["raw"] for t in current_trace],
                        "start_line": current_trace[0]["line_number"],
                        "end_line": current_trace[-1]["line_number"],
                        "error_type": _extract_error_type(current_trace)
                    })
                    in_trace = False
                    current_trace = []
        elif entry["level"] == "WARNING":
            warnings.append(entry)
        else:
            if in_trace:
                current_trace.append(entry)
    
    # If trace was in progress, save it
    if current_trace:
        stack_traces.append({
            "lines": [t["raw"] for t in current_trace],
            "start_line": current_trace[0]["line_number"],
            "end_line": current_trace[-1]["line_number"],
            "error_type": _extract_error_type(current_trace)
        })
    
    # Frequency analysis
    error_types = Counter()
    for err in errors:
        key = _categorize_error(err["raw"])
        error_types[key] += 1
    
    return {
        "tool": "log_parser",
        "total_lines": len(lines),
        "summary": {
            "total_entries": len(log_entries),
            "errors": len(errors),
            "warnings": len(warnings),
            "info": sum(1 for e in log_entries if e["level"] == "INFO"),
            "debug": sum(1 for e in log_entries if e["level"] == "DEBUG")
        },
        "stack_traces": stack_traces,
        "error_entries": [{"line": e["line_number"], "raw": e["raw"]} for e in errors],
        "warning_entries": [{"line": w["line_number"], "raw": w["raw"]} for w in warnings],
        "error_frequency": dict(error_types),
        "key_findings": _extract_key_findings(errors, warnings, stack_traces)
    }


def _parse_log_line(line: str, line_number: int) -> dict:
    """Parse a single log line into structured format."""
    # Pattern: [timestamp] LEVEL component: message
    pattern = r'\[([^\]]+)\]\s+(ERROR|WARNING|INFO|DEBUG)\s+(\w+):\s*(.*)'
    match = re.match(pattern, line)
    
    if match:
        return {
            "line_number": line_number,
            "timestamp": match.group(1),
            "level": match.group(2),
            "component": match.group(3),
            "message": match.group(4),
            "raw": line
        }
    
    return {
        "line_number": line_number,
        "timestamp": None,
        "level": "UNKNOWN",
        "component": None,
        "message": line,
        "raw": line
    }


def _extract_error_type(trace_entries: list) -> str:
    """Extract the error type from a stack trace."""
    for entry in trace_entries:
        raw = entry.get("raw", "")
        if "AssertionError" in raw or "AssertionError" in raw:
            return "AssertionError"
        if "Error:" in raw:
            match = re.search(r'(\w+Error):', raw)
            if match:
                return match.group(1)
    return "Unknown"


def _categorize_error(line: str) -> str:
    """Categorize an error line into a type."""
    if "ASSERTION FAILED" in line or "assert" in line.lower():
        return "assertion_failure"
    if "Traceback" in line:
        return "traceback"
    if "Offset calculation" in line:
        return "offset_error"
    if "Expected" in line and "got" in line:
        return "unexpected_value"
    return "other_error"


def _extract_key_findings(errors: list, warnings: list, stack_traces: list) -> list:
    """Extract key findings from log analysis."""
    findings = []
    
    if stack_traces:
        findings.append({
            "finding": f"Found {len(stack_traces)} stack trace(s) in logs",
            "severity": "high",
            "details": [st["error_type"] for st in stack_traces]
        })
    
    # Look for pagination-related entries
    pagination_errors = [e for e in errors if "page" in e["raw"].lower() or "offset" in e["raw"].lower() or "item" in e["raw"].lower()]
    if pagination_errors:
        findings.append({
            "finding": f"Found {len(pagination_errors)} pagination-related errors",
            "severity": "high",
            "details": [e["raw"][:150] for e in pagination_errors]
        })
    
    # Look for duplicate/count mismatches
    count_errors = [e for e in errors if "Expected" in e["raw"] and "got" in e["raw"]]
    if count_errors:
        findings.append({
            "finding": f"Found {len(count_errors)} count mismatch errors",
            "severity": "high",
            "details": [e["raw"][:150] for e in count_errors]
        })
    
    # Red herrings to note
    noise_warnings = [w for w in warnings if any(kw in w["raw"].lower() for kw in ["cache", "webhook", "rate limit", "wal", "security"])]
    if noise_warnings:
        findings.append({
            "finding": f"Found {len(noise_warnings)} infrastructure warnings (likely not related to bug)",
            "severity": "low",
            "details": [w["raw"][:100] for w in noise_warnings[:3]]
        })
    
    return findings
