import json
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.workflow import run_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InputSchema(BaseModel):
    mode: str
    revenue: float
    burn: float
    cash: float
    business_description: str = ""
    company_stage: str = "seed"
    arr_growth_rate: float | None = None
    net_revenue_retention: float | None = None
    ltv: float | None = None
    cac: float | None = None
    gross_margin: float | None = None
    payback_period_months: float | None = None
    monthly_new_customers: int = 50
    founder_market_fit: float | None = None
    execution_grit: float | None = None
    tam_size_billion: float | None = None
    market_pull: float | None = None
    moat_score_input: float | None = None
    market_timing: float | None = None
    proprietary_data_score: float | None = None
    switching_cost_score: float | None = None
    dau_mau_ratio: float | None = None
    thesis_alignment: float | None = None
    traction_validation: float | None = None
    legal_hygiene: float | None = None
    customer_concentration_percent: float | None = None
    cap_table_health: float | None = None
    prototype_readiness: float | None = None
    strategic_relationships: float | None = None
    product_rollout: float | None = None
    dscr: float | None = None
    total_debt_service: float | None = None
    current_ratio: float | None = None
    debt_to_equity_ratio: float | None = None
    interest_coverage_ratio: float | None = None
    interest_expense: float | None = None
    net_profit_margin: float | None = None
    credit_score: float | None = None
    years_in_business: float | None = None
    cheque_bounces: float | None = None
    average_bank_balance: float | None = None
    monthly_emi: float | None = None
    tax_compliance_score: float | None = None
    recent_defaults: float | None = None
    nbfc_loan_load: float | None = None
    collateral_value: float | None = None
    requested_loan_amount: float | None = None
    financial_spreading_score: float | None = None


