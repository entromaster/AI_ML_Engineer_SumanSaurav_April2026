"""
Assessment 1: Multi-Agent War Room — Product Launch Decision System
==================================================================

This system simulates a cross-functional war room during a product launch.
Multiple AI agents analyze metrics, user feedback, and release context to
produce a structured decision: Proceed / Pause / Roll Back.

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

from orchestrator import WarRoomOrchestrator

console = Console(force_terminal=True)


def main():
    """Main entry point for the War Room decision system."""
    
    # Banner
    console.print(Panel(
        "[bold bright_white]"
        "PURPLEMERIT MULTI-AGENT WAR ROOM SYSTEM\n"
        "Product Launch Decision Engine"
        "[/bold bright_white]\n\n"
        "Company: PurpleMerit Technologies\n"
        "Feature: Smart Insights v2.4.0\n"
        f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        "Agents: 6 (Data Analyst, Marketing, Customer Success, Engineering, PM, Risk)\n"
        "Tools: 4 (Metric Analyzer, Sentiment Analyzer, Trend Comparator, Threshold Checker)",
        title="[bold]Assessment 1[/bold]",
        border_style="bright_magenta",
        padding=(1, 2)
    ))
    
    # Load environment variables
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GOOGLE_API_KEY")
    
    if gemini_key:
        provider = "gemini"
        api_key = gemini_key
        console.print("[green][OK] Google Gemini API key loaded successfully[/green]")
    elif openai_key:
        provider = "openai"
        api_key = openai_key
        console.print("[green][OK] OpenAI API key loaded successfully[/green]")
    else:
        console.print("[bold red]ERROR: Neither OPENAI_API_KEY nor GOOGLE_API_KEY found![/bold red]")
        console.print("Please set an API key in your .env file or environment variables.")
        sys.exit(1)
    
    # Setup paths
    base_dir = Path(__file__).resolve().parent
    data_dir = str(base_dir / "data")
    output_dir = str(base_dir / "output")
    
    # Verify data files exist
    required_files = ["metrics.json", "user_feedback.json", "release_notes.md"]
    for fname in required_files:
        fpath = os.path.join(data_dir, fname)
        if not os.path.exists(fpath):
            console.print(f"[bold red]ERROR: Missing data file: {fpath}[/bold red]")
            sys.exit(1)
    
    console.print("[green][OK] All data files verified[/green]")
    console.print()
    
    # Run the war room
    try:
        orchestrator = WarRoomOrchestrator(data_dir, output_dir, provider, api_key)
        decision = orchestrator.run()
        
        # Pretty-print the final decision
        console.print(f"\n{'═'*60}")
        console.print("[bold bright_green]FINAL STRUCTURED OUTPUT[/bold bright_green]")
        console.print(f"{'═'*60}\n")
        
        console.print_json(json.dumps(decision, indent=2))
        
        console.print(f"\n{'═'*60}")
        console.print("[bold green][OK] War room complete. Files saved:[/bold green]")
        console.print(f"  Decision: {output_dir}/decision.json")
        console.print(f"  Trace Log: {output_dir}/trace.log")
        console.print(f"{'='*60}")
        
    except Exception as e:
        console.print(f"\n[bold red]ERROR during war room execution:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
