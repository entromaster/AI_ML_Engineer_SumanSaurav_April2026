"""
Customer Success Agent (Extra Agent)
Cross-references support tickets with feedback themes and assesses customer health
for the product launch war room.
"""

import json
from .base_agent import BaseAgent


class CustomerSuccessAgent(BaseAgent):
    """Analyzes customer health, support trends, and escalation risks."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="James Rodriguez",
            role="Customer Success Director",
            persona=(
                "You are a customer success leader who understands customer health scores, "
                "churn signals, and support escalation patterns. You bridge between technical "
                "issues and customer impact. You advocate for the customer experience and "
                "identify segments most at risk."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Analyzing customer health, support trends, and churn risk...")
        
        # Step 1: Analyze feedback for customer-centric insights
        feedback_path = context.get("feedback_path")
        sentiment_result = self.call_tool("analyze_feedback", filepath=feedback_path)
        
        # Step 2: Get metric trends for support volume
        metrics_path = context.get("metrics_path")
        trend_comparison = self.call_tool("compare_all_metrics", filepath=metrics_path)
        
        prompt = """As Customer Success Director, assess the impact on customer health and satisfaction.

FEEDBACK ANALYSIS:
""" + json.dumps(sentiment_result, indent=2)[:3500] + """

METRIC TRENDS (focus on retention and support volume):
""" + json.dumps(trend_comparison, indent=2)[:2000] + """

RELEASE NOTES:
""" + context.get("release_notes", "Not available")[:1500] + """

Respond with a JSON object containing:
{
    "summary": "2-3 sentence customer health assessment",
    "customer_health": {
        "overall_health_score": "good/at-risk/critical",
        "retention_impact": "assessment of D1/D7 retention changes",
        "support_load": "assessment of support ticket trends",
        "top_complaint_categories": ["category 1 with count", "category 2"]
    },
    "at_risk_segments": [
        {"segment": "description", "risk_level": "high/medium/low", "estimated_users": "number/range", "primary_issue": "description"}
    ],
    "escalation_risk": {
        "level": "low/medium/high",
        "potential_escalations": ["description 1", "description 2"],
        "enterprise_impact": "assessment"
    },
    "customer_actions_needed": [
        {"action": "description", "target_segment": "who", "timeline": "when", "channel": "how"}
    ],
    "recommendation_signal": "proceed/pause/rollback",
    "recommendation_reasoning": "customer-centric reasoning"
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
                "sentiment_analysis": {"themes_identified": True},
                "trend_comparison": {"focused_on": ["support_tickets", "retention"]}
            },
            "analysis": analysis
        }
