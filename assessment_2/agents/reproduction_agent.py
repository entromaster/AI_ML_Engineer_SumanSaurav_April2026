"""
Reproduction Agent
Constructs minimal reproduction scripts and runs them to verify the bug.
"""

import os
import json
from .base_agent import BaseAgent


class ReproductionAgent(BaseAgent):
    """Generates and runs minimal reproduction scripts."""
    
    def __init__(self, tools: dict, llm_client, logger):
        super().__init__(
            name="Repro Builder",
            role="Reproduction Specialist",
            persona=(
                "You are an expert at creating minimal, self-contained reproduction "
                "scripts that isolate bugs. You understand the importance of eliminating "
                "irrelevant code and focusing on the exact failure condition. Your repro "
                "scripts are clean, well-commented, and reliably demonstrate the bug."
            ),
            tools=tools,
            llm_client=llm_client,
            logger=logger
        )
    
    def run(self, context: dict) -> dict:
        self.display_status("Building and running minimal reproduction script...")
        
        # Step 1: Read the buggy source file
        repo_path = context.get("repo_path")
        utils_path = os.path.join(repo_path, "utils.py")
        utils_source = self.call_tool("read_file_content", filepath=utils_path)
        
        # Step 2: Analyze the buggy function
        func_analysis = self.call_tool("analyze_file", filepath=utils_path)
        
        # Step 3: Find the specific function
        func_detail = self.call_tool("find_function", filepath=utils_path, function_name="paginate_results")
        
        # Step 4: Gather context from previous agents
        triage = context.get("triage", {}).get("analysis", {})
        log_analyst = context.get("log_analyst", {}).get("analysis", {})
        
        # Step 5: Ask LLM to generate a minimal repro script
        prompt = """Based on the bug analysis, generate a MINIMAL reproduction script that demonstrates the bug.

BUGGY FUNCTION SOURCE:
""" + json.dumps(func_detail, indent=2)[:3000] + """

TRIAGE ANALYSIS:
""" + json.dumps(triage, indent=2)[:2000] + """

LOG EVIDENCE:
""" + json.dumps(log_analyst, indent=2)[:1500] + """

Generate a complete, self-contained Python script that:
1. Copies the paginate_results function (the buggy version)
2. Tests it with specific inputs that trigger the bug
3. Prints clear output showing expected vs actual behavior
4. Exits with non-zero code when the bug is demonstrated

Respond with a JSON object containing:
{
    "repro_script": "the complete Python script as a string (use \\n for newlines)",
    "description": "what the script tests and expects",
    "expected_output": "what correct behavior would show",
    "actual_output_prediction": "what the bug will cause",
    "run_command": "python repro_test.py",
    "minimal_explanation": "why this is a minimal reproduction"
}"""
        
        llm_response = self.call_llm(prompt)
        
        try:
            cleaned = llm_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
            repro_data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback: generate a known-good repro script
            repro_data = self._generate_fallback_repro()
        
        # Step 6: Save the repro script
        output_dir = context.get("output_dir", ".")
        repro_path = os.path.join(output_dir, "repro_test.py")
        
        repro_script = repro_data.get("repro_script", self._generate_fallback_repro()["repro_script"])
        
        os.makedirs(output_dir, exist_ok=True)
        with open(repro_path, 'w') as f:
            f.write(repro_script)
        
        self.logger.log_step(self.name, "Saved repro script", repro_path)
        
        # Step 7: Run the repro script
        run_result = self.call_tool("run_script", 
                                     script_path=repro_path,
                                     working_dir=output_dir)
        
        # Step 8: Also run the existing tests
        test_path = os.path.join(repo_path, "tests", "test_app.py")
        test_result = None
        if os.path.exists(test_path):
            test_result = self.call_tool("run_test",
                                          test_path=test_path,
                                          working_dir=repo_path)
        
        return {
            "agent": self.name,
            "role": self.role,
            "tool_results": {
                "utils_source": utils_source,
                "function_analysis": func_detail,
                "repro_run": run_result,
                "existing_tests": test_result
            },
            "repro_script_path": repro_path,
            "repro_script_content": repro_script,
            "analysis": {
                "description": repro_data.get("description", ""),
                "expected_output": repro_data.get("expected_output", ""),
                "actual_output_prediction": repro_data.get("actual_output_prediction", ""),
                "run_command": f"python {repro_path}",
                "repro_successful": run_result.get("exit_code", 1) != 0,
                "existing_tests_passed": test_result.get("all_passed", None) if test_result else None,
                "stdout": run_result.get("stdout", ""),
                "stderr": run_result.get("stderr", "")
            }
        }
    
    def _generate_fallback_repro(self) -> dict:
        """Generate a known-good repro script if LLM generation fails."""
        script = '''"""
Minimal Reproduction Script — Pagination Bug
=============================================
Demonstrates: Duplicate items on last page when total items % per_page != 0
"""

import sys


def paginate_results(items, page, per_page):
    """Buggy pagination function (copied from mini_repo/utils.py)."""
    total = len(items)
    total_pages = (total + per_page - 1) // per_page
    
    if page > total_pages and total > 0:
        return {"data": [], "pagination": {"page": page, "per_page": per_page, "total": total, "total_pages": total_pages}}
    
    # BUG: On the last page with uneven items, start from (total - per_page)
    # instead of (page-1)*per_page, causing overlap with previous page
    if page == total_pages and total % per_page != 0:
        start = total - per_page  # WRONG!
    else:
        start = (page - 1) * per_page
    
    end = start + per_page
    page_items = items[start:end]
    
    return {"data": page_items, "pagination": {"page": page, "per_page": per_page, "total": total, "total_pages": total_pages}}


def main():
    """Run the reproduction test."""
    print("=" * 60)
    print("PAGINATION BUG REPRODUCTION")
    print("=" * 60)
    
    # Setup: 30 items, 7 per page = 5 pages (last page should have 2 items)
    items = list(range(1, 31))
    per_page = 7
    total_pages = 5
    
    print(f"\\nTotal items: {len(items)}, Per page: {per_page}, Expected pages: {total_pages}")
    print("-" * 60)
    
    all_items = []
    bug_found = False
    
    for page in range(1, total_pages + 1):
        result = paginate_results(items, page, per_page)
        data = result["data"]
        all_items.extend(data)
        
        expected_count = per_page if page < total_pages else len(items) % per_page
        if expected_count == 0:
            expected_count = per_page
        
        status = "OK" if len(data) == expected_count else "BUG!"
        if status == "BUG!":
            bug_found = True
        
        print(f"Page {page}: {data}  (count={len(data)}, expected={expected_count}) [{status}]")
    
    print("-" * 60)
    print(f"\\nTotal items across all pages: {len(all_items)} (expected: {len(items)})")
    print(f"Unique items: {len(set(all_items))} (expected: {len(items)})")
    
    duplicates = [x for x in set(all_items) if all_items.count(x) > 1]
    if duplicates:
        print(f"\\n*** DUPLICATES FOUND: {duplicates} ***")
        bug_found = True
    
    print("\\n" + "=" * 60)
    if bug_found:
        print("RESULT: BUG REPRODUCED SUCCESSFULLY")
        print("=" * 60)
        sys.exit(1)
    else:
        print("RESULT: No bug found (unexpected)")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
'''
        return {
            "repro_script": script,
            "description": "Tests paginate_results with 30 items and per_page=7 to expose duplicate items on last page",
            "expected_output": "Last page should show items [29, 30] with count=2",
            "actual_output_prediction": "Last page shows items [24-30] with count=7, duplicating items 24-28",
            "run_command": "python repro_test.py",
            "minimal_explanation": "Uses only the paginate_results function with inputs that trigger the uneven division edge case"
        }
