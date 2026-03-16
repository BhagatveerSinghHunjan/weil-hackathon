from datetime import datetime, timezone

from langgraph.graph import END, StateGraph

from agent.aggregator import aggregate_results
from agent.state import AgentState
from audit.auditor import audit_step
from blockchain.logger import log_to_chain
from schemas.economics_input import UnitEconomicsInput
from schemas.financial_input import FinancialInput
from tools.business_assessment import BusinessAssessmentEngine
from weil_mcp.deployed_client import evaluate_startup_on_weilchain
from tools.financial_trends import FinancialTrendAnalyzer
from tools.unit_economics import UnitEconomicsEngine
from weil_mcp.chainvest_mcp import evaluate_startup

ACTION_FINANCIAL = "run_financial_tool"
ACTION_UNIT = "run_unit_tool"
ACTION_BUSINESS = "run_business_tool"
ACTION_AGGREGATE = "run_aggregation_tool"
ACTION_FINALIZE = "finalize"
ACTION_ABORT = "abort"


def _record_tool_history(state: AgentState, name: str, input_data, output_data) -> AgentState:
    state["tool_history"].append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": name,
            "input": input_data,
            "output": output_data,
        }
    )
    return state


def planner_node(state: AgentState):
    state["iteration_count"] += 1

    if state["iteration_count"] > state["max_iterations"]:
        state["next_action"] = ACTION_ABORT
        state["terminated"] = True
        state["termination_reason"] = "max_iterations_reached"
    elif state["financial_result"] is None:
        state["next_action"] = ACTION_FINANCIAL
    elif state["unit_result"] is None:
        state["next_action"] = ACTION_UNIT
    elif state["business_result"] is None:
        state["next_action"] = ACTION_BUSINESS
    elif state["risk_scores"] is None:
        state["next_action"] = ACTION_AGGREGATE
    else:
        state["next_action"] = ACTION_FINALIZE

    planner_output = {
        "next_action": state["next_action"],
        "iteration_count": state["iteration_count"],
        "terminated": state["terminated"],
        "termination_reason": state.get("termination_reason"),
    }
    state["planner_history"].append(planner_output)

    state = log_to_chain(
        state,
        "Planner Decision",
        input_data={
            "has_financial": state["financial_result"] is not None,
            "has_unit": state["unit_result"] is not None,
            "has_business": state["business_result"] is not None,
            "has_risk": state["risk_scores"] is not None,
        },
        output_data=planner_output,
    )
    state = audit_step(state, "Planner Decision")
    return state


def route_from_planner(state: AgentState):
    return state["next_action"] or ACTION_ABORT


def tool_executor_node(state: AgentState):
    action = state.get("next_action")

    if action == ACTION_FINANCIAL:
        state = log_to_chain(state, "Financial Analysis Started")

        analyzer = FinancialTrendAnalyzer()
        financial_input = FinancialInput(**state["startup_data"])
        result = analyzer.analyze(financial_input)
        state["financial_result"] = result

        latest_revenue = state["startup_data"]["monthly_revenue"][-1]
        latest_burn = state["startup_data"]["monthly_burn"][-1]
        cash = state["startup_data"]["cash_on_hand"]
        business_description = state["startup_data"].get("business_description", "")
        mcp_result = evaluate_startup_on_weilchain(
            latest_revenue,
            latest_burn,
            cash,
            business_description,
        )
        if mcp_result is None:
            mcp_result = evaluate_startup(latest_revenue, latest_burn, cash, business_description)
            mcp_result["deployment"] = {
                "source": "local_fallback",
                "contract_address": None,
            }
        state["mcp_result"] = mcp_result

        state = _record_tool_history(
            state,
            "financial_tool",
            financial_input.model_dump(),
            {"financial_result": result, "mcp_result": mcp_result},
        )
        state = log_to_chain(
            state,
            "Financial Analysis Completed",
            output_data={"financial_result": result, "mcp_result": mcp_result},
        )
        state = audit_step(state, "Financial Analysis Completed")
        return state

    if action == ACTION_UNIT:
        state = log_to_chain(state, "Unit Economics Analysis Started")

        engine = UnitEconomicsEngine()
        unit_input = UnitEconomicsInput(**state["startup_data"])
        result = engine.analyze(unit_input)
        state["unit_result"] = result

        state = _record_tool_history(
            state,
            "unit_economics_tool",
            unit_input.model_dump(),
            {"unit_result": result},
        )
        state = log_to_chain(
            state,
            "Unit Economics Analysis Completed",
            output_data=result,
        )
        state = audit_step(state, "Unit Economics Analysis Completed")
        return state

    if action == ACTION_AGGREGATE:
        state = log_to_chain(state, "Aggregation Started")
        state = aggregate_results(state)
        state = _record_tool_history(
            state,
            "aggregation_tool",
            {
                "financial_result": state["financial_result"],
                "unit_result": state["unit_result"],
                "business_result": state["business_result"],
            },
            {"risk_scores": state["risk_scores"], "decision": state["decision"]},
        )
        state = log_to_chain(
            state,
            "Aggregation Completed",
            output_data=state["risk_scores"],
        )
        state = audit_step(state, "Aggregation Completed")
        return state

    if action == ACTION_BUSINESS:
        state = log_to_chain(state, "Business Assessment Started")
        engine = BusinessAssessmentEngine()
        description = state["startup_data"].get("business_description", "")
        result = engine.analyze(description, state.get("mode", "vc"))
        state["business_result"] = result

        state = _record_tool_history(
            state,
            "business_assessment_tool",
            {"business_description": description, "mode": state.get("mode")},
            {"business_result": result},
        )
        state = log_to_chain(
            state,
            "Business Assessment Completed",
            output_data=result,
        )
        state = audit_step(state, "Business Assessment Completed")
        return state

    state["terminated"] = True
    state["termination_reason"] = f"invalid_tool_action:{action}"
    state = log_to_chain(
        state,
        "Tool Executor Aborted",
        output_data={"reason": state["termination_reason"]},
    )
    state = audit_step(state, "Tool Executor Aborted")
    return state


