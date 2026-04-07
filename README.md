# AI/ML Engineer Assessment — Suman Saurav

## 📋 Overview

This repository contains solutions for **both** PurpleMerit AI/ML Engineer assessments, implemented using **Python** with a **custom multi-agent orchestration framework** (no third-party agent frameworks) and **Google Gemini 2.0 Flash** as the LLM backend.

---

## Assessment 1: Multi-Agent War Room — Product Launch Decision

📁 **Directory**: [`assessment_1/`](./assessment_1/)

A multi-agent system that simulates a cross-functional **war room** during a product launch. Six AI agents analyze metrics, user feedback, and release notes to produce a structured decision: **Proceed / Pause / Roll Back**.

**Key Features:**
- 6 agents (4 required + 2 extra): Data Analyst, Marketing, Customer Success, Engineering, PM, Risk/Critic
- 4 tools: Metric Analyzer, Sentiment Analyzer, Trend Comparator, Threshold Checker
- Custom orchestrator with state-machine workflow
- Full traceability via trace logs

▶️ **Run**: `cd assessment_1 && python main.py`

📄 **[Full README](./assessment_1/README.md)**

---

## Assessment 2: Multi-Agent Bug Analysis System

📁 **Directory**: [`assessment_2/`](./assessment_2/)

A multi-agent system that ingests a bug report and logs, reproduces the issue with a minimal script, and outputs a root-cause hypothesis plus patch plan. Includes a mini Flask repo with an intentional pagination bug.

**Key Features:**
- 6 agents (5 required + 1 extra): Triage, Log Analyst, Dependency, Reproduction, Fix Planner, Reviewer
- 4 tool categories (9 functions): Log Parser, File Searcher, Test Runner, Code Analyzer
- Generates and executes a minimal reproduction script
- Full traceability via trace logs

▶️ **Run**: `cd assessment_2 && python main.py`

📄 **[Full README](./assessment_2/README.md)**

---

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### Setup
```bash
# 1. Clone the repository
git clone <repo-url>
cd "AI ML Engineer_SumanSaurav_April2026"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your API key
# Create a .env file in the root directory:
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### Run Assessment 1 (War Room)
```bash
cd assessment_1
python main.py
# Output: output/decision.json + output/trace.log
```

### Run Assessment 2 (Bug Analysis)
```bash
cd assessment_2
python main.py
# Output: output/analysis.json + output/repro_test.py + output/trace.log
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | ✅ Yes |

Create a `.env` file in the repository root or export in your shell. See `.env.example` for the template.

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| LLM | Google Gemini 2.0 Flash |
| LLM SDK | `google-generativeai` |
| Agent Framework | **Custom** (no LangGraph/CrewAI/AutoGen) |
| Console Output | Rich (beautiful terminal output) |
| Data Analysis | NumPy |
| Testing | pytest |
| Web Framework (Assessment 2) | Flask |

---

## Repository Structure

```
AI ML Engineer_SumanSaurav_April2026/
├── README.md                    ← You are here
├── requirements.txt             ← Shared dependencies
├── .env.example                 ← API key template
├── .gitignore
│
├── assessment_1/                ← War Room system
│   ├── README.md
│   ├── main.py                  ← Entry point
│   ├── orchestrator.py          ← Agent workflow coordinator
│   ├── trace_logger.py          ← Structured logging
│   ├── agents/                  ← 6 agent implementations
│   ├── tools/                   ← 4 analytical tools
│   └── data/                    ← Mock dashboard data
│
└── assessment_2/                ← Bug Analysis system
    ├── README.md
    ├── main.py                  ← Entry point
    ├── orchestrator.py          ← Agent workflow coordinator
    ├── trace_logger.py          ← Structured logging
    ├── agents/                  ← 6 agent implementations
    ├── tools/                   ← 4 tool categories (9 functions)
    ├── mini_repo/               ← Flask app with intentional bug
    └── inputs/                  ← Bug report + logs
```

---

## Author

**Suman Saurav**  
April 2026
