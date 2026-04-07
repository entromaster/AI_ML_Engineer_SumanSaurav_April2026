"""
Reviewer/Critic Agent
Challenges weak assumptions, checks repro minimality,
verifies fix plan safety, and suggests edge cases.
"""

import json
from .base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    """Reviews and critiques the analysis and fix plan."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Code Reviewer",
            role="Senior Code Reviewer & Critic",
            persona=(
                "You are a meticulous senior code reviewer who challenges every assumption. "
                "You verify that reproductions are truly minimal, fix plans are safe, "
                "and edge cases are covered. You think about what could go wrong with the "
                "proposed fix and whether the root cause analysis is complete."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Reviewing analysis, challenging assumptions, checking edge cases...")
        
        # Gather all previous agent analyses
        triage = context.get("triage", {}).get("analysis", {})
        log_analyst = context.get("log_analyst", {}).get("analysis", {})
        repro = context.get("reproduction", {}).get("analysis", {})
        fix_planner = context.get("fix_planner", {}).get("analysis", {})
        
        prompt = """As the Code Reviewer, critically evaluate the entire bug analysis pipeline.

TRIAGE ASSESSMENT:
""" + json.dumps(triage, indent=2)[:2000] + """

LOG ANALYSIS:
""" + json.dumps(log_analyst, indent=2)[:2000] + """

REPRODUCTION RESULTS:
""" + json.dumps(repro, indent=2)[:2000] + """

FIX PLAN:
""" + json.dumps(fix_planner, indent=2)[:3000] + """

Critically evaluate and respond with a JSON object containing:
{
    "overall_assessment": "strong/adequate/weak",
    "triage_review": {
        "quality": "good/acceptable/poor",
        "missed_symptoms": ["any symptoms not captured"],
        "hypothesis_quality": "assessment of hypothesis ranking"
    },
    "reproduction_review": {
        "is_truly_minimal": true/false,
        "minimality_issues": ["any issues with the repro"],
        "reliability": "always_reproduces/intermittent/unreliable",
        "suggested_improvements": ["improvement 1"]
    },
    "fix_plan_review": {
        "correctness": "correct/likely_correct/uncertain/incorrect",
        "safety_assessment": "safe/needs_review/risky",
        "completeness": "complete/partial/incomplete",
        "issues_found": ["issue 1", "issue 2"],
        "edge_cases_missed": [
            {"case": "description", "potential_impact": "what could go wrong"}
        ]
    },
    "assumptions_challenged": [
        {"assumption": "what was assumed", "challenge": "why it might be wrong", "suggestion": "what to do instead"}
    ],
    "additional_edge_cases": [
        {"case": "description", "test_input": "example input", "expected_behavior": "what should happen"}
    ],
    "risk_assessment": {
        "fix_introduction_risk": "low/medium/high",
        "regression_risk": "low/medium/high",
        "deployment_concerns": ["concern 1", "concern 2"]
    },
    "final_verdict": {
        "ready_to_proceed": true/false,
        "blocking_issues": ["issue 1 if any"],
        "recommendations": ["recommendation 1", "recommendation 2"]
    }
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
            "tool_results": {},
            "analysis": analysis
        }
