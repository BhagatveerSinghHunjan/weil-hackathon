from schemas.economics_input import UnitEconomicsInput


class UnitEconomicsEngine:

    def analyze(self, data: UnitEconomicsInput) -> dict:

        ltv_cac_ratio = data.ltv / data.cac

        gross_profit_per_customer = data.ltv * (data.gross_margin / 100)

        if gross_profit_per_customer == 0:
            payback_period = float("inf")
        else:
            payback_period = data.cac / gross_profit_per_customer

        contribution_margin = gross_profit_per_customer - data.cac

        if ltv_cac_ratio >= 3:
            sustainability_score = 85
        elif 2 <= ltv_cac_ratio < 3:
            sustainability_score = 65
        else:
            sustainability_score = 40

        return {
            "ltv_cac_ratio": round(ltv_cac_ratio, 2),
            "payback_period_months": round(payback_period, 2),
            "contribution_margin": round(contribution_margin, 2),
            "sustainability_score": sustainability_score,
        }