def _build_decision_reasoning(state: dict[str, Any]) -> dict[str, Any]:
    decision = state.get("decision") or "REVIEW"
    vc_assessment = state.get("vc_assessment")
    startup_assessment = state.get("startup_assessment")
    loan_assessment = state.get("loan_assessment")
    if vc_assessment:
        return {
            "summary": vc_assessment.get("summary"),
            "threshold_context": vc_assessment.get("threshold_context"),
            "score_breakdown": {
                "overall_score": round(float(vc_assessment.get("score", 0.0)) / 100.0, 3),
                "financial_score": (state.get("risk_scores") or {}).get("financial_score"),
                "unit_score": (state.get("risk_scores") or {}).get("unit_score"),
                "business_score": (state.get("risk_scores") or {}).get("business_score"),
                "vc_score": (state.get("risk_scores") or {}).get("vc_score"),
            },
            "highlights": vc_assessment.get("highlights", []),
            "concerns": vc_assessment.get("concerns", []),
            "diligence_checklist": vc_assessment.get("diligence_checklist", []),
        }
    if startup_assessment:
        return {
            "summary": startup_assessment.get("summary"),
            "threshold_context": startup_assessment.get("threshold_context"),
            "score_breakdown": {
                "overall_score": round(float(startup_assessment.get("score", 0.0)) / 100.0, 3),
                "financial_score": (state.get("risk_scores") or {}).get("financial_score"),
                "unit_score": (state.get("risk_scores") or {}).get("unit_score"),
                "business_score": (state.get("risk_scores") or {}).get("business_score"),
                "startup_score": (state.get("risk_scores") or {}).get("startup_score"),
            },
            "highlights": startup_assessment.get("highlights", []),
            "concerns": startup_assessment.get("concerns", []),
            "diligence_checklist": startup_assessment.get("diligence_checklist", []),
        }
    if loan_assessment:
        return {
            "summary": loan_assessment.get("summary"),
            "threshold_context": loan_assessment.get("threshold_context"),
            "score_breakdown": {
                "overall_score": round(float(loan_assessment.get("score", 0.0)) / 100.0, 3),
                "financial_score": (state.get("risk_scores") or {}).get("financial_score"),
                "unit_score": (state.get("risk_scores") or {}).get("unit_score"),
                "business_score": (state.get("risk_scores") or {}).get("business_score"),
                "loan_score": (state.get("risk_scores") or {}).get("loan_score"),
            },
            "highlights": loan_assessment.get("highlights", []),
            "concerns": loan_assessment.get("concerns", []),
            "diligence_checklist": loan_assessment.get("diligence_checklist", []),
        }

    scores = state.get("risk_scores") or {}
    financial = state.get("financial_result") or {}
    unit = state.get("unit_result") or {}
    business = state.get("business_result") or {}

    overall_score = float(scores.get("overall_score", 0.0))
    threshold_text = (
        "Approved above 0.75, Review from 0.50 to 0.75, Rejected below 0.50."
    )

    highlights: list[str] = []
    concerns: list[str] = []

    runway_months = float(financial.get("runway_months", 0.0))
    volatility = float(financial.get("revenue_volatility", 0.0))
    growth = float(financial.get("avg_mom_growth", 0.0))
    sustainability = float(unit.get("sustainability_score", 0.0))
    business_score = float(business.get("business_score", 0.0))

    if runway_months >= 12:
        highlights.append(f"Cash runway is {runway_months:.1f} months, which supports continued execution.")
    elif runway_months < 6:
        concerns.append(f"Cash runway is only {runway_months:.1f} months, which creates financing pressure.")

    if growth >= 0.1:
        highlights.append(f"Average month-over-month growth is {growth:.2f}, indicating strong commercial momentum.")
    elif growth <= 0.02:
        concerns.append(f"Average month-over-month growth is {growth:.2f}, which is weak for VC-style upside.")

    if volatility <= 0.2:
        highlights.append("Revenue volatility is controlled, which improves forecast confidence.")
    elif volatility >= 0.5:
        concerns.append("Revenue volatility is elevated, which reduces confidence in consistency.")

    if sustainability >= 80:
        highlights.append(f"Unit economics are strong with a sustainability score of {sustainability:.0f}.")
    elif sustainability < 60:
        concerns.append(f"Unit economics are soft with a sustainability score of {sustainability:.0f}.")

    if business_score >= 70:
        highlights.append(
            f"Business quality scores well on sector, scalability, and market attractiveness at {business_score:.0f}."
        )
    elif business_score < 50:
        concerns.append(
            f"Business quality is weaker at {business_score:.0f}, which suggests scaling or market-quality concerns."
        )

    for flag in business.get("flags", []) or []:
        if flag == "customer_concentration_risk":
            concerns.append("The business description suggests customer concentration risk.")
        elif flag == "early_or_unclear_positioning":
            concerns.append("Positioning appears early or unclear, which weakens investability.")
        elif flag == "missing_business_description":
            concerns.append("Business context is too thin, so the company quality assessment is conservative.")

    if decision == "APPROVE":
        summary = f"Accepted because the overall score of {overall_score:.3f} clears the approval threshold with enough financial and business quality support."
    elif decision == "REJECT":
        summary = f"Rejected because the overall score of {overall_score:.3f} falls below the review threshold and the current profile is not investable enough."
    else:
        summary = f"Placed in review because the overall score of {overall_score:.3f} is mixed: strong enough to avoid rejection, but not strong enough for approval."

    if not highlights:
        highlights.append("The company has some positive signals, but none are strong enough to dominate the decision.")
    if not concerns:
        concerns.append("No major red flags were detected in the current financial and business inputs.")

    return {
        "summary": summary,
        "threshold_context": threshold_text,
        "score_breakdown": {
            "overall_score": round(overall_score, 3),
            "financial_score": scores.get("financial_score"),
            "unit_score": scores.get("unit_score"),
            "business_score": scores.get("business_score"),
        },
        "highlights": highlights,
        "concerns": concerns,
    }


def _ensure_risk_scores(state: dict[str, Any]) -> None:
    if state.get("risk_scores") is not None:
        return

    financial = state.get("financial_result") or {}
    unit = state.get("unit_result") or {}
    business = state.get("business_result") or {}

    growth_score = max(min(float(financial.get("avg_mom_growth", 0.0)), 1.0), 0.0)
    runway_score = min(float(financial.get("runway_months", 0.0)) / 24.0, 1.0)
    volatility = float(financial.get("revenue_volatility", 0.0))
    volatility_score = 1.0 / (1.0 + volatility)

    financial_score = (growth_score + runway_score + volatility_score) / 3.0
    unit_score = float(unit.get("sustainability_score", 0.0)) / 100.0
    business_score = float(business.get("business_score", 0.0)) / 100.0
    overall_score = (0.45 * financial_score) + (0.25 * unit_score) + (0.30 * business_score)

    state["risk_scores"] = {
        "growth_score": round(growth_score, 3),
        "runway_score": round(runway_score, 3),
        "volatility_score": round(volatility_score, 3),
        "financial_score": round(financial_score, 3),
        "unit_score": round(unit_score, 3),
        "business_score": round(business_score, 3),
        "overall_score": round(overall_score, 3),
    }
    state["final_score"] = round(overall_score, 3)

    if overall_score > 0.75:
        state["decision"] = "APPROVE"
    elif overall_score >= 0.5:
        state["decision"] = "REVIEW"
    else:
        state["decision"] = "REJECT"

