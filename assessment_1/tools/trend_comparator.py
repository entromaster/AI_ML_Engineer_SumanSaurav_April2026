"""
Trend Comparator Tool
Compares metric values across two time windows (pre-launch vs post-launch)
to identify significant changes.
"""

import json
import numpy as np
from typing import Any


def load_metrics(filepath: str) -> dict:
    """Load metrics data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def compare_windows(pre_values: list[float], post_values: list[float], metric_name: str) -> dict:
    """
    Compare two time windows and determine if the change is significant.
    Uses Cohen's d for effect size measurement.
    """
    pre = np.array(pre_values)
    post = np.array(post_values)
    
    pre_mean = float(np.mean(pre))
    post_mean = float(np.mean(post))
    
    # Cohen's d for effect size
    pooled_std = float(np.sqrt((np.std(pre)**2 + np.std(post)**2) / 2))
    cohens_d = (post_mean - pre_mean) / pooled_std if pooled_std > 0 else 0
    
    # Determine significance based on effect size
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        significance = "negligible"
    elif abs_d < 0.5:
        significance = "small"
    elif abs_d < 0.8:
        significance = "medium"
    else:
        significance = "large"
    
    pct_change = ((post_mean - pre_mean) / pre_mean * 100) if pre_mean != 0 else 0
    
    return {
        "metric": metric_name,
        "pre_launch_mean": round(pre_mean, 4),
        "post_launch_mean": round(post_mean, 4),
        "absolute_change": round(post_mean - pre_mean, 4),
        "pct_change": round(pct_change, 2),
        "cohens_d": round(cohens_d, 4),
        "effect_size": significance,
        "direction": "improved" if pct_change > 0 else "degraded" if pct_change < 0 else "unchanged"
    }


def compare_all_metrics(filepath: str) -> dict:
    """
    Tool entry point: Compare pre-launch vs post-launch for all metrics.
    Returns comparison results with significance analysis.
    """
    raw = load_metrics(filepath)
    data = raw["metrics"]["data"]
    launch_index = 7  # Day 8 is launch day (0-indexed)
    
    metric_keys = [
        "signup_conversion_pct",
        "dau",
        "d1_retention_pct",
        "d7_retention_pct",
        "crash_rate_pct",
        "api_latency_p95_ms",
        "payment_success_rate_pct",
        "support_ticket_volume"
    ]
    
    # Define which direction is "good" for each metric
    higher_is_better = {
        "signup_conversion_pct": True,
        "dau": True,
        "d1_retention_pct": True,
        "d7_retention_pct": True,
        "crash_rate_pct": False,
        "api_latency_p95_ms": False,
        "payment_success_rate_pct": True,
        "support_ticket_volume": False
    }
    
    comparisons = []
    alerts = []
    
    for key in metric_keys:
        pre_values = [d[key] for d in data[:launch_index]]
        post_values = [d[key] for d in data[launch_index:]]
        
        comparison = compare_windows(pre_values, post_values, key)
        
        # Determine health status
        is_higher_better = higher_is_better.get(key, True)
        pct = comparison["pct_change"]
        
        if is_higher_better:
            health = "healthy" if pct >= -2 else "warning" if pct >= -10 else "critical"
        else:
            health = "healthy" if pct <= 2 else "warning" if pct <= 50 else "critical"
        
        comparison["health_status"] = health
        comparisons.append(comparison)
        
        if health in ("warning", "critical"):
            alerts.append({
                "metric": key,
                "status": health,
                "pct_change": comparison["pct_change"],
                "effect_size": comparison["effect_size"]
            })
    
    return {
        "tool": "trend_comparator",
        "launch_date": raw["metrics"]["launch_date"],
        "pre_launch_window": f"{data[0]['date']} to {data[launch_index-1]['date']}",
        "post_launch_window": f"{data[launch_index]['date']} to {data[-1]['date']}",
        "comparisons": comparisons,
        "alerts": sorted(alerts, key=lambda x: x["status"] == "critical", reverse=True),
        "summary": {
            "total_metrics": len(comparisons),
            "healthy": sum(1 for c in comparisons if c["health_status"] == "healthy"),
            "warning": sum(1 for c in comparisons if c["health_status"] == "warning"),
            "critical": sum(1 for c in comparisons if c["health_status"] == "critical")
        }
    }
