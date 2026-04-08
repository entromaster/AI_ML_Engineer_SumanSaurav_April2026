"""
Bug Analysis Orchestrator
Manages the multi-agent workflow for bug report analysis, reproduction,
and fix planning.
"""

import os
import sys
import json
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

from llm_wrapper import LLMWrapper

from agents.triage_agent import TriageAgent
from agents.log_analyst_agent import LogAnalystAgent
from agents.dependency_agent import DependencyAgent
from agents.reproduction_agent import ReproductionAgent
from agents.fix_planner_agent import FixPlannerAgent
from agents.reviewer_agent import ReviewerAgent
from tools.log_parser import parse_logs
from tools.file_searcher import search_files, read_file_content
from tools.test_runner import run_test, run_script, run_code_string
from tools.code_analyzer import analyze_file, find_function, trace_call_chain
from trace_logger import TraceLogger

console = Console(force_terminal=True)


class BugAnalysisOrchestrator:
    """
    Orchestrates the multi-agent bug analysis workflow.
    
    Workflow:
    1. Triage Agent → Parse bug report, extract symptoms, prioritize hypotheses
    2. Log Analyst → Analyze logs for evidence
    3. Dependency Analyst → Check for dependency issues
    4. Reproduction Agent → Generate and run minimal repro
    5. Fix Planner → Propose root cause and fix plan
    6. Reviewer/Critic → Challenge and validate
    7. Final Synthesis → Structured JSON output
    """
    
    def __init__(self, repo_path: str, inputs_dir: str, output_dir: str, provider: str, api_key: str):
        self.repo_path = repo_path
        self.inputs_dir = inputs_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure LLM Client
        self.llm = LLMWrapper(provider, api_key)
        
        # Initialize logger
        self.logger = TraceLogger(output_dir)
        
        # Register tools
        self.tools = {
            "parse_logs": parse_logs,
            "search_files": search_files,
            "read_file_content": read_file_content,
            "run_test": run_test,
            "run_script": run_script,
            "run_code_string": run_code_string,
            "analyze_file": analyze_file,
            "find_function": find_function,
            "trace_call_chain": trace_call_chain
        }
        
        # Shared context
        self.context = {
            "repo_path": repo_path,
            "bug_report_path": os.path.join(inputs_dir, "bug_report.md"),
            "logs_path": os.path.join(inputs_dir, "logs.txt"),
            "output_dir": output_dir
        }
        
        # Initialize agents
        self.agents = {
            "triage": TriageAgent(self.tools, self.llm, self.logger),
            "log_analyst": LogAnalystAgent(self.tools, self.llm, self.logger),
            "dependency": DependencyAgent(self.tools, self.llm, self.logger),
            "reproduction": ReproductionAgent(self.tools, self.llm, self.logger),
            "fix_planner": FixPlannerAgent(self.tools, self.llm, self.logger),
            "reviewer": ReviewerAgent(self.tools, self.llm, self.logger)
        }
        
        # Workflow order
        self.workflow = [
            ("triage", "Phase 1: Bug Triage & Hypothesis Generation"),
            ("log_analyst", "Phase 2: Log Analysis & Evidence Gathering"),
            ("dependency", "Phase 3: Dependency Analysis"),
            ("reproduction", "Phase 4: Minimal Reproduction"),
            ("fix_planner", "Phase 5: Root Cause Analysis & Fix Plan"),
            ("reviewer", "Phase 6: Review & Critique")
        ]
    
    def run(self) -> dict:
        """Execute the full bug analysis workflow."""
        console.print(Panel(
            "[bold white]MULTI-AGENT BUG ANALYSIS SYSTEM[/bold white]\n\n"
            "Analyzing bug report and producing root-cause hypothesis + fix plan.\n"
            f"Repository: {self.repo_path}\n"
            f"Agents: {len(self.agents)} | Tools: {len(self.tools)}",
            title="BUG ANALYSIS INITIATED",
            border_style="bright_red",
            padding=(1, 2)
        ))
        
        self.logger.log_step("Orchestrator", "Bug analysis initiated",
                            f"Agents: {list(self.agents.keys())}")
        
        # Execute each agent in workflow order
        for agent_key, phase_name in self.workflow:
            console.print(f"\n{'-'*60}")
            console.print(f"[bold bright_blue]>> {phase_name}[/bold bright_blue]")
            console.print(f"{'-'*60}")
            
            self.logger.log_step("Orchestrator", f"Starting {phase_name}",
                                f"Agent: {agent_key}")
            
            agent = self.agents[agent_key]
            result = agent.run(self.context)
            self.context[agent_key] = result
            
            self.logger.log_step("Orchestrator", f"Completed {phase_name}",
                                f"Agent: {agent_key}")
            
            # Avoid API rate limits between agents (Gemini free tier allows 15 RPM, meaning 1 req every 4s)
            if agent_key != self.workflow[-1][0]:
                console.print("  [dim]Pausing 10s to avoid rate limits...[/dim]")
                time.sleep(10)
        
        # Phase 7: Final Synthesis
        console.print(f"\n{'-'*60}")
        console.print(f"[bold bright_green]>> Phase 7: Final Synthesis[/bold bright_green]")
        console.print(f"{'-'*60}")
        
        final_output = self._synthesize_output()
        
        # Save output
        output_path = os.path.join(self.output_dir, "analysis.json")
        with open(output_path, 'w') as f:
            json.dump(final_output, f, indent=2)
        
        trace_path = self.logger.finalize()
        
        console.print(f"\n[green][OK] Analysis saved to:[/green] {output_path}")
        console.print(f"[green][OK] Trace log saved to:[/green] {trace_path}")
        
        repro_path = self.context.get("reproduction", {}).get("repro_script_path", "N/A")
        console.print(f"[green][OK] Repro script saved to:[/green] {repro_path}")
        
        return final_output
    
    def _synthesize_output(self) -> dict:
        """Synthesize all agent outputs into the final structured output."""
        self.logger.log_step("Orchestrator", "Synthesizing final output")
        
        triage = self.context.get("triage", {}).get("analysis", {})
        log_analyst = self.context.get("log_analyst", {}).get("analysis", {})
        repro = self.context.get("reproduction", {})
        fix_planner = self.context.get("fix_planner", {}).get("analysis", {})
        reviewer = self.context.get("reviewer", {}).get("analysis", {})
        
        prompt = """Synthesize ALL agent outputs into the final structured bug analysis report.

TRIAGE: """ + json.dumps(triage, indent=2)[:2000] + """

LOG ANALYSIS: """ + json.dumps(log_analyst, indent=2)[:2000] + """

REPRODUCTION: """ + json.dumps(repro.get("analysis", {}), indent=2)[:2000] + """

FIX PLAN: """ + json.dumps(fix_planner, indent=2)[:2500] + """

REVIEWER: """ + json.dumps(reviewer, indent=2)[:2000] + """

Produce the FINAL output as a JSON object with EXACTLY this structure:
{
    "bug_summary": {
        "title": "concise bug title",
        "symptoms": ["symptom 1", "symptom 2"],
        "scope": "scope of the bug",
        "severity": "critical/high/medium/low",
        "affected_component": "component name",
        "affected_users": "description of who is affected"
    },
    "evidence": {
        "log_lines": [
            {"line_number": number, "content": "relevant log line", "significance": "why it matters"}
        ],
        "stack_trace_excerpts": ["relevant stack trace lines"],
        "test_failures": ["test that failed and why"]
    },
    "reproduction": {
        "steps": ["step 1", "step 2"],
        "repro_artifact_path": "output/repro_test.py",
        "command_to_run": "python output/repro_test.py",
        "expected_failing_output": "what the repro script outputs when demonstrating the bug",
        "repro_reliability": "always/intermittent"
    },
    "root_cause_hypothesis": {
        "summary": "1-2 sentence root cause",
        "detailed_explanation": "technical explanation",
        "confidence": "high/medium/low",
        "buggy_code_location": {"file": "utils.py", "function": "paginate_results", "line_range": "range"},
        "buggy_code_snippet": "the exact buggy code"
    },
    "patch_plan": {
        "files_impacted": [{"file": "filename", "changes": "description"}],
        "approach": "description of fix approach",
        "fixed_code_snippet": "the corrected code",
        "risks": ["risk 1", "risk 2"],
        "backward_compatible": true/false
    },
    "validation_plan": {
        "tests_to_add": ["test description 1", "test description 2"],
        "regression_checks": ["check 1", "check 2"],
        "verification_commands": ["command 1", "command 2"]
    },
    "open_questions": ["question 1 if any", "question 2"],
    "metadata": {
        "generated_at": "ISO timestamp",
        "agents_consulted": 6,
        "tools_used": ["log_parser", "file_searcher", "test_runner", "code_analyzer"],
        "total_tool_calls": "count"
    }
}

IMPORTANT: Return ONLY valid JSON. No markdown formatting, no code fences."""

        self.logger.log_llm_call("Orchestrator", prompt[:500])
        
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.llm.generate_content, prompt)
        try:
            response = future.result(timeout=10.0)
            result_text = response.text
            self.logger.log_llm_response("Orchestrator", result_text[:500])
        except concurrent.futures.TimeoutError:
            console.print(f"  [yellow]LLM Timeout on synthesis after 10s.[/yellow]")
            self.logger.log_error("Orchestrator", "Final synthesis LLM call timed out")
            raise Exception("LLM call timed out")
        except Exception as e:
            console.print(f"  [red]LLM Error on synthesis: {e}[/red]")
            self.logger.log_error("Orchestrator", f"Final synthesis LLM call failed: {e}")
            raise
        
        try:
            
            cleaned = result_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
            
            output = json.loads(cleaned)
            
            # Ensure metadata
            if "metadata" not in output:
                output["metadata"] = {}
            output["metadata"]["generated_at"] = datetime.now().isoformat()
            output["metadata"]["agents_consulted"] = len(self.agents)
            output["metadata"]["tools_used"] = list(self.tools.keys())
            
            return output
            
        except json.JSONDecodeError as e:
            self.logger.log_error("Orchestrator", f"Failed to parse final JSON: {e}")
            return {
                "bug_summary": triage.get("summary", "Pagination bug causing duplicate items"),
                "evidence": {"log_lines": log_analyst.get("key_log_lines", [])},
                "reproduction": repro.get("analysis", {}),
                "root_cause_hypothesis": fix_planner.get("root_cause", {}),
                "patch_plan": fix_planner.get("fix_proposal", {}),
                "validation_plan": fix_planner.get("verification_plan", {}),
                "open_questions": [],
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "note": "Fallback output due to JSON parse failure"
                }
            }
        except Exception as e:
            self.logger.log_error("Orchestrator", f"Synthesis failed: {e}")
            raise
