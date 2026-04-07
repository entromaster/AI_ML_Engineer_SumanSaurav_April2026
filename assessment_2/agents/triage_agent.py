"""
Triage Agent
Extracts key symptoms, expected vs actual behavior, environment details,
and prioritizes hypotheses from the bug report.
"""

import json
from .base_agent import BaseAgent


class TriageAgent(BaseAgent):
    """Triages bug reports and prioritizes investigation hypotheses."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Triage Bot",
            role="Bug Triage Specialist",
            persona=(
                "You are an experienced bug triage specialist who quickly identifies "
                "the most likely failure surface from bug reports. You extract key symptoms, "
                "differentiate between expected and actual behavior, note environment details, "
                "and rank hypotheses by likelihood. You are methodical and precise."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Parsing bug report, extracting symptoms, and prioritizing hypotheses...")
        
        # Step 1: Read the bug report
        bug_report_path = context.get("bug_report_path")
        bug_report = self.call_tool("read_file_content", filepath=bug_report_path)
        
        # Step 2: Search for related code files
        repo_path = context.get("repo_path")
        search_results = self.call_tool("search_files", 
                                         search_path=repo_path,
                                         pattern="paginate|pagination|page|per_page",
                                         file_glob="*.py")
        
        prompt = """Analyze this bug report and provide a triage assessment.

BUG REPORT:
""" + bug_report.get("content", "Not available")[:3000] + """

CODE SEARCH RESULTS (files mentioning pagination):
""" + json.dumps(search_results, indent=2)[:2000] + """

Respond with a JSON object containing:
{
    "summary": "1-2 sentence bug summary",
    "symptoms": ["symptom 1", "symptom 2"],
    "expected_behavior": "what should happen",
    "actual_behavior": "what actually happens",
    "environment": {
        "language": "Python version",
        "framework": "Flask version",
        "database": "SQLite",
        "os": "relevant OS info"
    },
    "severity": "critical/high/medium/low",
    "category": "data_integrity/performance/crash/ui/security",
    "affected_components": ["component 1", "component 2"],
    "hypotheses": [
        {"rank": 1, "hypothesis": "most likely cause", "confidence": "high/medium/low", "evidence": "why this is likely"},
        {"rank": 2, "hypothesis": "alternative cause", "confidence": "medium/low", "evidence": "supporting evidence"}
    ],
    "investigation_plan": ["step 1", "step 2", "step 3"],
    "files_to_examine": ["file1.py", "file2.py"]
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
                "bug_report": bug_report,
                "code_search": search_results
            },
            "analysis": analysis
        }