def _format_logs(logs: list[Any]) -> list[str]:
    output: list[str] = []
    for log in logs:
        if isinstance(log, dict):
            ts = log.get("timestamp")
            step = log.get("step")
            tx = log.get("tx_hash")
            output.append(f"{ts} | {step} | {tx}")
        else:
            output.append(str(log))
    return output


@app.post("/analyze")
def analyze(data: InputSchema):
    vc_profile = {
        "company_stage": data.company_stage,
        "arr_growth_rate": data.arr_growth_rate,
        "net_revenue_retention": data.net_revenue_retention,
        "payback_period_months": data.payback_period_months,
        "founder_market_fit": data.founder_market_fit,
        "execution_grit": data.execution_grit,
        "tam_size_billion": data.tam_size_billion,
        "market_pull": data.market_pull,
        "moat_score_input": data.moat_score_input,
        "market_timing": data.market_timing,
        "proprietary_data_score": data.proprietary_data_score,
        "switching_cost_score": data.switching_cost_score,
        "dau_mau_ratio": data.dau_mau_ratio,
        "thesis_alignment": data.thesis_alignment,
        "traction_validation": data.traction_validation,
        "legal_hygiene": data.legal_hygiene,
        "customer_concentration_percent": data.customer_concentration_percent,
        "cap_table_health": data.cap_table_health,
        "prototype_readiness": data.prototype_readiness,
        "strategic_relationships": data.strategic_relationships,
        "product_rollout": data.product_rollout,
        "dscr": data.dscr,
        "total_debt_service": data.total_debt_service,
        "current_ratio": data.current_ratio,
        "debt_to_equity_ratio": data.debt_to_equity_ratio,
        "interest_coverage_ratio": data.interest_coverage_ratio,
        "interest_expense": data.interest_expense,
        "net_profit_margin": data.net_profit_margin,
        "credit_score": data.credit_score,
        "years_in_business": data.years_in_business,
        "cheque_bounces": data.cheque_bounces,
        "average_bank_balance": data.average_bank_balance,
        "monthly_emi": data.monthly_emi,
        "tax_compliance_score": data.tax_compliance_score,
        "recent_defaults": data.recent_defaults,
        "nbfc_loan_load": data.nbfc_loan_load,
        "collateral_value": data.collateral_value,
        "requested_loan_amount": data.requested_loan_amount,
        "financial_spreading_score": data.financial_spreading_score,
    }

    result = run_agent(
        mode=data.mode,
        monthly_revenue=[data.revenue] * 12,
        monthly_burn=[data.burn] * 12,
        cash_on_hand=data.cash,
        business_description=data.business_description,
        ltv=data.ltv,
        cac=data.cac,
        gross_margin=data.gross_margin or 60,
        monthly_new_customers=data.monthly_new_customers,
        vc_profile=vc_profile,
    )

    print("\n===== NEW REQUEST =====")
    print("RESULT JSON:\n", json.dumps(result, indent=2))

    state = result.get("state", result)
    state["mode"] = state.get("mode") or data.mode

    _ensure_risk_scores(state)

    return {
        "mode": state.get("mode"),
        "decision": state.get("decision"),
        "final_score": state.get("final_score"),
        "reasons": state.get("reasons", []),
        "decision_reasoning": _build_decision_reasoning(state),
        "financial_result": state.get("financial_result"),
        "unit_result": state.get("unit_result"),
        "business_result": state.get("business_result"),
        "risk_scores": state.get("risk_scores"),
        "vc_assessment": state.get("vc_assessment"),
        "startup_assessment": state.get("startup_assessment"),
        "loan_assessment": state.get("loan_assessment"),
        "mcp_result": state.get("mcp_result"),
        "logs": _format_logs(state.get("logs", [])),
        "tx_hashes": state.get("tx_hashes", []),
        "audit_logs": state.get("audit_logs", []),
        "planner_history": state.get("planner_history", []),
        "tool_history": state.get("tool_history", []),
        "onchain_audit": state.get("onchain_audit", []),
        "termination_reason": state.get("termination_reason"),
        "iteration_count": state.get("iteration_count"),
    }
