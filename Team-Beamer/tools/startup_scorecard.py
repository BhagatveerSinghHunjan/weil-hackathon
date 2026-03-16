from __future__ import annotations

from typing import Any


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(value, upper))


def _float(value: Any, default: float) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _status(score: float) -> str:
    if score >= 0.9:
        return "Exceptional"
    if score >= 0.75:
        return "Strong"
    if score >= 0.55:
        return "Watch"
    return "Weak"


def _metric(name: str, value: str, benchmark: str, score: float, note: str) -> dict[str, Any]:
    return {
        "name": name,
        "value": value,
        "benchmark": benchmark,
        "status": _status(score),
        "score": round(score, 3),
        "note": note,
    }


def build_startup_scorecard(state: dict[str, Any]) -> dict[str, Any]:
    startup = state.get("startup_data") or {}
    financial = state.get("financial_result") or {}
    unit = state.get("unit_result") or {}
    business = state.get("business_result") or {}
    scores = state.get("risk_scores") or {}

    company_stage = str(startup.get("company_stage") or "seed")
    arr_growth = _float(startup.get("arr_growth_rate"), max(_float(financial.get("avg_mom_growth"), 0.0) * 12.0 * 100.0, 0.0))
    nrr = _float(startup.get("net_revenue_retention"), 100.0)
    gross_margin = _float(startup.get("gross_margin"), 70.0)
    ltv = _float(startup.get("ltv"), 0.0)
    cac = max(_float(startup.get("cac"), 1.0), 1.0)
    payback_period = _float(startup.get("payback_period_months"), _float(unit.get("payback_period_months"), 18.0))
    dau_mau_ratio = _float(startup.get("dau_mau_ratio"), 10.0)
    founder_market_fit = _float(startup.get("founder_market_fit"), 3.0)
    execution_grit = _float(startup.get("execution_grit"), 3.0)
    tam_size_billion = _float(startup.get("tam_size_billion"), 0.8)
    market_pull = _float(startup.get("market_pull"), 3.0)
    proprietary_data = _float(startup.get("proprietary_data_score"), 3.0)
    switching_costs = _float(startup.get("switching_cost_score"), 3.0)
    thesis_alignment = _float(startup.get("thesis_alignment"), 3.0)
    traction_validation = _float(startup.get("traction_validation"), 3.0)
    legal_hygiene = _float(startup.get("legal_hygiene"), 3.0)
    customer_concentration = _float(startup.get("customer_concentration_percent"), 0.0)
    cap_table_health = _float(startup.get("cap_table_health"), 3.0)
    prototype_readiness = _float(startup.get("prototype_readiness"), 3.0)
    strategic_relationships = _float(startup.get("strategic_relationships"), 3.0)
    product_rollout = _float(startup.get("product_rollout"), 3.0)
    runway_months = _float(financial.get("runway_months"), 0.0)
    cash_on_hand = _float(startup.get("cash_on_hand"), 0.0)

    ltv_cac_ratio = _float(unit.get("ltv_cac_ratio"), ltv / cac if cac else 0.0)
    latest_revenue = _float((startup.get("monthly_revenue") or [0])[-1], 0.0)
    latest_burn = _float((startup.get("monthly_burn") or [0])[-1], 0.0)
    annual_revenue = latest_revenue * 12.0
    net_new_arr = max(annual_revenue * (arr_growth / 100.0), 1.0)
    burn_multiple = (latest_burn * 12.0) / net_new_arr

    founder_market_fit_score = _clamp(founder_market_fit / 5.0)
    execution_grit_score = _clamp(execution_grit / 5.0)
    tam_score = _clamp(tam_size_billion / 5.0)
    market_pull_score = _clamp(market_pull / 5.0)
    proprietary_data_score = _clamp(proprietary_data / 5.0)
    switching_cost_score = _clamp(switching_costs / 5.0)
    thesis_alignment_score = _clamp(thesis_alignment / 5.0)
    traction_validation_score = _clamp(traction_validation / 5.0)
    legal_hygiene_score = _clamp(legal_hygiene / 5.0)

    arr_growth_score = _clamp(arr_growth / 120.0)
    nrr_score = _clamp((nrr - 90.0) / 35.0)
    burn_multiple_score = _clamp((2.5 - burn_multiple) / 1.5)
    ltv_cac_score = _clamp((ltv_cac_ratio - 1.0) / 3.0)
    payback_score = _clamp((18.0 - payback_period) / 12.0)
    dau_mau_score = _clamp(dau_mau_ratio / 20.0)
    runway_score = _clamp(runway_months / 24.0)
    revenue_scale_score = _clamp(latest_revenue / 100000.0)
    cash_reserve_score = _clamp(cash_on_hand / max(latest_burn * 18.0, 1.0))
    capital_efficiency_score = _clamp(
        0.5 * runway_score + 0.3 * burn_multiple_score + 0.2 * _float(scores.get("financial_score"), 0.0)
    )
    valuation_financial_signal = _clamp(
        0.40 * revenue_scale_score
        + 0.25 * burn_multiple_score
        + 0.20 * runway_score
        + 0.15 * cash_reserve_score
    )

    qualitative_pillars = [
        _metric("Founder-Market Fit", f"{founder_market_fit:.1f}/5", "4/5 or higher", founder_market_fit_score, "Industry depth and technical edge."),
        _metric("Execution Grit", f"{execution_grit:.1f}/5", "4/5 or higher", execution_grit_score, "Speed of learning, resilience, and ability to recruit."),
        _metric("Market Opportunity (TAM)", f"${tam_size_billion:.2f}B", ">$1B and ideally much larger", tam_score, "Venture-scale upside requires a large market."),
        _metric("Market Pull", f"{market_pull:.1f}/5", "4/5 or higher", market_pull_score, "Urgency of the customer pain point."),
        _metric("Proprietary Data", f"{proprietary_data:.1f}/5", "4/5 or higher", proprietary_data_score, "Hard-to-replicate data advantage."),
        _metric("Switching Costs", f"{switching_costs:.1f}/5", "4/5 or higher", switching_cost_score, "How sticky the product becomes after adoption."),
    ]

    quantitative_metrics = [
        _metric("ARR / MRR Growth", f"{arr_growth:.1f}%", "100%+ YoY or 10-20% MoM", arr_growth_score, "Primary growth signal."),
        _metric("Net Revenue Retention", f"{nrr:.1f}%", ">120%", nrr_score, "Negative churn and account expansion."),
        _metric("Burn Multiple", f"{burn_multiple:.2f}x", "<1.5x, ideally <1.0x", burn_multiple_score, "Efficiency of spend versus ARR creation."),
        _metric("LTV : CAC Ratio", f"{ltv_cac_ratio:.2f}x", "3.0x or higher", ltv_cac_score, "Unit economics quality."),
        _metric("CAC Payback Period", f"{payback_period:.1f} mo", "<12 months", payback_score, "Sales efficiency and speed."),
        _metric("DAU / MAU Ratio", f"{dau_mau_ratio:.1f}%", ">13% for B2B SaaS", dau_mau_score, "Product stickiness and engagement."),
    ]

    berkus = {
        "sound_idea": prototype_readiness >= 3,
        "prototype": prototype_readiness >= 4,
        "quality_management": founder_market_fit >= 4 and execution_grit >= 4,
        "strategic_relationships": strategic_relationships >= 4,
        "product_rollout": product_rollout >= 4,
    }
    berkus_base = sum(1 for value in berkus.values() if value) * 500_000
    berkus_financial_premium = round(1_500_000 * valuation_financial_signal)
    berkus_score = berkus_base + berkus_financial_premium

    scorecard_method = round(
        (
            0.25 * founder_market_fit_score
            + 0.20 * tam_score
            + 0.15 * traction_validation_score
            + 0.10 * proprietary_data_score
            + 0.15 * capital_efficiency_score
            + 0.15 * valuation_financial_signal
        )
        * 100.0,
        1,
    )

    if company_stage in {"pre_seed", "seed"}:
        weighting = {
            "Founder / Team": 0.35,
            "Market Opportunity": 0.25,
            "Product Defensibility": 0.20,
            "Traction / Validation": 0.20,
        }
        startup_mode_score = (
            0.35 * (0.6 * founder_market_fit_score + 0.4 * execution_grit_score)
            + 0.25 * (0.6 * tam_score + 0.4 * market_pull_score)
            + 0.20 * (0.55 * proprietary_data_score + 0.45 * switching_cost_score)
            + 0.20 * (0.6 * traction_validation_score + 0.4 * thesis_alignment_score)
        )
        stage_label = "Early Stage"
    else:
        weighting = {
            "Growth": 0.22,
            "Retention": 0.18,
            "Efficiency": 0.18,
            "Unit Economics": 0.16,
            "Sales Speed": 0.12,
            "Engagement": 0.14,
        }
        startup_mode_score = (
            0.22 * arr_growth_score
            + 0.18 * nrr_score
            + 0.18 * burn_multiple_score
            + 0.16 * ltv_cac_score
            + 0.12 * payback_score
            + 0.14 * dau_mau_score
        )
        stage_label = "Series A+"

    diligence_layers = [
        _metric("Thesis Alignment", f"{thesis_alignment:.1f}/5", "4/5 or higher", thesis_alignment_score, "Sector, stage, and geography fit."),
        _metric("Traction & Validation", f"{traction_validation:.1f}/5", "4/5 or higher", traction_validation_score, "Proof through pilots, LOIs, or cohort quality."),
        _metric("Capital Efficiency", f"{runway_months:.1f} mo", "18-24 months runway", capital_efficiency_score, "Milestone progress per dollar spent."),
        _metric("Legal Hygiene", f"{legal_hygiene:.1f}/5", "4/5 or higher", legal_hygiene_score, "IP ownership and compliance readiness."),
    ]

    red_flags: list[str] = []
    if customer_concentration > 30:
        red_flags.append("Customer concentration is above 30% of revenue.")
    if cap_table_health <= 2:
        red_flags.append("Cap table health indicates dead-weight or inactive ownership risk.")
    if legal_hygiene <= 2:
        red_flags.append("Legal hygiene is weak and may indicate IP or compliance gaps.")

    combined_score = round(
        (
            0.30 * _float(scores.get("financial_score"), 0.0)
            + 0.20 * _float(scores.get("unit_score"), 0.0)
            + 0.20 * _float(scores.get("business_score"), 0.0)
            + 0.30 * startup_mode_score
        )
        * 100.0,
        1,
    )

    if red_flags:
        decision = "REJECT"
    elif combined_score >= 76:
        decision = "APPROVE"
    elif combined_score >= 56:
        decision = "REVIEW"
    else:
        decision = "REJECT"

    highlights: list[str] = []
    concerns: list[str] = []
    for metric in qualitative_pillars + quantitative_metrics + diligence_layers:
        if metric["status"] in {"Exceptional", "Strong"} and len(highlights) < 4:
            highlights.append(f'{metric["name"]} is {metric["value"]}, which is {metric["status"].lower()} against the startup benchmark.')
        if metric["status"] == "Weak" and len(concerns) < 4:
            concerns.append(f'{metric["name"]} is {metric["value"]}, below the expected benchmark of {metric["benchmark"]}.')
    concerns.extend(red_flags)
    if not concerns and not red_flags:
        concerns.append("No critical startup red flags were detected in the current assessment.")

    diligence_checklist = []
    if decision in {"APPROVE", "REVIEW"}:
        diligence_checklist = [
            "Confirm thesis alignment on sector, stage, and geography.",
            "Validate traction through pilots, LOIs, cohort retention, and customer references.",
            "Stress-test capital efficiency versus milestone progress and runway needs.",
            "Review IP ownership, compliance posture, and cap table cleanliness.",
        ]

    return {
        "stage": stage_label,
        "score": combined_score,
        "decision": decision,
        "weighting": [{"label": label, "weight": int(weight * 100)} for label, weight in weighting.items()],
        "qualitative_pillars": qualitative_pillars,
        "quantitative_metrics": quantitative_metrics,
        "diligence_layers": diligence_layers,
        "red_flags": red_flags,
        "highlights": highlights,
        "concerns": concerns,
        "diligence_checklist": diligence_checklist,
        "advanced_valuation": {
            "berkus_estimate": berkus_score,
            "scorecard_percentile": scorecard_method,
            "valuation_drivers": {
                "monthly_revenue": latest_revenue,
                "monthly_burn": latest_burn,
                "cash_available": cash_on_hand,
                "runway_months": round(runway_months, 1),
                "revenue_scale_score": round(revenue_scale_score * 100.0, 1),
                "burn_discipline_score": round(burn_multiple_score * 100.0, 1),
                "cash_reserve_score": round(cash_reserve_score * 100.0, 1),
                "valuation_financial_signal": round(valuation_financial_signal * 100.0, 1),
            },
        },
        "threshold_context": "Startup mode balances early-stage qualitative conviction with performance indicators and red-flag screening.",
        "summary": f"{decision.title()} in Startup Evaluation mode with a {combined_score:.1f}/100 composite score under the {stage_label} model.",
    }
