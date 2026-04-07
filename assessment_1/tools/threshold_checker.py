"""
Threshold Checker Tool
Checks metrics against predefined success criteria from release notes.
Returns pass/fail status for each criterion.
"""

import json
import numpy as np
from typing import Any


def load_metrics(filepath: str) -> dict:
    """Load metrics data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


# Success criteria from release notes
SUCCESS_CRITERIA = {
    "signup_conversion_pct": {
        "description": "Signup conversion rate: no more than 5% degradation vs. baseline",
        "type": "max_degradation_pct",
        "threshold": 5.0,
        "higher_is_better": True
    },
    "crash_rate_pct": {
        "description": "Crash rate: must remain below 1.0%",
        "type": "absolute_max",
        "threshold": 1.0,
        "higher_is_better": False
    },
    "api_latency_p95_ms": {
        "description": "API latency (p95): must remain below 300ms",
        "type": "absolute_max",
        "threshold": 300.0,
        "higher_is_better": False
    },
    "payment_success_rate_pct": {
        "description": "Payment success rate: must remain above 99.0%",
        "type": "absolute_min",
        "threshold": 99.0,
        "higher_is_better": True
    },
    "d1_retention_pct": {
        "description": "D1 retention: no more than 3 percentage point drop vs. baseline",
        "type": "max_degradation_pp",
        "threshold": 3.0,
        "higher_is_better": True
    },
    "support_ticket_volume": {
        "description": "Support ticket volume: no more than 30% increase vs. baseline",
        "type": "max_increase_pct",
        "threshold": 30.0,
        "higher_is_better": False
    }
}


def check_threshold(metric_name: str, pre_launch_values: list[float], 
                     post_launch_values: list[float]) -> dict:
    """
    Check a single metric against its success criterion.
    Returns detailed pass/fail analysis.
    """
    criteria = SUCCESS_CRITERIA.get(metric_name)
    if not criteria:
        return {"metric": metric_name, "status": "no_criteria", "message": "No success criteria defined"}
    
    pre_mean = float(np.mean(pre_launch_values))
    post_mean = float(np.mean(post_launch_values))
    latest_value = post_launch_values[-1] if post_launch_values else 0
    
    result = {
        "metric": metric_name,
        "criteria_description": criteria["description"],
        "baseline_mean": round(pre_mean, 2),
        "current_mean": round(post_mean, 2),
        "latest_value": round(latest_value, 2)
    }
    
    check_type = criteria["type"]
    threshold = criteria["threshold"]
    
    if check_type == "max_degradation_pct":
        actual_degradation = ((pre_mean - post_mean) / pre_mean * 100) if pre_mean != 0 else 0
        result["actual_degradation_pct"] = round(actual_degradation, 2)
        result["threshold"] = threshold
        result["passed"] = actual_degradation <= threshold
        result["margin"] = round(threshold - actual_degradation, 2)
        
    elif check_type == "absolute_max":
        result["latest_value"] = round(latest_value, 2)
        result["threshold"] = threshold
        result["passed"] = latest_value <= threshold
        result["margin"] = round(threshold - latest_value, 2)
        result["days_exceeding"] = sum(1 for v in post_launch_values if v > threshold)
        
    elif check_type == "absolute_min":
        result["latest_value"] = round(latest_value, 2)
        result["threshold"] = threshold
        result["passed"] = latest_value >= threshold
        result["margin"] = round(latest_value - threshold, 2)
        result["days_below"] = sum(1 for v in post_launch_values if v < threshold)
        
    elif check_type == "max_degradation_pp":
        actual_drop = pre_mean - post_mean
        result["actual_drop_pp"] = round(actual_drop, 2)
        result["threshold"] = threshold
        result["passed"] = actual_drop <= threshold
        result["margin"] = round(threshold - actual_drop, 2)
        
    elif check_type == "max_increase_pct":
        actual_increase = ((post_mean - pre_mean) / pre_mean * 100) if pre_mean != 0 else 0
        result["actual_increase_pct"] = round(actual_increase, 2)
        result["threshold"] = threshold
        result["passed"] = actual_increase <= threshold
        result["margin"] = round(threshold - actual_increase, 2)
    
    result["severity"] = "passing" if result.get("passed", False) else (
        "critical" if abs(result.get("margin", 0)) > threshold * 0.5 else "warning"
    )
    
    return result


def check_all_thresholds(filepath: str) -> dict:
    """
    Tool entry point: Check all metrics against success criteria.
    Returns comprehensive pass/fail analysis.
    """
    raw = load_metrics(filepath)
    data = raw["metrics"]["data"]
    launch_index = 7
    
    results = []
    passed_count = 0
    failed_count = 0
    
    for metric_name in SUCCESS_CRITERIA:
        pre_values = [d[metric_name] for d in data[:launch_index]]
        post_values = [d[metric_name] for d in data[launch_index:]]
        
        check = check_threshold(metric_name, pre_values, post_values)
        results.append(check)
        
        if check.get("passed"):
            passed_count += 1
        else:
            failed_count += 1
    
    overall_pass = failed_count == 0
    
    return {
        "tool": "threshold_checker",
        "success_criteria_source": "Release Notes v2.4.0",
        "results": results,
        "summary": {
            "total_criteria": len(results),
            "passed": passed_count,
            "failed": failed_count,
            "overall_status": "PASS" if overall_pass else "FAIL",
            "failed_metrics": [r["metric"] for r in results if not r.get("passed")],
            "critical_failures": [r["metric"] for r in results if r.get("severity") == "critical"]
        }
    }
