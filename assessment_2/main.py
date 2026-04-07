"""
Assessment 2: Multi-Agent Bug Analysis System
==============================================

This system ingests a bug report and related logs, reproduces the issue
by generating a minimal reproducible test, and outputs a root-cause
hypothesis plus a patch plan.

Usage:
    python main.py

Ensure GOOGLE_API_KEY is set in your environment or .env file.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from orchestrator import BugAnalysisOrchestrator

console = Console(force_terminal=True)


def main():
    """Main entry point for the Bug Analysis system."""
    
    # Banner
    console.print(Panel(
        "[bold bright_white]"
        "PURPLEMERIT MULTI-AGENT BUG ANALYSIS SYSTEM\n"
        "Automated Bug Investigation Engine"
        "[/bold bright_white]\n\n"
        "Input: Bug report + Logs + Mini-repo with intentional bug\n"
        f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        "Agents: 6 (Triage, Log Analyst, Dependency, Reproduction, Fix Planner, Reviewer)\n"
        "Tools: 9 (Log Parser, File Searcher, Test Runner, Code Analyzer, etc.)",
        title="[bold]Assessment 2[/bold]",
        border_style="bright_red",
        padding=(1, 2)
    ))
    
    # Load environment variables
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GOOGLE_API_KEY")
    
    if openai_key:
        provider = "openai"
        api_key = openai_key
        console.print("[green][OK] OpenAI API key loaded successfully[/green]")
    elif gemini_key:
        provider = "gemini"
        api_key = gemini_key
        console.print("[green][OK] Google Gemini API key loaded successfully[/green]")
    else:
        console.print("[bold red]ERROR: Neither OPENAI_API_KEY nor GOOGLE_API_KEY found![/bold red]")
        console.print("Please set an API key in your .env file or environment variables.")
        sys.exit(1)
    
    # Setup paths
    base_dir = Path(__file__).resolve().parent
    repo_path = str(base_dir / "mini_repo")
    inputs_dir = str(base_dir / "inputs")
    output_dir = str(base_dir / "output")
    
    # Verify input files exist
    required_files = [
        (inputs_dir, "bug_report.md"),
        (inputs_dir, "logs.txt"),
        (repo_path, "app.py"),
        (repo_path, "utils.py"),
        (repo_path, "models.py")
    ]
    
    for dir_path, fname in required_files:
        fpath = os.path.join(dir_path, fname)
        if not os.path.exists(fpath):
            console.print(f"[bold red]ERROR: Missing file: {fpath}[/bold red]")
            sys.exit(1)
    
    console.print("[green][OK] All input files verified[/green]")
    console.print()
    
    # Run the bug analysis
    try:
        orchestrator = BugAnalysisOrchestrator(repo_path, inputs_dir, output_dir, provider, api_key)
        analysis = orchestrator.run()
        
        # Pretty-print the final output
        console.print(f"\n{'='*60}")
        console.print("[bold bright_green]FINAL STRUCTURED OUTPUT[/bold bright_green]")
        console.print(f"{'='*60}\n")
        
        console.print_json(json.dumps(analysis, indent=2))
        
        console.print(f"\n{'='*60}")
        console.print("[bold green][OK] Bug analysis complete. Files saved:[/bold green]")
        console.print(f"  Analysis: {output_dir}/analysis.json")
        console.print(f"  Repro Script: {output_dir}/repro_test.py")
        console.print(f"  Trace Log: {output_dir}/trace.log")
        console.print(f"{'='*60}")
        
    except Exception as e:
        console.print(f"\n[bold red]ERROR during bug analysis:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
