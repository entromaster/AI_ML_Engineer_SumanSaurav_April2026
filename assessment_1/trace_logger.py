"""
Trace Logger
Provides structured logging of agent steps, tool calls, and LLM interactions
for traceability and debugging.
"""

import os
import sys
import json
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Force UTF-8 on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

console = Console(force_terminal=True)


class TraceLogger:
    """Logs agent workflow traces to file and console."""
    
    def __init__(self, output_dir: str, log_filename: str = "trace.log"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.log_path = os.path.join(output_dir, log_filename)
        self.traces = []
        self.start_time = time.time()
        
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"MULTI-AGENT WAR ROOM TRACE LOG\n")
            f.write(f"Started: {datetime.now().isoformat()}\n")
            f.write(f"{'='*80}\n\n")
    
    def _write_to_file(self, message: str):
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(message + "\n")
    
    def _elapsed(self) -> str:
        return f"{time.time() - self.start_time:.2f}s"
    
    def log_step(self, agent_name: str, step: str, details: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": self._elapsed(),
            "type": "STEP",
            "agent": agent_name,
            "step": step,
            "details": details
        }
        self.traces.append(entry)
        msg = f"[{self._elapsed()}] [{agent_name}] STEP: {step}"
        if details:
            msg += f" | {details}"
        self._write_to_file(msg)
        console.print(f"  [dim]{self._elapsed()}[/dim] [bold cyan]{agent_name}[/bold cyan] -> {step}")
    
    def log_tool_call(self, agent_name: str, tool_name: str, args: dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": self._elapsed(),
            "type": "TOOL_CALL",
            "agent": agent_name,
            "tool": tool_name,
            "arguments": {k: str(v)[:200] for k, v in args.items()}
        }
        self.traces.append(entry)
        args_str = ", ".join(f"{k}={str(v)[:50]}" for k, v in args.items())
        msg = f"[{self._elapsed()}] [{agent_name}] TOOL_CALL: {tool_name}({args_str})"
        self._write_to_file(msg)
        console.print(f"  [TOOL] [dim]{self._elapsed()}[/dim] [yellow]{agent_name}[/yellow] calling tool: [bold]{tool_name}[/bold]")
    
    def log_tool_result(self, agent_name: str, tool_name: str, result: dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": self._elapsed(),
            "type": "TOOL_RESULT",
            "agent": agent_name,
            "tool": tool_name,
            "status": result.get("status", "completed")
        }
        self.traces.append(entry)
        status = result.get("status", "completed")
        elapsed = result.get("elapsed_seconds", "?")
        msg = f"[{self._elapsed()}] [{agent_name}] TOOL_RESULT: {tool_name} -> {status} ({elapsed}s)"
        self._write_to_file(msg)
        console.print(f"  [OK] [dim]{self._elapsed()}[/dim] [yellow]{agent_name}[/yellow] tool result: [green]{tool_name}[/green] ({status})")
    
    def log_llm_call(self, agent_name: str, prompt_preview: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": self._elapsed(),
            "type": "LLM_CALL",
            "agent": agent_name,
            "prompt_preview": prompt_preview[:300]
        }
        self.traces.append(entry)
        msg = f"[{self._elapsed()}] [{agent_name}] LLM_CALL: prompt_length={len(prompt_preview)} chars"
        self._write_to_file(msg)
        console.print(f"  [LLM] [dim]{self._elapsed()}[/dim] [magenta]{agent_name}[/magenta] calling Gemini LLM...")
    
    def log_llm_response(self, agent_name: str, response_preview: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": self._elapsed(),
            "type": "LLM_RESPONSE",
            "agent": agent_name,
            "response_preview": response_preview[:300]
        }
        self.traces.append(entry)
        msg = f"[{self._elapsed()}] [{agent_name}] LLM_RESPONSE: length={len(response_preview)} chars"
        self._write_to_file(msg + f"\n  Preview: {response_preview[:200]}")
        console.print(f"  [RESP] [dim]{self._elapsed()}[/dim] [magenta]{agent_name}[/magenta] received LLM response ({len(response_preview)} chars)")
    
    def log_error(self, agent_name: str, error: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": self._elapsed(),
            "type": "ERROR",
            "agent": agent_name,
            "error": error
        }
        self.traces.append(entry)
        msg = f"[{self._elapsed()}] [{agent_name}] ERROR: {error}"
        self._write_to_file(msg)
        console.print(f"  [ERR] [dim]{self._elapsed()}[/dim] [bold red]{agent_name}[/bold red] ERROR: {error}")
    
    def log_decision(self, decision: str, confidence: str, rationale: str):
        msg = f"\n{'='*80}\nFINAL DECISION: {decision}\nConfidence: {confidence}\nRationale: {rationale}\n{'='*80}"
        self._write_to_file(msg)
        console.print(Panel(
            f"[bold]{decision}[/bold]\nConfidence: {confidence}\n{rationale}",
            title="FINAL DECISION",
            border_style="green" if decision == "Proceed" else "yellow" if decision == "Pause" else "red"
        ))
    
    def finalize(self):
        elapsed = self._elapsed()
        summary = f"\n{'='*80}\nTRACE SUMMARY\n"
        summary += f"Total elapsed: {elapsed}\n"
        summary += f"Total trace entries: {len(self.traces)}\n"
        type_counts = {}
        for t in self.traces:
            type_counts[t["type"]] = type_counts.get(t["type"], 0) + 1
        for t, c in type_counts.items():
            summary += f"  {t}: {c}\n"
        summary += f"\nCompleted: {datetime.now().isoformat()}\n{'='*80}\n"
        self._write_to_file(summary)
        
        table = Table(title="Trace Summary")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="green")
        for t, c in type_counts.items():
            table.add_row(t, str(c))
        console.print(table)
        return self.log_path
