"""
Log Analyst Agent
Searches logs for stack traces, error signatures, frequency,
correlation with deploy/version, and key anomalies.
"""

import json
from .base_agent import BaseAgent


class LogAnalystAgent(BaseAgent):
    """Analyzes application logs to find evidence of the bug."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Log Analyzer",
            role="Log Analysis Specialist",
            persona=(
                "You are a log analysis expert who can quickly identify relevant "
                "error patterns in noisy log files. You differentiate between real "
                "issues and red herrings, correlate timestamps, and extract actionable "
                "evidence. You always quantify your findings."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Analyzing logs for stack traces, errors, and anomalies...")
        
        # Step 1: Parse logs
        logs_path = context.get("logs_path")
        log_analysis = self.call_tool("parse_logs", filepath=logs_path)
        
        # Step 2: Search for specific patterns based on triage
        triage = context.get("triage", {}).get("analysis", {})
        hypotheses = triage.get("hypotheses", [])
        
        # Search for pagination-related entries
        search_result = self.call_tool("search_files",
                                        search_path=logs_path,
                                        pattern="offset|start=|page|duplicate|Expected.*got",
                                        file_glob="*.txt")
        
        prompt = """Analyze these parsed logs and search results to find evidence of the bug.

LOG ANALYSIS:
""" + json.dumps(log_analysis, indent=2)[:4000] + """

SEARCH RESULTS (pagination-related entries):
""" + json.dumps(search_result, indent=2)[:2000] + """

TRIAGE HYPOTHESES:
""" + json.dumps(hypotheses, indent=2)[:1000] + """

Respond with a JSON object containing:
{
    "summary": "2-3 sentence log analysis summary",
    "stack_traces_found": [
        {"error_type": "type", "file": "filename", "line": line_number, "description": "what happened"}
    ],
    "error_signatures": [
        {"pattern": "error pattern", "frequency": count, "relevance": "high/medium/low", "description": "explanation"}
    ],
    "evidence_for_hypotheses": [
        {"hypothesis": "from triage", "supporting_evidence": ["log line 1", "log line 2"], "contradicting_evidence": [], "verdict": "supported/unsupported/inconclusive"}
    ],
    "red_herrings": ["description of noise entries that are not related"],
    "timeline_analysis": {
        "first_error": "timestamp",
        "error_sequence": ["event 1", "event 2"],
        "correlation": "description of any correlation found"
    },
    "key_log_lines": [
        {"line_number": number, "content": "the log line", "significance": "why this matters"}
    ],
    "confidence_in_root_cause": "high/medium/low",
    "recommended_next_steps": ["step 1", "step 2"]
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
                "log_analysis": log_analysis,
                "search_results": search_result
            },
            "analysis": analysis
        }
