"""
Product Manager Agent
Defines success criteria, user impact, and go/no-go framing
for the product launch war room.
"""

import json
from .base_agent import BaseAgent


class PMAgent(BaseAgent):
    """Synthesizes all inputs to frame the go/no-go decision."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Sarah Chen",
            role="VP of Product",
            persona=(
                "You are a decisive product leader who balances user impact, business goals, "
                "and technical constraints. You synthesize input from data, marketing, engineering, "
                "and customer success to make a clear recommendation. You frame decisions in terms "
                "of user value, revenue risk, and strategic outcomes. You are accountability-focused."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Synthesizing all inputs for go/no-go decision framing...")
        
        # Step 1: Check thresholds for formal pass/fail
        metrics_path = context.get("metrics_path")
        threshold_check = self.call_tool("check_all_thresholds", filepath=metrics_path)
        
        # Step 2: Gather all previous agent analyses
        data_analyst = context.get("data_analyst", {}).get("analysis", {})
        marketing = context.get("marketing", {}).get("analysis", {})
        engineering = context.get("engineering", {}).get("analysis", {})
        customer_success = context.get("customer_success", {}).get("analysis", {})
        
        prompt = """As VP of Product, synthesize all war room inputs and frame the launch decision.

THRESHOLD CHECK (formal success criteria):
""" + json.dumps(threshold_check, indent=2)[:3000] + """

DATA ANALYST ASSESSMENT:
""" + json.dumps(data_analyst, indent=2)[:2000] + """

MARKETING ASSESSMENT:
""" + json.dumps(marketing, indent=2)[:2000] + """

ENGINEERING ASSESSMENT:
""" + json.dumps(engineering, indent=2)[:2000] + """

CUSTOMER SUCCESS ASSESSMENT:
""" + json.dumps(customer_success, indent=2)[:2000] + """

RELEASE NOTES:
""" + context.get("release_notes", "Not available")[:2000] + """

Respond with a JSON object containing:
{
    "summary": "3-4 sentence executive summary of the situation",
    "decision_framing": {
        "success_criteria_status": "X of Y criteria passed",
        "user_impact_assessment": "description of user impact",
        "revenue_impact_assessment": "description of revenue risk",
        "strategic_considerations": "broader strategic context"
    },
    "go_nogo_analysis": {
        "factors_for_proceed": ["factor 1", "factor 2"],
        "factors_for_pause": ["factor 1", "factor 2"],
        "factors_for_rollback": ["factor 1", "factor 2"]
    },
    "recommendation": "Proceed/Pause/Roll Back",
    "recommendation_reasoning": "detailed reasoning for the recommendation",
    "conditions_for_proceed": ["condition 1 that must be met", "condition 2"],
    "action_items": [
        {"action": "description", "owner": "team/person", "timeline": "immediate/24h/48h", "priority": "P0/P1/P2"}
    ],
    "confidence_level": "high/medium/low",
    "what_would_increase_confidence": ["factor 1", "factor 2"]
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
                "threshold_check": threshold_check
            },
            "analysis": analysis
        }
