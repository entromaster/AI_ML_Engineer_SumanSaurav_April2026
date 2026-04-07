"""
Fix Planner Agent
Proposes root-cause hypothesis, patch approach, and verification plan.
References reproduction outcome and log evidence.
"""

import json
import os
from .base_agent import BaseAgent


class FixPlannerAgent(BaseAgent):
    """Proposes root cause analysis and fix plan."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Fix Planner",
            role="Senior Debugging Engineer",
            persona=(
                "You are a senior engineer who specializes in root cause analysis. "
                "You trace bugs to their exact source, propose minimal and safe fixes, "
                "and design comprehensive verification plans. You always consider "
                "regression risks and edge cases in your fix proposals."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Analyzing root cause and proposing fix plan...")
        
        # Step 1: Read the buggy source file
        repo_path = context.get("repo_path")
        utils_path = os.path.join(repo_path, "utils.py")
        
        # Analyze the code
        code_analysis = self.call_tool("analyze_file", filepath=utils_path)
        func_detail = self.call_tool("find_function", filepath=utils_path, function_name="paginate_results")
        
        # Trace call chain
        call_chain = self.call_tool("trace_call_chain", directory=repo_path, function_name="paginate_results")
        
        # Gather context
        triage = context.get("triage", {}).get("analysis", {})
        log_analyst = context.get("log_analyst", {}).get("analysis", {})
        repro = context.get("reproduction", {}).get("analysis", {})
        
        prompt = """Based on all evidence, provide a root cause analysis and fix plan.

BUGGY FUNCTION:
""" + json.dumps(func_detail, indent=2)[:3000] + """

CODE STRUCTURE:
""" + json.dumps(code_analysis, indent=2)[:1500] + """

CALL CHAIN (where paginate_results is called):
""" + json.dumps(call_chain, indent=2)[:1000] + """

TRIAGE:
""" + json.dumps(triage, indent=2)[:1500] + """

LOG EVIDENCE:
""" + json.dumps(log_analyst, indent=2)[:1500] + """

REPRODUCTION RESULTS:
""" + json.dumps(repro, indent=2)[:2000] + """

Respond with a JSON object containing:
{
    "root_cause": {
        "summary": "1-2 sentence root cause description",
        "detailed_explanation": "detailed technical explanation of why the bug occurs",
        "exact_location": {"file": "filename", "function": "function_name", "line_range": "start-end"},
        "buggy_code": "the exact buggy code snippet",
        "confidence": "high/medium/low"
    },
    "fix_proposal": {
        "approach": "description of the fix approach",
        "fixed_code": "the corrected code snippet",
        "files_to_modify": [{"file": "filename", "changes": "description of changes"}],
        "risk_level": "low/medium/high",
        "breaking_changes": true/false,
        "backward_compatible": true/false
    },
    "verification_plan": {
        "unit_tests_to_add": ["test description 1", "test description 2"],
        "edge_cases_to_test": [
            {"case": "description", "input": "test input", "expected_output": "expected result"}
        ],
        "regression_checks": ["check 1", "check 2"],
        "commands_to_run": ["pytest command", "other verification"]
    },
    "alternative_fixes": [
        {"approach": "alternative approach", "pros": ["pro 1"], "cons": ["con 1"]}
    ]
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
                "code_analysis": code_analysis,
                "function_detail": func_detail,
                "call_chain": call_chain
            },
            "analysis": analysis
        }
