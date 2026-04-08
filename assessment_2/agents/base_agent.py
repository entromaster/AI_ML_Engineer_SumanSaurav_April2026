"""
Base Agent Class for Assessment 2
Foundation for all agents in the bug report analysis system.
"""

import json
import sys
import time
from rich.console import Console
from rich.panel import Panel

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

console = Console(force_terminal=True)


class BaseAgent:
    """Base class for all bug analysis agents."""
    
    def __init__(self, name: str, role: str, persona: str, tools: dict,
                 llm_client, logger):
        self.name = name
        self.role = role
        self.persona = persona
        self.tools = tools
        self.llm = llm_client
        self.logger = logger
    
    def call_tool(self, tool_name: str, **kwargs):
        start_time = time.time()
        self.logger.log_tool_call(self.name, tool_name, kwargs)
        
        if tool_name not in self.tools:
            error = f"Tool '{tool_name}' not found. Available: {list(self.tools.keys())}"
            self.logger.log_tool_result(self.name, tool_name, {"error": error})
            return {"error": error}
        
        try:
            result = self.tools[tool_name](**kwargs)
            elapsed = round(time.time() - start_time, 2)
            self.logger.log_tool_result(self.name, tool_name,
                                        {"status": "success", "elapsed_seconds": elapsed})
            return result
        except Exception as e:
            error_result = {"error": str(e)}
            self.logger.log_tool_result(self.name, tool_name, error_result)
            return error_result
    
    def call_llm(self, prompt: str, context: dict = None) -> str:
        """Send a prompt to the Gemini LLM with a strict 10-second timeout."""
        import concurrent.futures
        full_prompt = self._build_prompt(prompt, context)
        self.logger.log_llm_call(self.name, full_prompt[:500] + "..." if len(full_prompt) > 500 else full_prompt)
        
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.llm.generate_content, full_prompt)
        try:
            response = future.result(timeout=10.0)
            result = response.text
            self.logger.log_llm_response(self.name, result[:500] + "..." if len(result) > 500 else result)
            return result
        except concurrent.futures.TimeoutError:
            error_msg = "LLM call timed out after 10 seconds."
            console.print(f"  [yellow]LLM Timeout: Moving to next agent.[/yellow]")
            self.logger.log_error(self.name, error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"LLM call failed: {str(e)}"
            console.print(f"  [red]LLM Error: {error_msg}. Moving to next agent.[/red]")
            self.logger.log_error(self.name, error_msg)
            return error_msg
    
    def _build_prompt(self, task_prompt: str, context: dict = None) -> str:
        parts = [
            f"You are {self.name}, a {self.role} in an automated bug analysis system.",
            f"Your persona: {self.persona}",
            "",
            "IMPORTANT: You must respond with valid JSON only. No markdown, no code fences, no extra text.",
            ""
        ]
        
        if context:
            parts.append("=== CONTEXT FROM PREVIOUS AGENTS AND TOOLS ===")
            for key, value in context.items():
                if isinstance(value, (dict, list)):
                    parts.append(f"\n--- {key} ---")
                    parts.append(json.dumps(value, indent=2)[:3000])
                else:
                    parts.append(f"\n--- {key} ---")
                    parts.append(str(value)[:3000])
            parts.append("\n=== END CONTEXT ===\n")
        
        parts.append(task_prompt)
        return "\n".join(parts)
    
    def run(self, context: dict) -> dict:
        raise NotImplementedError("Subclasses must implement run()")
    
    def display_status(self, message: str):
        console.print(Panel(
            f"[bold]{message}[/bold]",
            title=f"[AGENT] {self.name} ({self.role})",
            border_style="cyan"
        ))
