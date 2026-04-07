"""
Risk/Critic Agent
Challenges assumptions, highlights risks, and requests additional evidence
for the product launch war room.
"""

import json
from .base_agent import BaseAgent


class RiskAgent(BaseAgent):
    """Critiques and challenges the war room's analysis and recommendations."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Aisha Okafor",
            role="Risk Manager & Devil's Advocate",
            persona=(
                "You are a skeptical risk manager who challenges every assumption. "
                "Your job is to find holes in arguments, identify blind spots, "
                "and stress-test the recommendation. You ask 'what if' questions "
                "and demand evidence. You are not contrarian for its own sake — "
                "you want the team to make a well-informed decision."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Challenging assumptions and identifying risks...")
        
        # Step 1: Review metric analysis for gaps
        metrics_path = context.get("metrics_path")
        metric_analysis = self.call_tool("analyze_all_metrics", filepath=metrics_path)
        
        # Step 2: Review all previous agent analyses
        data_analyst = context.get("data_analyst", {}).get("analysis", {})
        marketing = context.get("marketing", {}).get("analysis", {})
        pm = context.get("pm", {}).get("analysis", {})
        engineering = context.get("engineering", {}).get("analysis", {})
        customer_success = context.get("customer_success", {}).get("analysis", {})
        
        prompt = """As the Risk Manager, critically evaluate ALL previous analyses and the PM's recommendation. Your job is to:
1. Find flaws in reasoning
2. Identify risks that others missed
3. Challenge assumptions
4. Demand missing evidence
5. Stress-test the recommendation

PM'S RECOMMENDATION: """ + json.dumps(pm.get("recommendation", "unknown")) + """

PM'S FULL ANALYSIS:
""" + json.dumps(pm, indent=2)[:2500] + """

DATA ANALYST FINDINGS:
""" + json.dumps(data_analyst, indent=2)[:2000] + """

MARKETING ASSESSMENT:
""" + json.dumps(marketing, indent=2)[:1500] + """

ENGINEERING ASSESSMENT:
""" + json.dumps(engineering, indent=2)[:1500] + """

CUSTOMER SUCCESS ASSESSMENT:
""" + json.dumps(customer_success, indent=2)[:1500] + """

RAW METRIC ANOMALIES:
""" + json.dumps({k: v.get("anomalies", []) for k, v in metric_analysis.get("metrics", {}).items()}, indent=2)[:1500] + """

Respond with a JSON object containing:
{
    "summary": "2-3 sentence risk assessment overview",
    "assumptions_challenged": [
        {"assumption": "what was assumed", "challenge": "why it might be wrong", "evidence_needed": "what data would settle this"}
    ],
    "blind_spots": [
        {"area": "what was missed", "potential_impact": "high/medium/low", "recommendation": "what to do"}
    ],
    "risk_register": [
        {"risk": "description", "likelihood": "high/medium/low", "impact": "high/medium/low", "mitigation": "proposed action", "owner": "team/person"}
    ],
    "worst_case_scenarios": [
        {"scenario": "what could go wrong", "probability": "high/medium/low", "contingency": "what to do if it happens"}
    ],
    "missing_data": ["data point 1 that would help", "data point 2"],
    "recommendation_challenge": {
        "agrees_with_pm": true/false,
        "alternative_recommendation": "if different from PM",
        "reasoning": "why agree or disagree",
        "conditions": ["condition for agreement"]
    },
    "overall_risk_level": "low/moderate/high/critical"
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
                "metric_review": {"anomalies_reviewed": True}
            },
            "analysis": analysis
        }