def final_node(state: AgentState):
    if state.get("next_action") == ACTION_ABORT and state.get("decision") is None:
        state["decision"] = "REVIEW"
        state["termination_reason"] = state.get("termination_reason") or "aborted_without_decision"

    state = log_to_chain(
        state,
        "Final Decision Generated",
        output_data={
            "decision": state.get("decision"),
            "final_score": state.get("final_score"),
            "termination_reason": state.get("termination_reason"),
        },
    )
    state = audit_step(state, "Final Decision Generated")
    state["finished"] = True
    return state


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("planner", planner_node)
    builder.add_node("tool_executor", tool_executor_node)
    builder.add_node("finalize", final_node)

    builder.set_entry_point("planner")
    builder.add_conditional_edges(
        "planner",
        route_from_planner,
        {
            ACTION_FINANCIAL: "tool_executor",
            ACTION_UNIT: "tool_executor",
            ACTION_BUSINESS: "tool_executor",
            ACTION_AGGREGATE: "tool_executor",
            ACTION_FINALIZE: "finalize",
            ACTION_ABORT: "finalize",
        },
    )
    builder.add_edge("tool_executor", "planner")
    builder.add_edge("finalize", END)
    return builder.compile()


def run_agent(
    mode: str,
    monthly_revenue: list[float],
    monthly_burn: list[float],
    cash_on_hand: float,
    business_description: str = "",
    ltv: float | None = None,
    cac: float | None = None,
    gross_margin: float = 60,
    monthly_new_customers: int = 50,
    vc_profile: dict | None = None,
):
    avg_revenue = sum(monthly_revenue) / len(monthly_revenue) if monthly_revenue else 0.0
    avg_burn = sum(monthly_burn) / len(monthly_burn) if monthly_burn else 0.0
    customer_count = max(float(monthly_new_customers), 1.0)
    gross_margin_ratio = max(min(gross_margin / 100.0, 1.0), 0.0)

    revenue_per_customer = avg_revenue / customer_count if customer_count else 0.0
    derived_ltv = max(ltv if ltv is not None else revenue_per_customer * 6.0 * gross_margin_ratio, 100.0)
    derived_cac = max(cac if cac is not None else avg_burn / customer_count, 50.0)

    startup_data = {
        "monthly_revenue": monthly_revenue,
        "monthly_burn": monthly_burn,
        "cash_on_hand": cash_on_hand,
        "business_description": business_description,
        "ltv": round(derived_ltv, 2),
        "cac": round(derived_cac, 2),
        "gross_margin": gross_margin,
        "monthly_new_customers": monthly_new_customers,
    }
    if vc_profile:
        startup_data.update(vc_profile)

    initial_state: AgentState = {
        "mode": mode,
        "startup_data": startup_data,
        "financial_result": None,
        "unit_result": None,
        "business_result": None,
        "mcp_result": None,
        "final_score": None,
        "risk_scores": None,
        "vc_assessment": None,
        "startup_assessment": None,
        "loan_assessment": None,
        "decision": None,
        "logs": [],
        "tx_hashes": [],
        "audit_logs": [],
        "planner_history": [],
        "tool_history": [],
        "onchain_audit": [],
        "next_action": None,
        "terminated": False,
        "finished": False,
        "termination_reason": None,
        "iteration_count": 0,
        "max_iterations": 12,
    }

    graph = build_graph()
    result = graph.invoke(initial_state)

    return {
        "mode": result.get("mode", mode),
        "decision": result["decision"],
        "final_score": result["final_score"],
        "financial_result": result["financial_result"],
        "unit_result": result["unit_result"],
        "business_result": result.get("business_result"),
        "mcp_result": result.get("mcp_result"),
        "risk_scores": result.get("risk_scores"),
        "vc_assessment": result.get("vc_assessment"),
        "startup_assessment": result.get("startup_assessment"),
        "loan_assessment": result.get("loan_assessment"),
        "logs": result.get("logs"),
        "tx_hashes": result.get("tx_hashes"),
        "audit_logs": result.get("audit_logs"),
        "planner_history": result.get("planner_history"),
        "tool_history": result.get("tool_history"),
        "onchain_audit": result.get("onchain_audit"),
        "termination_reason": result.get("termination_reason"),
        "iteration_count": result.get("iteration_count"),
    }


if __name__ == "__main__":
    print("Workflow ready.")
