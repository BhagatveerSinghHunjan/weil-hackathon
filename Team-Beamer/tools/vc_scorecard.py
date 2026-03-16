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


def _build_metric(name: str, value: float, benchmark: str, score: float, note: str, unit: str = "") -> dict[str, Any]:
    if unit == "%":
        display_value = f"{value:.1f}%"
    elif unit == "months":
        display_value = f"{value:.1f} mo"
    elif unit == "x":
        display_value = f"{value:.2f}x"
    elif unit == "$B":
        display_value = f"${value:.2f}B"
    else:
        display_value = f"{value:.2f}"

    return {
        "name": name,
        "value": display_value,
        "benchmark": benchmark,
        "status": _status(score),
        "score": round(score, 3),
        "note": note,
    }


def build_vc_scorecard(state: dict[str, Any]) -> dict[str, Any]:
    startup = state.get("startup_data") or {}
    financial = state.get("financial_result") or {}
    unit = state.get("unit_result") or {}
    business = state.get("business_result") or {}

    latest_revenue = _float((startup.get("monthly_revenue") or [0])[-1], 0.0)
    latest_burn = _float((startup.get("monthly_burn") or [0])[-1], 0.0)
    annual_revenue = latest_revenue * 12.0

    company_stage = str(startup.get("company_stage") or "seed")
    arr_growth = _float(startup.get("arr_growth_rate"), max(_float(financial.get("avg_mom_growth"), 0.0) * 12.0 * 100.0, 0.0))
    nrr = _float(startup.get("net_revenue_retention"), 100.0)
    ltv = _float(startup.get("ltv"), 0.0)
    cac = max(_float(startup.get("cac"), 0.0), 1.0)
    ltv_cac_ratio = _float(unit.get("ltv_cac_ratio"), ltv / cac if cac else 0.0)
    gross_margin = _float(startup.get("gross_margin"), 60.0)
    payback_period = _float(startup.get("payback_period_months"), _float(unit.get("payback_period_months"), 18.0))
    founder_market_fit = _float(startup.get("founder_market_fit"), 3.0)
    tam_size_billion = _float(startup.get("tam_size_billion"), 0.75)
    moat_input = _float(startup.get("moat_score_input"), 3.0)
    market_timing = _float(startup.get("market_timing"), 3.0)
    customer_concentration = _float(startup.get("customer_concentration_percent"), 0.0)
    cap_table_health = _float(startup.get("cap_table_health"), 3.0)

    net_new_arr = max(annual_revenue * (arr_growth / 100.0), 1.0)
    burn_multiple = (latest_burn * 12.0) / net_new_arr
    runway_months = _float(financial.get("runway_months"), 0.0)

    arr_growth_score = _clamp(arr_growth / 120.0)
    nrr_score = _clamp((nrr - 90.0) / 35.0)
    ltv_cac_score = _clamp((ltv_cac_ratio - 1.0) / 3.0)
    burn_multiple_score = _clamp((3.0 - burn_multiple) / 2.0)
    gross_margin_score = _clamp((gross_margin - 50.0) / 30.0)
    payback_score = _clamp((18.0 - payback_period) / 12.0)

    quantitative_metrics = [
        _build_metric(
            "ARR / MRR Growth",
            arr_growth,
            ">100% YoY early-stage; 50%+ growth stage",
            arr_growth_score,
            "Measures top-line momentum and scalability.",
            "%",
        ),
        _build_metric(
            "Net Revenue Retention",
            nrr,
            ">110-120% best-in-class",
            nrr_score,
            "Shows whether existing customers expand over time.",
            "%",
        ),
        _build_metric(
            "LTV / CAC Ratio",
            ltv_cac_ratio,
            "3.0x or higher",
            ltv_cac_score,
            "Tests acquisition sustainability.",
            "x",
        ),
        _build_metric(
            "Burn Multiple",
            burn_multiple,
            "<2.0x good; <1.0x exceptional",
            burn_multiple_score,
            "Measures how efficiently burn creates new ARR.",
            "x",
        ),
        _build_metric(
            "Gross Margin",
            gross_margin,
            "70-80%+ for software",
            gross_margin_score,
            "Low margins weaken SaaS quality.",
            "%",
        ),
        _build_metric(
            "Payback Period",
            payback_period,
            "<12 months B2B; ideally <6 months",
            payback_score,
            "Shorter payback supports efficient growth.",
            "months",
        ),
    ]

    moat_score = _clamp(((moat_input / 5.0) + _float(business.get("moat_score"), 0.5)) / 2.0)
    market_opportunity_score = _clamp(
        0.55 * _clamp(tam_size_billion / 3.0)
        + 0.25 * _clamp(market_timing / 5.0)
        + 0.20 * _float(business.get("market_score"), 0.5)
    )
    team_vision_score = _clamp(
        0.65 * _clamp(founder_market_fit / 5.0) + 0.35 * _clamp(cap_table_health / 5.0)
    )
    early_traction_score = _clamp(
        0.4 * arr_growth_score + 0.35 * nrr_score + 0.25 * _float(business.get("traction_score"), 0.5)
    )
    unit_efficiency_score = (
        arr_growth_score
        + nrr_score
        + ltv_cac_score
        + burn_multiple_score
        + gross_margin_score
        + payback_score
    ) / 6.0
    market_dominance_score = _clamp(
        0.45 * moat_score + 0.30 * market_opportunity_score + 0.25 * _float(business.get("sector_score"), 0.5)
    )

    qualitative_pillars = [
        _build_metric(
            "Founder-Market Fit",
            founder_market_fit,
            "4/5 or higher",
            _clamp(founder_market_fit / 5.0),
            "Captures team credibility, technical depth, and lived experience.",
        ),
        _build_metric(
            "Market Opportunity (TAM)",
            tam_size_billion,
            ">$1B TAM",
            _clamp(tam_size_billion / 3.0),
            "The market must be large enough for venture-scale outcomes.",
            "$B",
        ),
        _build_metric(
            "Defensible Moat",
            moat_input,
            "4/5 or higher",
            moat_score,
            "Combines declared moat strength with business defensibility signals.",
        ),
        _build_metric(
            "Market Timing",
            market_timing,
            "4/5 or higher",
            _clamp(market_timing / 5.0),
            "Favors adoption tailwinds and favorable timing windows.",
        ),
    ]

    if company_stage in {"series_b_plus", "growth"}:
        stage_label = "Series B+"
        weighting = {
            "Unit Economics / Efficiency": 0.60,
            "Market Dominance": 0.20,
            "Team / Leadership": 0.20,
        }
        vc_mode_score = (
            0.60 * unit_efficiency_score
            + 0.20 * market_dominance_score
            + 0.20 * team_vision_score
        )
    else:
        stage_label = "Seed"
        weighting = {
            "Team / Vision": 0.50,
            "Market Opportunity": 0.30,
            "Early Traction / Product": 0.20,
        }
        vc_mode_score = (
            0.50 * team_vision_score
            + 0.30 * market_opportunity_score
            + 0.20 * early_traction_score
        )

    red_flags: list[str] = []
    if customer_concentration > 30:
        red_flags.append("Customer concentration is above 30% of revenue.")
    if runway_months < 6 and arr_growth < 40:
        red_flags.append("Runway is below 6 months without strong enough growth to offset burn risk.")
    if cap_table_health <= 2:
        red_flags.append("Cap table health looks weak and may indicate non-strategic or inactive ownership.")

    combined_score = round(
        (
            0.35 * _float((state.get("risk_scores") or {}).get("financial_score"), 0.0)
            + 0.20 * _float((state.get("risk_scores") or {}).get("unit_score"), 0.0)
            + 0.20 * _float((state.get("risk_scores") or {}).get("business_score"), 0.0)
            + 0.25 * vc_mode_score
        )
        * 100.0,
        1,
    )

    if red_flags:
        decision = "REJECT"
    elif combined_score >= 78:
        decision = "APPROVE"
    elif combined_score >= 58:
        decision = "REVIEW"
    else:
        decision = "REJECT"

    highlights: list[str] = []
    concerns: list[str] = []

    for metric in quantitative_metrics + qualitative_pillars:
        if metric["status"] in {"Exceptional", "Strong"} and len(highlights) < 4:
            highlights.append(f'{metric["name"]} is {metric["value"]}, which is {metric["status"].lower()} versus the VC benchmark.')
        if metric["status"] == "Weak" and len(concerns) < 4:
            concerns.append(f'{metric["name"]} is {metric["value"]}, which misses the target benchmark of {metric["benchmark"]}.')

    if not concerns and not red_flags:
        concerns.append("No automatic rejection triggers were detected in the current VC inputs.")
    concerns.extend(red_flags)

    diligence_checklist = []
    if decision in {"APPROVE", "REVIEW"}:
        diligence_checklist = [
            "Technical audit: review code quality, architecture resilience, and technical debt.",
            "Customer validation: interview the top 5 customers and confirm why they bought and stayed.",
            "Legal hygiene: verify IP ownership, contracts, and compliance with data/privacy law.",
            "Reference checks: run founder and operator back-channel references on integrity and execution.",
        ]

    return {
        "stage": stage_label,
        "score": combined_score,
        "decision": decision,
        "weighting": [
            {"label": label, "weight": int(weight * 100)}
            for label, weight in weighting.items()
        ],
        "quantitative_metrics": quantitative_metrics,
        "qualitative_pillars": qualitative_pillars,
        "category_scores": {
            "team_vision": round(team_vision_score * 100.0, 1),
            "market_opportunity": round(market_opportunity_score * 100.0, 1),
            "early_traction_product": round(early_traction_score * 100.0, 1),
            "unit_efficiency": round(unit_efficiency_score * 100.0, 1),
            "market_dominance": round(market_dominance_score * 100.0, 1),
        },
        "red_flags": red_flags,
        "highlights": highlights,
        "concerns": concerns,
        "diligence_checklist": diligence_checklist,
        "threshold_context": "VC mode uses stage-aware weights and auto-reject red flags before approve/review thresholds are applied.",
        "summary": (
            f"{decision.title()} in VC mode with a {combined_score:.1f}/100 composite score under the {stage_label} weighting model."
        ),
    }
