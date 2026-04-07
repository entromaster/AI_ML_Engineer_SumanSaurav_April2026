"""
Metric Analyzer Tool
Provides metric aggregation, trend analysis, and anomaly detection
for the War Room decision-making system.
"""

import json
import numpy as np
from typing import Any


def load_metrics(filepath: str) -> dict:
    """Load metrics data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def compute_summary_stats(values: list[float]) -> dict:
    """Compute summary statistics for a list of metric values."""
    arr = np.array(values)
    return {
        "mean": round(float(np.mean(arr)), 4),
        "median": round(float(np.median(arr)), 4),
        "std": round(float(np.std(arr)), 4),
        "min": round(float(np.min(arr)), 4),
        "max": round(float(np.max(arr)), 4),
        "range": round(float(np.max(arr) - np.min(arr)), 4),
        "count": len(values)
    }


def detect_anomalies(values: list[float], z_threshold: float = 2.0) -> list[dict]:
    """
    Detect anomalies using z-score method.
    Returns list of anomalous data points with their index and z-score.
    """
    arr = np.array(values)
    mean = np.mean(arr)
    std = np.std(arr)
    
    if std == 0:
        return []
    
    anomalies = []
    for i, val in enumerate(values):
        z_score = abs((val - mean) / std)
        if z_score > z_threshold:
            anomalies.append({
                "index": i,
                "value": round(val, 4),
                "z_score": round(z_score, 4),
                "direction": "above" if val > mean else "below"
            })
    return anomalies


def compute_trend(values: list[float]) -> dict:
    """
    Compute linear trend (slope) using least squares regression.
    Returns slope, direction, and percentage change.
    """
    if len(values) < 2:
        return {"slope": 0, "direction": "stable", "pct_change": 0}
    
    x = np.arange(len(values))
    coeffs = np.polyfit(x, values, 1)
    slope = coeffs[0]
    
    first_val = values[0]
    last_val = values[-1]
    pct_change = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
    
    if abs(pct_change) < 2:
        direction = "stable"
    elif pct_change > 0:
        direction = "increasing"
    else:
        direction = "decreasing"
    
    return {
        "slope": round(float(slope), 4),
        "direction": direction,
        "pct_change": round(float(pct_change), 2),
        "first_value": round(first_val, 4),
        "last_value": round(last_val, 4)
    }


def analyze_metric(metric_name: str, data: list[dict], launch_day_index: int = 7) -> dict:
    """
    Comprehensive analysis of a single metric.
    Splits into pre-launch and post-launch periods.
    """
    values = []
    for entry in data:
        if metric_name == "feature_adoption_funnel":
            funnel = entry.get(metric_name, {})
            values.append(funnel.get("completed", 0))
        else:
            values.append(entry.get(metric_name, 0))
    
    pre_launch = values[:launch_day_index]
    post_launch = values[launch_day_index:]
    
    result = {
        "metric_name": metric_name,
        "overall": compute_summary_stats(values),
        "trend_overall": compute_trend(values),
        "pre_launch": {
            "stats": compute_summary_stats(pre_launch),
            "trend": compute_trend(pre_launch)
        },
        "post_launch": {
            "stats": compute_summary_stats(post_launch),
            "trend": compute_trend(post_launch)
        },
        "anomalies": detect_anomalies(values),
        "pre_vs_post_change": {
            "mean_change_pct": round(
                (np.mean(post_launch) - np.mean(pre_launch)) / np.mean(pre_launch) * 100
                if np.mean(pre_launch) != 0 else 0, 2
            )
        }
    }
    return result


def analyze_all_metrics(filepath: str) -> dict:
    """
    Tool entry point: Analyze all metrics from the dashboard data.
    Returns comprehensive analysis for each metric.
    """
    raw = load_metrics(filepath)
    data = raw["metrics"]["data"]
    launch_date = raw["metrics"]["launch_date"]
    
    metric_keys = [
        "signup_conversion_pct",
        "dau",
        "d1_retention_pct",
        "d7_retention_pct",
        "crash_rate_pct",
        "api_latency_p95_ms",
        "payment_success_rate_pct",
        "support_ticket_volume",
        "feature_adoption_funnel"
    ]
    
    results = {
        "tool": "metric_analyzer",
        "launch_date": launch_date,
        "analysis_period": f"{data[0]['date']} to {data[-1]['date']}",
        "total_data_points": len(data),
        "metrics": {}
    }
    
    for key in metric_keys:
        results["metrics"][key] = analyze_metric(key, data)
    
    return results
