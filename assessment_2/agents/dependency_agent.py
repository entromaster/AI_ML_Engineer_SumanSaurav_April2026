"""
Dependency Analyst Agent (Extra Agent)
Checks if the buggy code has external dependencies or version-related issues.
"""

import json
import os
from .base_agent import BaseAgent


class DependencyAgent(BaseAgent):
    """Analyzes code dependencies and import chains for potential issues."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Dependency Analyst",
            role="Dependency & Import Chain Analyst",
            persona=(
                "You examine code dependencies, import chains, and version compatibility. "
                "You check if the bug could be related to a dependency update, "
                "a missing import, or a version mismatch. You trace how modules interact."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Analyzing dependencies and import chains...")
        
        repo_path = context.get("repo_path")
        
        # Analyze all Python files in the repo
        analyses = {}
        for fname in ["app.py", "models.py", "utils.py"]:
            filepath = os.path.join(repo_path, fname)
            if os.path.exists(filepath):
                analyses[fname] = self.call_tool("analyze_file", filepath=filepath)
        
        # Search for import statements
        import_search = self.call_tool("search_files",
                                        search_path=repo_path,
                                        pattern="import|from .* import",
                                        file_glob="*.py")
        
        prompt = """Analyze the dependency structure and import chains in this mini-repo.

FILE ANALYSES:
""" + json.dumps(analyses, indent=2)[:4000] + """

IMPORT SEARCH:
""" + json.dumps(import_search, indent=2)[:2000] + """

Respond with a JSON object containing:
{
    "summary": "1-2 sentence dependency assessment",
    "import_chain": {
        "app.py": {"imports": ["list of imports"], "depends_on": ["files"]},
        "utils.py": {"imports": ["list of imports"], "depends_on": ["files"]},
        "models.py": {"imports": ["list of imports"], "depends_on": ["files"]}
    },
    "dependency_issues": [
        {"issue": "description", "severity": "high/medium/low", "related_to_bug": true/false}
    ],
    "version_concerns": ["concern 1 if any"],
    "isolation_assessment": "Can the bug be isolated to a single module? Yes/No + explanation"
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
                "file_analyses": analyses,
                "import_search": import_search
            },
            "analysis": analysis
        }
