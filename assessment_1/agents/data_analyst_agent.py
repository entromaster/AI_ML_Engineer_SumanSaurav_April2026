"""
Data Analyst Agent
Analyzes quantitative metrics, trends, anomalies, and statistical confidence
for the product launch war room.
"""

import json
from .base_agent import BaseAgent


class DataAnalystAgent(BaseAgent):
    """Analyzes dashboard metrics and provides quantitative insights."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Alex Chen",
            role="Senior Data Analyst",
            persona=(
                "You are a meticulous data analyst who prioritizes statistical rigor. "
                "You look for trends, anomalies, and correlations in the data. "
                "You provide confidence levels for your findings and always cite specific numbers. "
                "You flag when sample sizes are too small for conclusive analysis."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Analyzing dashboard metrics, trends, and anomalies...")
        
        # Step 1: Run metric analysis tool
        metrics_path = context.get("metrics_path")
        metric_analysis = self.call_tool("analyze_all_metrics", filepath=metrics_path)
        
        # Step 2: Run trend comparison tool
        trend_comparison = self.call_tool("compare_all_metrics", filepath=metrics_path)
        
        # Step 3: Run threshold check tool
        threshold_results = self.call_tool("check_all_thresholds", filepath=metrics_path)
        
        # Step 4: Ask LLM to synthesize findings
        prompt = """Based on the quantitative analysis below, provide your assessment.

METRIC ANALYSIS (trends, anomalies, statistics):
""" + json.dumps(metric_analysis, indent=2)[:4000] + """

TREND COMPARISON (pre-launch vs post-launch):
""" + json.dumps(trend_comparison, indent=2)[:3000] + """

THRESHOLD CHECK (success criteria pass/fail):
""" + json.dumps(threshold_results, indent=2)[:3000] + """

Respond with a JSON object containing:
{
    "summary": "2-3 sentence overview of the data picture",
    "key_findings": ["finding 1 with specific numbers", "finding 2", ...],
    "critical_metrics": [{"metric": "name", "status": "critical/warning/healthy", "detail": "explanation with numbers"}],
    "anomalies_detected": [{"metric": "name", "description": "what happened", "severity": "high/medium/low"}],
    "data_confidence": "high/medium/low",
    "confidence_reasoning": "why this confidence level",
    "recommendation_signal": "proceed/pause/rollback",
    "recommendation_reasoning": "data-driven reasoning"
}"""
        
        llm_response = self.call_llm(prompt)
        
        try:
            # Try to parse JSON from response
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
                "metric_analysis": metric_analysis,
                "trend_comparison": trend_comparison,
                "threshold_results": threshold_results
            },
            "analysis": analysis
        }
