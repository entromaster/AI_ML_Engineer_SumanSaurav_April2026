"""
Marketing/Communications Agent
Assesses messaging, customer perception, and communication actions
for the product launch war room.
"""

import json
from .base_agent import BaseAgent


class MarketingAgent(BaseAgent):
    """Analyzes user feedback, customer perception, and communication needs."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Priya Sharma",
            role="Head of Marketing & Communications",
            persona=(
                "You are a seasoned marketing leader who understands brand perception "
                "and customer communication. You focus on how the launch is being perceived, "
                "what messaging needs to happen (internal and external), and how to manage "
                "the narrative. You care deeply about customer trust and brand reputation."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Analyzing customer sentiment, perception, and communication needs...")
        
        # Step 1: Run sentiment analysis tool
        feedback_path = context.get("feedback_path")
        sentiment_result = self.call_tool("analyze_feedback", filepath=feedback_path)
        
        # Step 2: Get data analyst findings for context
        data_analyst = context.get("data_analyst", {})
        
        # Step 3: Ask LLM for communication assessment
        prompt = """Based on the user feedback analysis and data context, provide your marketing and communications assessment.

SENTIMENT ANALYSIS:
""" + json.dumps(sentiment_result, indent=2)[:4000] + """

DATA ANALYST FINDINGS (for context):
""" + json.dumps(data_analyst.get("analysis", {}), indent=2)[:2000] + """

RELEASE NOTES CONTEXT:
""" + context.get("release_notes", "Not available")[:2000] + """

Respond with a JSON object containing:
{
    "summary": "2-3 sentence overview of customer perception",
    "sentiment_assessment": {
        "overall_mood": "positive/mixed/negative",
        "key_positive_themes": ["theme 1", "theme 2"],
        "key_negative_themes": ["theme 1", "theme 2"],
        "brand_risk_level": "low/medium/high",
        "brand_risk_details": "explanation"
    },
    "customer_impact": {
        "affected_segments": ["segment 1", "segment 2"],
        "churn_risk": "low/medium/high",
        "nps_impact_estimate": "description"
    },
    "communication_plan": {
        "internal_messaging": [
            {"audience": "engineering", "message": "key points", "urgency": "immediate/24h/48h"},
            {"audience": "support", "message": "key points", "urgency": "immediate/24h/48h"}
        ],
        "external_messaging": [
            {"channel": "email/in-app/social/blog", "message": "key points", "timing": "when"}
        ]
    },
    "recommendation_signal": "proceed/pause/rollback",
    "recommendation_reasoning": "communication perspective reasoning"
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
                "sentiment_analysis": sentiment_result
            },
            "analysis": analysis
        }
