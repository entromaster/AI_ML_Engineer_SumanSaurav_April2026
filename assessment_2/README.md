# Assessment 2: Multi-Agent Bug Analysis System

## Overview

This system ingests a **bug report** and related **application logs**, reproduces the issue by generating a **minimal reproducible test**, and outputs a **root-cause hypothesis** plus a **patch plan**.

The system uses **Option A (Provided Mini-Repo)**: a small Flask API with an intentionally introduced pagination bug.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Orchestrator                        │
│         (Sequential Workflow with Handoffs)           │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Phase 1: Triage Agent ──→ Symptom Extraction        │
│  Phase 2: Log Analyst ──→ Evidence Gathering         │
│  Phase 3: Dependency Analyst ──→ Import Chain Check  │
│  Phase 4: Reproduction Agent ──→ Minimal Repro + Run │
│  Phase 5: Fix Planner ──→ Root Cause + Patch Plan    │
│  Phase 6: Reviewer/Critic ──→ Validate & Challenge   │
│  Phase 7: Final Synthesis ──→ Structured Output      │
│                                                      │
├──────────────────────────────────────────────────────┤
│  Tools: log_parser | file_searcher | test_runner |   │
│         code_analyzer | read_file | find_function |  │
│         trace_call_chain | run_script | run_test    │
├──────────────────────────────────────────────────────┤
│  LLM: Google Gemini 2.0 Flash                       │
└──────────────────────────────────────────────────────┘
```

## The Bug

**Mini-repo**: A Flask REST API for task management (`mini_repo/`)

**Bug**: Off-by-one pagination error in `utils.py → paginate_results()`. When the total number of items is **not evenly divisible** by `per_page`, the last page incorrectly calculates its start offset as `total - per_page` instead of `(page-1) * per_page`, causing **duplicate items** that overlap with the previous page.

## Agents (6 total)

| Agent | Role | Responsibility |
|-------|------|----------------|
| Triage Bot | Bug Triage Specialist | Parse bug report, extract symptoms, rank hypotheses |
| Log Analyzer | Log Analysis Specialist | Search logs for errors, stack traces, correlations |
| Dependency Analyst | Import Chain Analyst | Examine module dependencies and version issues |
| Repro Builder | Reproduction Specialist | Generate and execute minimal reproduction script |
| Fix Planner | Senior Debugging Engineer | Root cause analysis, patch proposal, verification plan |
| Code Reviewer | Critic & Reviewer | Challenge assumptions, verify repro minimality, edge cases |

> **Note**: Dependency Analyst is an **extra agent** beyond the minimum 5 required.

## Tools (4 categories, 9 functions)

| Tool Module | Functions | Description |
|-------------|-----------|-------------|
| `log_parser` | `parse_logs()` | Extract errors, stack traces, frequency analysis |
| `file_searcher` | `search_files()`, `read_file_content()` | Pattern matching across files |
| `test_runner` | `run_test()`, `run_script()`, `run_code_string()` | Execute tests and scripts |
| `code_analyzer` | `analyze_file()`, `find_function()`, `trace_call_chain()` | Python AST analysis |

## Input Artifacts

- **`inputs/bug_report.md`** — Structured bug report with title, description, expected/actual behavior, environment, reproduction hints
- **`inputs/logs.txt`** — Application logs with stack traces, error signatures, and red herring noise
- **`mini_repo/`** — Flask app with intentional pagination bug
  - `app.py` — API routes
  - `models.py` — Data models and DB initialization  
  - `utils.py` — Pagination utility (**bug is here**)
  - `tests/test_app.py` — Tests (2 tests expose the bug)

## Setup & Run Instructions

### Prerequisites
- Python 3.10+
- Google Gemini API key

### Installation
```bash
# From the repository root
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the repository root (or set in your environment):
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Run
```bash
cd assessment_2
python main.py
```

### Verify the Bug Manually (Optional)
```bash
# Run the existing tests to see the bug
cd assessment_2/mini_repo
python -m pytest tests/test_app.py -v
# Expected: 2 tests FAIL (test_last_page_uneven_division, test_no_duplicate_items_across_pages)

# Run the generated repro script
python assessment_2/output/repro_test.py
# Expected: Exits with code 1, showing "BUG REPRODUCED SUCCESSFULLY"
```

## Output Files

The system produces:

1. **`output/analysis.json`** — Final structured analysis (JSON)
2. **`output/repro_test.py`** — Generated minimal reproduction script
3. **`output/trace.log`** — Full trace of agent steps and tool calls

## Output Format

The final `analysis.json` contains:
```json
{
    "bug_summary": { "title": "...", "symptoms": [...], "severity": "...", "scope": "..." },
    "evidence": { "log_lines": [...], "stack_trace_excerpts": [...], "test_failures": [...] },
    "reproduction": { "steps": [...], "repro_artifact_path": "...", "command_to_run": "..." },
    "root_cause_hypothesis": { "summary": "...", "confidence": "high/medium/low", "buggy_code_location": {...} },
    "patch_plan": { "files_impacted": [...], "approach": "...", "fixed_code_snippet": "..." },
    "validation_plan": { "tests_to_add": [...], "regression_checks": [...] },
    "open_questions": [...],
    "metadata": { "generated_at": "...", "agents_consulted": 6, "tools_used": [...] }
}
```

## Trace Logs

Traces are saved to `output/trace.log`. Each entry shows:
- `[elapsed_time] [agent_name] EVENT_TYPE: details`
- Event types: `STEP`, `TOOL_CALL`, `TOOL_RESULT`, `LLM_CALL`, `LLM_RESPONSE`, `ERROR`
