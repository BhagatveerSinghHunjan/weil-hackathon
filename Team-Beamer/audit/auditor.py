from datetime import datetime, timezone
from typing import Any


def audit_step(state: dict[str, Any], step_name: str) -> dict[str, Any]:
    """
    Deterministic integrity auditor.

    Produces repeatable checks for:
    - workflow control integrity
    - financial sanity constraints
    - termination safety
    """

    checks: list[str] = []
    anomaly_flag = False

    if step_name == "Planner Decision":
        next_action = state.get("next_action")
        allowed = {
            "run_financial_tool",
            "run_unit_tool",
            "run_business_tool",
            "run_aggregation_tool",
            "finalize",
            "abort",
        }
        if next_action not in allowed:
            anomaly_flag = True
            checks.append(f"unexpected_next_action:{next_action}")
        else:
            checks.append(f"planner_action:{next_action}")

    if state.get("financial_result"):
        runway = float(state["financial_result"].get("runway_months", 0.0))
        if runway < 0:
            anomaly_flag = True
            checks.append("negative_runway")
        elif runway < 3:
            checks.append("low_runway_warning")

    if state.get("iteration_count", 0) > state.get("max_iterations", 0):
        anomaly_flag = True
        checks.append("iteration_limit_exceeded")

    transparency_score = 100
    if anomaly_flag:
        transparency_score = 70
    elif any("warning" in c for c in checks):
        transparency_score = 85

    audit_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": step_name,
        "transparency_score": transparency_score,
        "anomaly_flag": anomaly_flag,
        "checks": checks,
    }

    if "audit_logs" not in state:
        state["audit_logs"] = []

    state["audit_logs"].append(audit_entry)
    return state
