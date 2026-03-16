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


def build_loan_scorecard(state: dict[str, Any]) -> dict[str, Any]:
    startup = state.get("startup_data") or {}
    financial = state.get("financial_result") or {}
    scores = state.get("risk_scores") or {}

    latest_revenue = _float((startup.get("monthly_revenue") or [0])[-1], 0.0)
    latest_burn = _float((startup.get("monthly_burn") or [0])[-1], 0.0)
    cash_on_hand = _float(startup.get("cash_on_hand"), 0.0)

    dscr = _float(startup.get("dscr"), max((latest_revenue - latest_burn) / max(_float(startup.get("total_debt_service"), latest_burn * 0.35), 1.0), 0.0))
    current_ratio = _float(startup.get("current_ratio"), max(cash_on_hand / max(latest_burn, 1.0), 0.0))
    debt_to_equity = _float(startup.get("debt_to_equity_ratio"), 1.5)
    interest_coverage = _float(startup.get("interest_coverage_ratio"), max((latest_revenue - latest_burn) / max(_float(startup.get("interest_expense"), latest_burn * 0.08), 1.0), 0.0))
    net_profit_margin = _float(startup.get("net_profit_margin"), max((latest_revenue - latest_burn) / max(latest_revenue, 1.0) * 100.0, -100.0))

    credit_score = _float(startup.get("credit_score"), 680.0)
    years_in_business = _float(startup.get("years_in_business"), 2.0)
    cheque_bounces = _float(startup.get("cheque_bounces"), 0.0)
    avg_bank_balance = _float(startup.get("average_bank_balance"), cash_on_hand / 6.0 if cash_on_hand else 0.0)
    monthly_emi = _float(startup.get("monthly_emi"), latest_burn * 0.15)
    customer_concentration = _float(startup.get("customer_concentration_percent"), 0.0)
    tax_compliance = _float(startup.get("tax_compliance_score"), 4.0)
    defaults_recent = _float(startup.get("recent_defaults"), 0.0)
    nbfc_loan_load = _float(startup.get("nbfc_loan_load"), 2.0)
    collateral_value = _float(startup.get("collateral_value"), 0.0)
    requested_loan_amount = _float(startup.get("requested_loan_amount"), latest_revenue * 6.0)
    ltv_ratio = requested_loan_amount / max(collateral_value, 1.0) if collateral_value > 0 else 0.0

    declining_revenue = False
    revenue_series = startup.get("monthly_revenue") or []
    if len(revenue_series) >= 9:
        quarters = [
            sum(revenue_series[-9:-6]),
            sum(revenue_series[-6:-3]),
            sum(revenue_series[-3:]),
        ]
        declining_revenue = quarters[0] > quarters[1] > quarters[2]

    dscr_score = _clamp((dscr - 1.0) / 0.75)
    current_ratio_score = _clamp((current_ratio - 1.0) / 1.0)
    debt_to_equity_score = _clamp((3.0 - debt_to_equity) / 2.0)
    interest_coverage_score = _clamp((interest_coverage - 1.0) / 3.0)
    net_margin_score = _clamp((net_profit_margin - 2.0) / 13.0)
    credit_score_metric = _clamp((credit_score - 600.0) / 150.0)
    longevity_score = _clamp((years_in_business - 1.0) / 3.0)
    banking_hygiene_score = _clamp(
        0.6 * (1.0 if cheque_bounces == 0 else 0.2)
        + 0.4 * _clamp(avg_bank_balance / max(monthly_emi * 2.0, 1.0))
    )
    collateral_score = _clamp((0.85 - ltv_ratio) / 0.25) if collateral_value > 0 else 0.5
    tax_compliance_score = _clamp(tax_compliance / 5.0)

    solvency_metrics = [
        _metric("Debt Service Coverage Ratio", f"{dscr:.2f}x", ">1.25 standard; <1.0 auto-reject", dscr_score, "Core ability to service debt from operations."),
        _metric("Current Ratio", f"{current_ratio:.2f}x", "1.5 to 2.0 ideal", current_ratio_score, "Short-term liquidity coverage."),
        _metric("Debt-to-Equity Ratio", f"{debt_to_equity:.2f}x", "<2.0 preferred", debt_to_equity_score, "Avoids over-leverage."),
        _metric("Interest Coverage Ratio", f"{interest_coverage:.2f}x", ">3.0 safe", interest_coverage_score, "Interest servicing headroom."),
        _metric("Net Profit Margin", f"{net_profit_margin:.1f}%", ">10% average; <5% red flag", net_margin_score, "Operating profitability."),
    ]

    credit_metrics = [
        _metric("Bureau Credit Score", f"{credit_score:.0f}", ">700 typically required", credit_score_metric, "Credit behavior history."),
        _metric("Business Longevity", f"{years_in_business:.1f} years", "2-3 years minimum", longevity_score, "Operational history and filings."),
        _metric("Banking Hygiene", "Clean" if cheque_bounces == 0 else f"{int(cheque_bounces)} bounce(s)", "No cheque bounces; ABB >10-20% of EMI", banking_hygiene_score, "Statement hygiene and balance stability."),
        _metric("Collateral LTV", f"{ltv_ratio:.2f}x" if collateral_value > 0 else "Unsecured", "60-80% funding versus collateral value", collateral_score, "Security coverage on the requested loan."),
    ]

    playbook_layers = [
        _metric("Financial Spreading Readiness", f"{_float(startup.get('financial_spreading_score'), 4.0):.1f}/5", "4/5 or higher", _clamp(_float(startup.get("financial_spreading_score"), 4.0) / 5.0), "Quality of GST, ITR, and balance-sheet data readiness."),
        _metric("Capital Survival", f"{_float(financial.get('runway_months'), 0.0):.1f} mo", "Stable cash flow and sufficient runway", _clamp(0.6 * _clamp(_float(financial.get("runway_months"), 0.0) / 18.0) + 0.4 * dscr_score), "Cash-flow durability."),
        _metric("Customer Diversity", f"{customer_concentration:.1f}%", "<40% single-customer dependence", _clamp((40.0 - customer_concentration) / 25.0), "Revenue concentration risk."),
        _metric("Tax Compliance", f"{tax_compliance:.1f}/5", "4/5 or higher", tax_compliance_score, "GST and income-tax discipline."),
    ]

    red_flags: list[str] = []
    if dscr < 1.0:
        red_flags.append("DSCR is below 1.0, which is an auto-reject for most lenders.")
    if declining_revenue:
        red_flags.append("Revenue has declined across the last three consecutive quarters.")
    if customer_concentration > 40:
        red_flags.append("Customer concentration is above 40% of revenue.")
    if defaults_recent > 0:
        red_flags.append("Recent defaults were reported.")
    if tax_compliance <= 2:
        red_flags.append("Tax compliance appears weak or tax dues may be outstanding.")
    if nbfc_loan_load >= 4:
        red_flags.append("Existing NBFC or micro-loan load is too high.")

    loan_mode_score = (
        0.40 * (0.30 * dscr_score + 0.20 * current_ratio_score + 0.20 * interest_coverage_score + 0.15 * debt_to_equity_score + 0.15 * net_margin_score)
        + 0.25 * (0.45 * credit_score_metric + 0.25 * longevity_score + 0.30 * banking_hygiene_score)
        + 0.20 * (0.50 * tax_compliance_score + 0.25 * collateral_score + 0.25 * _clamp((40.0 - customer_concentration) / 25.0))
        + 0.15 * _float(scores.get("financial_score"), 0.0)
    )
    combined_score = round(loan_mode_score * 100.0, 1)

    if red_flags:
        decision = "REJECT"
    elif dscr > 1.5 and credit_score >= 700 and customer_concentration < 35 and combined_score >= 78:
        decision = "APPROVE"
    elif dscr >= 1.0 and combined_score >= 58:
        decision = "REVIEW"
    else:
        decision = "REJECT"

    risk_band = "Low Risk" if decision == "APPROVE" else "Moderate Risk" if decision == "REVIEW" else "High Risk"

    highlights: list[str] = []
    concerns: list[str] = []
    for metric in solvency_metrics + credit_metrics + playbook_layers:
        if metric["status"] in {"Exceptional", "Strong"} and len(highlights) < 4:
            highlights.append(f'{metric["name"]} is {metric["value"]}, which is {metric["status"].lower()} for SME lending.')
        if metric["status"] == "Weak" and len(concerns) < 4:
            concerns.append(f'{metric["name"]} is {metric["value"]}, below the lending benchmark of {metric["benchmark"]}.')
    concerns.extend(red_flags)
    if not concerns and not red_flags:
        concerns.append("No hard SME lending rejection triggers were detected.")

    diligence_checklist = []
    if decision in {"APPROVE", "REVIEW"}:
        diligence_checklist = [
            "Verify GST, ITR, and audited financial statements through financial spreading.",
            "Review bank statements for cheque bounces, ABB consistency, and EMI servicing behavior.",
            "Validate collateral forced-sale value and loan-to-value fit if the facility is secured.",
            "Check tax compliance, existing loan stack, and customer concentration before sanction.",
        ]

    return {
        "score": combined_score,
        "decision": decision,
        "risk_band": risk_band,
        "solvency_metrics": solvency_metrics,
        "credit_metrics": credit_metrics,
        "playbook_layers": playbook_layers,
        "red_flags": red_flags,
        "highlights": highlights,
        "concerns": concerns,
        "diligence_checklist": diligence_checklist,
        "summary": f"{decision.title()} in SME loan mode with a {combined_score:.1f}/100 credit score and a {risk_band.lower()} profile.",
        "threshold_context": "SME loan mode weights cash-flow survival, credit behavior, and lender red flags ahead of approval.",
        "collateral": {
            "requested_loan_amount": requested_loan_amount,
            "collateral_value": collateral_value,
            "ltv_ratio": round(ltv_ratio, 2) if collateral_value > 0 else None,
        },
    }
