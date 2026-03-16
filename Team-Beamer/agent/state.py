from typing import Dict, List, Optional, TypedDict


class AgentState(TypedDict):
    # Input
    mode: str
    startup_data: Dict

    # Tool Outputs
    financial_result: Optional[Dict]
    unit_result: Optional[Dict]
    business_result: Optional[Dict]
    mcp_result: Optional[Dict]

    # Aggregation
    final_score: Optional[float]
    risk_scores: Optional[Dict]
    vc_assessment: Optional[Dict]
    startup_assessment: Optional[Dict]
    loan_assessment: Optional[Dict]

    # Final Output
    decision: Optional[str]

    # Audit + execution traces
    logs: List[Dict]
    tx_hashes: List[str]
    audit_logs: List[Dict]
    planner_history: List[Dict]
    tool_history: List[Dict]
    onchain_audit: List[Dict]

    # Workflow control flags
    next_action: Optional[str]
    terminated: bool
    finished: bool
    termination_reason: Optional[str]
    iteration_count: int
    max_iterations: int
