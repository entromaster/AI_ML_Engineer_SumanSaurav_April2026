"""
Engineering/SRE Agent (Extra Agent)
Assesses technical health, crash rates, latency, and system stability
for the product launch war room.
"""

import json
from .base_agent import BaseAgent


class EngineeringAgent(BaseAgent):
    """Analyzes technical health metrics and system stability."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Marcus Williams",
            role="Engineering Lead / SRE",
            persona=(
                "You are a senior engineering lead with deep SRE experience. "
                "You focus on system stability, error rates, latency, and technical debt. "
                "You think in terms of SLOs, error budgets, and incident severity levels. "
                "You provide concrete technical recommendations and timeline estimates."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Assessing technical health, stability, and system metrics...")
        
        # Step 1: Analyze metrics with focus on technical health
        metrics_path = context.get("metrics_path")
        metric_analysis = self.call_tool("analyze_all_metrics", filepath=metrics_path)
        
        # Step 2: Check thresholds
        threshold_check = self.call_tool("check_all_thresholds", filepath=metrics_path)
        
        # Extract technical metrics
        tech_metrics = {}
        for key in ["crash_rate_pct", "api_latency_p95_ms", "payment_success_rate_pct"]:
            tech_metrics[key] = metric_analysis.get("metrics", {}).get(key, {})
        
        prompt = """As Engineering Lead, assess the technical health of the Smart Insights launch.

TECHNICAL METRICS ANALYSIS:
""" + json.dumps(tech_metrics, indent=2)[:3000] + """

THRESHOLD CHECK:
""" + json.dumps(threshold_check, indent=2)[:2000] + """

RELEASE NOTES (known issues):
""" + context.get("release_notes", "Not available")[:2000] + """

Respond with a JSON object containing:
{
    "summary": "2-3 sentence technical health assessment",
    "system_health": {
        "overall_status": "healthy/degraded/critical",
        "crash_rate_assessment": "analysis with numbers",
        "latency_assessment": "analysis with numbers",
        "payment_health": "analysis with numbers",
        "error_budget_status": "analysis of error budget consumption"
    },
    "incident_assessment": {
        "severity_level": "SEV1/SEV2/SEV3/SEV4",
        "active_issues": ["issue 1", "issue 2"],
        "root_causes_identified": ["cause 1", "cause 2"],
        "fixes_in_progress": ["fix 1", "fix 2"]
    },
    "technical_recommendations": [
        {"action": "description", "effort": "hours/days", "impact": "high/medium/low", "priority": "P0/P1/P2"}
    ],
    "can_technical_issues_be_resolved": true/false,
    "estimated_fix_timeline": "description",
    "recommendation_signal": "proceed/pause/rollback",
    "recommendation_reasoning": "technical reasoning"
}"""
        
        llm_response = self.call_llm(prompt)
        
        try:
            cleaned = llm_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
            analysis = json.loads(cleaned)
        except json.JSONDecodeError:
            analysis = {"raw_response": llm_response, "parse_error": True}
        
        return {
            "agent": self.name,
            "role": self.role,
            "tool_results": {
                "metric_analysis": {"focused_on": ["crash_rate", "latency", "payment"]},
                "threshold_check": threshold_check
            },
            "analysis": analysis
        }
