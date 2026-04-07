# Assessment 1: Multi-Agent War Room — Product Launch Decision System

## Overview

This system simulates a cross-functional **war room** during the launch of PurpleMerit's "Smart Insights v2.4.0" feature. Multiple AI agents analyze a mock dashboard (metrics + user feedback) and produce a structured launch decision: **Proceed / Pause / Roll Back**, along with a concise action plan.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Orchestrator                        │
│         (Sequential State Machine Workflow)           │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Phase 1: Data Analyst ──→ Quantitative Analysis     │
│  Phase 2: Marketing ──→ Sentiment & Perception       │
│  Phase 3: Customer Success ──→ Customer Health       │
│  Phase 4: Engineering ──→ Technical Health            │
│  Phase 5: PM ──→ Decision Framing                    │
│  Phase 6: Risk/Critic ──→ Challenge & Risk Review    │
│  Phase 7: Final Synthesis ──→ Structured Decision    │
│                                                      │
├──────────────────────────────────────────────────────┤
│  Tools: metric_analyzer | sentiment_analyzer |       │
│         trend_comparator | threshold_checker         │
├──────────────────────────────────────────────────────┤
│  LLM: Google Gemini 2.0 Flash                       │
└──────────────────────────────────────────────────────┘
```

## Agents (6 total)

| Agent | Role | Responsibility |
|-------|------|----------------|
| Alex Chen | Senior Data Analyst | Metrics analysis, trend detection, anomaly detection |
| Priya Sharma | Head of Marketing | User sentiment, brand perception, communication plan |
| James Rodriguez | Customer Success Director | Customer health, churn risk, at-risk segments |
| Marcus Williams | Engineering Lead/SRE | System stability, crash rates, latency, incident assessment |
| Sarah Chen | VP of Product | Decision framing, go/no-go synthesis |
| Aisha Okafor | Risk Manager | Challenges assumptions, builds risk register |

> **Note**: Customer Success and Engineering are **extra agents** beyond the minimum 4 required.

## Tools (4 total)

| Tool | Function | Description |
|------|----------|-------------|
| `metric_analyzer` | `analyze_all_metrics()` | Computes stats, trend (linear regression), anomaly detection (z-score) |
| `sentiment_analyzer` | `analyze_feedback()` | Sentiment distribution, theme extraction, critical issues |
| `trend_comparator` | `compare_all_metrics()` | Pre/post launch comparison using Cohen's d effect size |
| `threshold_checker` | `check_all_thresholds()` | Validates metrics against success criteria from release notes |

## Mock Data

- **`data/metrics.json`** — 14-day time series with 9 metrics (7 pre-launch, 7 post-launch)
- **`data/user_feedback.json`** — 35 feedback entries (positive/negative/neutral mix)
- **`data/release_notes.md`** — Feature description, known issues, success criteria

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
cd assessment_1
python main.py
```

### Expected Output
The system produces:
1. **`output/decision.json`** — Final structured decision (JSON)
2. **`output/trace.log`** — Full trace of agent steps and tool calls

## Output Format

The final `decision.json` contains:
```json
{
    "decision": "Proceed | Pause | Roll Back",
    "rationale": { "summary": "...", "key_metric_drivers": [...], "feedback_summary": {...} },
    "risk_register": [{ "risk_id": "R1", "description": "...", "mitigation": "..." }],
    "action_plan_24_48h": [{ "action_id": "A1", "action": "...", "owner": "...", "timeline": "..." }],
    "communication_plan": { "internal": [...], "external": [...] },
    "confidence_score": "high/medium/low",
    "confidence_factors": { "supporting": [...], "undermining": [...] },
    "agent_consensus": { "data_analyst": "...", "pm": "...", ... },
    "metadata": { "generated_at": "...", "agents_consulted": 6, "tools_used": [...] }
}
```

## Trace Logs

Traces are saved to `output/trace.log` and include:
- Agent step transitions
- Tool invocations with arguments
- LLM API calls with prompt previews
- LLM responses
- Final decision

**How to read**: Each line is prefixed with `[elapsed_time] [agent_name] EVENT_TYPE: details`
