"""
Sentiment Analyzer Tool
Analyzes user feedback for sentiment distribution, theme extraction,
and key issue identification.
"""

import json
import re
from collections import Counter
from typing import Any


def load_feedback(filepath: str) -> list[dict]:
    """Load user feedback from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data["entries"]


def compute_sentiment_distribution(entries: list[dict]) -> dict:
    """Compute distribution of sentiment across feedback entries."""
    sentiments = [e["sentiment"] for e in entries]
    counter = Counter(sentiments)
    total = len(sentiments)
    
    return {
        "total_entries": total,
        "positive": {"count": counter.get("positive", 0), "pct": round(counter.get("positive", 0) / total * 100, 1)},
        "negative": {"count": counter.get("negative", 0), "pct": round(counter.get("negative", 0) / total * 100, 1)},
        "neutral": {"count": counter.get("neutral", 0), "pct": round(counter.get("neutral", 0) / total * 100, 1)}
    }


def extract_themes(entries: list[dict]) -> dict:
    """
    Extract common themes/issues from feedback using keyword matching.
    Returns grouped themes with counts and sample feedback.
    """
    theme_patterns = {
        "crash": r"\b(crash|crashes|crashing|oom|out of memory)\b",
        "slow_performance": r"\b(slow|loading|latency|timeout|takes forever|seconds|lag)\b",
        "payment_failure": r"\b(payment|pay|subscribe|subscription|checkout|billing|PM-4021)\b",
        "positive_feature": r"\b(love|great|amazing|excellent|brilliant|incredible|outstanding|impressed|game changer|best)\b",
        "ui_issues": r"\b(render|display|overlap|layout|ui|interface|tablet|ipad)\b",
        "export_issues": r"\b(export|pdf|csv|report|download)\b",
        "onboarding": r"\b(tutorial|get started|how to|confus|unclear)\b",
        "api_errors": r"\b(api|error|403|forbidden|internal server|timeout)\b"
    }
    
    themes = {}
    for theme_name, pattern in theme_patterns.items():
        matching = []
        for entry in entries:
            if re.search(pattern, entry["text"], re.IGNORECASE):
                matching.append({
                    "id": entry["id"],
                    "sentiment": entry["sentiment"],
                    "channel": entry["channel"],
                    "text": entry["text"][:150]
                })
        if matching:
            themes[theme_name] = {
                "count": len(matching),
                "entries": matching
            }
    
    return themes


def analyze_by_channel(entries: list[dict]) -> dict:
    """Analyze feedback distribution by channel."""
    channels = {}
    for entry in entries:
        channel = entry["channel"]
        if channel not in channels:
            channels[channel] = {"total": 0, "positive": 0, "negative": 0, "neutral": 0}
        channels[channel]["total"] += 1
        channels[channel][entry["sentiment"]] += 1
    return channels


def identify_critical_issues(entries: list[dict]) -> list[dict]:
    """
    Identify critical issues: negative feedback that appears repeatedly
    or mentions severe problems (crash, payment, data loss).
    """
    critical_keywords = ["crash", "payment fail", "error", "can't access", "data loss", "broken", "unusable"]
    critical = []
    
    for entry in entries:
        if entry["sentiment"] == "negative":
            text_lower = entry["text"].lower()
            severity = "medium"
            for keyword in critical_keywords:
                if keyword in text_lower:
                    severity = "high"
                    break
            critical.append({
                "id": entry["id"],
                "channel": entry["channel"],
                "severity": severity,
                "text": entry["text"][:200],
                "timestamp": entry["timestamp"]
            })
    
    return sorted(critical, key=lambda x: x["severity"] == "high", reverse=True)


def compute_sentiment_trend(entries: list[dict]) -> list[dict]:
    """
    Compute sentiment trend over time by grouping entries by date.
    """
    daily = {}
    for entry in entries:
        date = entry["timestamp"][:10]
        if date not in daily:
            daily[date] = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
        daily[date][entry["sentiment"]] += 1
        daily[date]["total"] += 1
    
    trend = []
    for date in sorted(daily.keys()):
        d = daily[date]
        trend.append({
            "date": date,
            "total": d["total"],
            "positive_pct": round(d["positive"] / d["total"] * 100, 1) if d["total"] > 0 else 0,
            "negative_pct": round(d["negative"] / d["total"] * 100, 1) if d["total"] > 0 else 0,
            "net_sentiment": d["positive"] - d["negative"]
        })
    
    return trend


def analyze_feedback(filepath: str) -> dict:
    """
    Tool entry point: Comprehensive feedback analysis.
    Returns sentiment distribution, themes, critical issues, and trends.
    """
    entries = load_feedback(filepath)
    
    return {
        "tool": "sentiment_analyzer",
        "total_feedback_entries": len(entries),
        "sentiment_distribution": compute_sentiment_distribution(entries),
        "themes": extract_themes(entries),
        "channel_analysis": analyze_by_channel(entries),
        "critical_issues": identify_critical_issues(entries),
        "sentiment_trend": compute_sentiment_trend(entries)
    }
