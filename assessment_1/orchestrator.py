"""
War Room Orchestrator
Manages the multi-agent workflow for the product launch decision.
Coordinates agent execution, manages shared context, and produces the final decision.
"""

import os
import sys
import json
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from llm_wrapper import LLMWrapper

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import google.generativeai as genai

from agents.data_analyst_agent import DataAnalystAgent
from agents.marketing_agent import MarketingAgent
from agents.engineering_agent import EngineeringAgent
from agents.customer_success_agent import CustomerSuccessAgent
from agents.pm_agent import PMAgent
from agents.risk_agent import RiskAgent
from tools.metric_analyzer import analyze_all_metrics
from tools.sentiment_analyzer import analyze_feedback
from tools.trend_comparator import compare_all_metrics
from tools.threshold_checker import check_all_thresholds
from trace_logger import TraceLogger

console = Console(force_terminal=True)


class WarRoomOrchestrator:
    """
    Orchestrates the multi-agent war room workflow.
    
    Workflow:
    1. Data Analyst → quantitative analysis
    2. Marketing/Comms → sentiment and perception analysis
    3. Customer Success → customer health assessment
    4. Engineering → technical health assessment
    5. Product Manager → decision framing and recommendation
    6. Risk/Critic → challenge and risk assessment
    7. Final Synthesis → structured decision output
    """
    
    def __init__(self, data_dir: str, output_dir: str, provider: str, api_key: str):
        self.data_dir = data_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure LLM Client
        self.llm = LLMWrapper(provider, api_key)
        
        # Initialize logger
        self.logger = TraceLogger(output_dir)
        
        # Register tools
        self.tools = {
            "analyze_all_metrics": analyze_all_metrics,
            "analyze_feedback": analyze_feedback,
            "compare_all_metrics": compare_all_metrics,
            "check_all_thresholds": check_all_thresholds
        }
        
        # Load release notes
        release_notes_path = os.path.join(data_dir, "release_notes.md")
        with open(release_notes_path, 'r') as f:
            self.release_notes = f.read()
        
        # Shared context
        self.context = {
            "metrics_path": os.path.join(data_dir, "metrics.json"),
            "feedback_path": os.path.join(data_dir, "user_feedback.json"),
            "release_notes": self.release_notes
        }
        
        # Initialize agents
        self.agents = {
            "data_analyst": DataAnalystAgent(self.tools, self.llm, self.logger),
            "marketing": MarketingAgent(self.tools, self.llm, self.logger),
            "customer_success": CustomerSuccessAgent(self.tools, self.llm, self.logger),
            "engineering": EngineeringAgent(self.tools, self.llm, self.logger),
            "pm": PMAgent(self.tools, self.llm, self.logger),
            "risk": RiskAgent(self.tools, self.llm, self.logger)
        }
        
        # Workflow order
        self.workflow = [
            ("data_analyst", "Phase 1: Quantitative Analysis"),
            ("marketing", "Phase 2: Customer Perception & Communication"),
            ("customer_success", "Phase 3: Customer Health Assessment"),
            ("engineering", "Phase 4: Technical Health Assessment"),
            ("pm", "Phase 5: Decision Framing"),
            ("risk", "Phase 6: Risk Assessment & Challenge")
        ]
    
    def run(self) -> dict:
        """Execute the full war room workflow and produce a decision."""
        console.print(Panel(
            "[bold white]PURPLEMERIT WAR ROOM - SMART INSIGHTS v2.4.0 LAUNCH[/bold white]\n\n"
            "Convening cross-functional war room to evaluate launch status.\n"
            f"Analysis period: Based on mock dashboard data\n"
            f"Agents: {len(self.agents)} | Tools: {len(self.tools)}",
            title="WAR ROOM INITIATED",
            border_style="bright_blue",
            padding=(1, 2)
        ))
        
        self.logger.log_step("Orchestrator", "War room initiated", 
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
            
            # Store result in shared context for next agents
            self.context[agent_key] = result
            
            self.logger.log_step("Orchestrator", f"Completed {phase_name}",
                                f"Agent: {agent_key}")
            
            # Avoid API rate limits between agents (Gemini free tier allows 15 RPM, meaning 1 req every 4s)
            if agent_key != self.workflow[-1][0]:
                console.print("  [dim]Pausing 10s to avoid rate limits...[/dim]")
                time.sleep(10)
        
        # Phase 7: Final Synthesis
        console.print(f"\n{'-'*60}")
        console.print(f"[bold bright_green]>> Phase 7: Final Decision Synthesis[/bold bright_green]")
        console.print(f"{'-'*60}")
        
        final_decision = self._synthesize_decision()
        
        # Save output
        output_path = os.path.join(self.output_dir, "decision.json")
        with open(output_path, 'w') as f:
            json.dump(final_decision, f, indent=2)
        
        self.logger.log_decision(
            final_decision.get("decision", "Unknown"),
            final_decision.get("confidence_score", "Unknown"),
            final_decision.get("rationale", {}).get("summary", "No rationale provided")
        )
        
        # Finalize trace log
        trace_path = self.logger.finalize()
        
        console.print(f"\n[green][OK] Decision saved to:[/green] {output_path}")
        console.print(f"[green][OK] Trace log saved to:[/green] {trace_path}")
        
        return final_decision
    
    def _synthesize_decision(self) -> dict:
        """Synthesize all agent outputs into a final structured decision."""
        self.logger.log_step("Orchestrator", "Synthesizing final decision")
        
        # Collect all agent recommendations
        pm_analysis = self.context.get("pm", {}).get("analysis", {})
        risk_analysis = self.context.get("risk", {}).get("analysis", {})
        data_analysis = self.context.get("data_analyst", {}).get("analysis", {})
        marketing_analysis = self.context.get("marketing", {}).get("analysis", {})
        engineering_analysis = self.context.get("engineering", {}).get("analysis", {})
        cs_analysis = self.context.get("customer_success", {}).get("analysis", {})
        
        # Ask LLM for final synthesis
        prompt = """You are the War Room Orchestrator. Synthesize ALL agent inputs into a FINAL structured decision.

PM RECOMMENDATION: """ + json.dumps(pm_analysis.get("recommendation", "unknown")) + """
PM ANALYSIS: """ + json.dumps(pm_analysis, indent=2)[:2500] + """

RISK ASSESSMENT: """ + json.dumps(risk_analysis, indent=2)[:2500] + """

DATA ANALYST: """ + json.dumps(data_analysis, indent=2)[:1500] + """

MARKETING: """ + json.dumps(marketing_analysis, indent=2)[:1500] + """

ENGINEERING: """ + json.dumps(engineering_analysis, indent=2)[:1500] + """

CUSTOMER SUCCESS: """ + json.dumps(cs_analysis, indent=2)[:1500] + """

Produce the FINAL WAR ROOM DECISION as a JSON object with EXACTLY this structure:
{
    "decision": "Proceed" or "Pause" or "Roll Back",
    "rationale": {
        "summary": "3-5 sentence executive summary of why this decision was made",
        "key_metric_drivers": [
            {"metric": "name", "current_value": "value", "threshold": "threshold", "status": "pass/fail", "impact": "description"}
        ],
        "feedback_summary": {
            "total_entries": number,
            "positive_pct": number,
            "negative_pct": number,
            "top_issues": ["issue 1", "issue 2", "issue 3"]
        }
    },
    "risk_register": [
        {"risk_id": "R1", "description": "risk description", "likelihood": "high/medium/low", "impact": "high/medium/low", "mitigation": "proposed action", "owner": "team/person", "status": "open/mitigating/accepted"}
    ],
    "action_plan_24_48h": [
        {"action_id": "A1", "action": "description", "owner": "team/person", "timeline": "immediate/12h/24h/48h", "priority": "P0/P1/P2", "success_criteria": "how to verify"}
    ],
    "communication_plan": {
        "internal": [
            {"audience": "team/group", "message_summary": "key points", "channel": "slack/email/meeting", "timing": "when"}
        ],
        "external": [
            {"audience": "customers/public", "message_summary": "key points", "channel": "email/in-app/blog/social", "timing": "when"}
        ]
    },
    "confidence_score": "high (>80%) / medium (50-80%) / low (<50%)",
    "confidence_factors": {
        "supporting": ["factor 1", "factor 2"],
        "undermining": ["factor 1", "factor 2"],
        "would_increase_confidence": ["action/data 1", "action/data 2"]
    },
    "agent_consensus": {
        "data_analyst": "proceed/pause/rollback",
        "marketing": "proceed/pause/rollback",
        "engineering": "proceed/pause/rollback",
        "customer_success": "proceed/pause/rollback",
        "pm": "proceed/pause/rollback",
        "risk_critic": "agrees/disagrees with final decision"
    },
    "next_review": "when the next war room should reconvene",
    "metadata": {
        "generated_at": "ISO timestamp",
        "agents_consulted": 6,
        "tools_used": ["metric_analyzer", "sentiment_analyzer", "trend_comparator", "threshold_checker"],
        "data_period": "2026-03-24 to 2026-04-06"
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
            
            # Parse JSON
            cleaned = result_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
            
            decision = json.loads(cleaned)
            
            # Ensure metadata
            if "metadata" not in decision:
                decision["metadata"] = {}
            decision["metadata"]["generated_at"] = datetime.now().isoformat()
            decision["metadata"]["agents_consulted"] = len(self.agents)
            decision["metadata"]["tools_used"] = list(self.tools.keys())
            
            return decision
            
        except json.JSONDecodeError as e:
            self.logger.log_error("Orchestrator", f"Failed to parse final decision JSON: {e}")
            # Return a structured fallback
            return {
                "decision": pm_analysis.get("recommendation", "Pause"),
                "rationale": {
                    "summary": "Decision based on PM recommendation (LLM synthesis failed to produce valid JSON)",
                    "key_metric_drivers": [],
                    "feedback_summary": {}
                },
                "risk_register": risk_analysis.get("risk_register", []),
                "action_plan_24_48h": pm_analysis.get("action_items", []),
                "communication_plan": marketing_analysis.get("communication_plan", {}),
                "confidence_score": "low",
                "confidence_factors": {"supporting": [], "undermining": ["JSON synthesis failed"], "would_increase_confidence": []},
                "agent_consensus": {},
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "agents_consulted": len(self.agents),
                    "tools_used": list(self.tools.keys()),
                    "note": "Fallback decision due to JSON parse failure"
                }
            }
        except Exception as e:
            self.logger.log_error("Orchestrator", f"Final synthesis failed: {e}")
            raise
