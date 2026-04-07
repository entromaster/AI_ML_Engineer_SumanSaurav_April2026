"""
Base Agent Class
Foundation for all agents in the multi-agent war room system.
"""

import json
import sys
import time
from rich.console import Console
from rich.panel import Panel

# Force UTF-8 on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

console = Console(force_terminal=True)


class BaseAgent:
    """Base class for all war room agents."""
    
    def __init__(self, name: str, role: str, persona: str, tools: dict, 
                 llm_client, logger):
        self.name = name
        self.role = role
        self.persona = persona
        self.tools = tools
        self.llm = llm_client
        self.logger = logger
    
    def call_tool(self, tool_name: str, **kwargs) -> dict:
        """Execute a registered tool and log the call."""
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
        """Send a prompt to the Gemini LLM with retry logic for rate limits."""
        full_prompt = self._build_prompt(prompt, context)
        self.logger.log_llm_call(self.name, full_prompt[:500] + "..." if len(full_prompt) > 500 else full_prompt)
        
        max_retries = 3
        retry_delays = [15, 30, 60]
        
        for attempt in range(max_retries + 1):
            try:
                response = self.llm.generate_content(full_prompt)
                result = response.text
                self.logger.log_llm_response(self.name, result[:500] + "..." if len(result) > 500 else result)
                return result
            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower()) and attempt < max_retries:
                    delay = retry_delays[attempt]
                    console.print(f"  [yellow]Rate limited. Waiting {delay}s before retry ({attempt+1}/{max_retries})...[/yellow]")
                    self.logger.log_step(self.name, f"Rate limited, retrying in {delay}s", f"Attempt {attempt+1}")
                    time.sleep(delay)
                else:
                    error_msg = f"LLM call failed: {error_str}"
                    self.logger.log_error(self.name, error_msg)
                    return error_msg
        
        return "LLM call failed after all retries"
    
    def _build_prompt(self, task_prompt: str, context: dict = None) -> str:
        """Build the full prompt with persona and context."""
        parts = [
            f"You are {self.name}, a {self.role} in a product launch war room.",
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
