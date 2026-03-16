from tools.vc_scorecard import build_vc_scorecard
from tools.startup_scorecard import build_startup_scorecard
from tools.loan_scorecard import build_loan_scorecard


def aggregate_results(state):
    financial = state["financial_result"]
    unit = state["unit_result"]
    business = state["business_result"]

    # Exact scoring rules
    growth_score = max(min(financial["avg_mom_growth"], 1.0), 0.0)
    runway_score = min(financial["runway_months"] / 24.0, 1.0)
    volatility_score = 1.0 / (1.0 + financial["revenue_volatility"])

    financial_score = (growth_score + runway_score + volatility_score) / 3.0
    unit_score = unit["sustainability_score"] / 100.0
    business_score = business["business_score"] / 100.0
    final_score = (0.45 * financial_score) + (0.25 * unit_score) + (0.30 * business_score)

    state["risk_scores"] = {
        "growth_score": round(growth_score, 3),
        "runway_score": round(runway_score, 3),
        "volatility_score": round(volatility_score, 3),
        "financial_score": round(financial_score, 3),
        "unit_score": round(unit_score, 3),
        "business_score": round(business_score, 3),
        "overall_score": round(final_score, 3),
    }

    if state.get("mode") == "vc":
        vc_assessment = build_vc_scorecard(state)
        state["vc_assessment"] = vc_assessment
        state["startup_assessment"] = None
        state["loan_assessment"] = None
        state["final_score"] = round(vc_assessment["score"] / 100.0, 3)
        state["decision"] = vc_assessment["decision"]
        state["risk_scores"]["vc_score"] = round(vc_assessment["score"] / 100.0, 3)
        state["risk_scores"]["overall_score"] = round(vc_assessment["score"] / 100.0, 3)
    elif state.get("mode") == "startup":
        startup_assessment = build_startup_scorecard(state)
        state["startup_assessment"] = startup_assessment
        state["vc_assessment"] = None
        state["loan_assessment"] = None
        state["final_score"] = round(startup_assessment["score"] / 100.0, 3)
        state["decision"] = startup_assessment["decision"]
        state["risk_scores"]["startup_score"] = round(startup_assessment["score"] / 100.0, 3)
        state["risk_scores"]["overall_score"] = round(startup_assessment["score"] / 100.0, 3)
    elif state.get("mode") == "loan":
        loan_assessment = build_loan_scorecard(state)
        state["loan_assessment"] = loan_assessment
        state["vc_assessment"] = None
        state["startup_assessment"] = None
        state["final_score"] = round(loan_assessment["score"] / 100.0, 3)
        state["decision"] = loan_assessment["decision"]
        state["risk_scores"]["loan_score"] = round(loan_assessment["score"] / 100.0, 3)
        state["risk_scores"]["overall_score"] = round(loan_assessment["score"] / 100.0, 3)
    else:
        state["vc_assessment"] = None
        state["startup_assessment"] = None
        state["loan_assessment"] = None
        # Decision rules:
        # > 0.75 -> APPROVE
        # 0.5 - 0.75 -> REVIEW
        # < 0.5 -> REJECT
        if final_score > 0.75:
            decision = "APPROVE"
        elif final_score >= 0.5:
            decision = "REVIEW"
        else:
            decision = "REJECT"

        state["final_score"] = round(final_score, 3)
        state["decision"] = decision

    return state
