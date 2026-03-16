from schemas.economics_input import UnitEconomicsInput


class UnitEconomicsEngine:
    @staticmethod
    def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
        return max(lower, min(value, upper))

    def analyze(self, data: UnitEconomicsInput) -> dict:
        ltv_cac_ratio = data.ltv / data.cac

        gross_profit_per_customer = data.ltv * (data.gross_margin / 100)

        if gross_profit_per_customer == 0:
            payback_period = float("inf")
        else:
            payback_period = data.cac / gross_profit_per_customer

        contribution_margin = gross_profit_per_customer - data.cac

        ratio_score = self._clamp((ltv_cac_ratio - 1.0) / 4.0)
        payback_score = 0.0 if payback_period == float("inf") else self._clamp(1.0 - (payback_period / 24.0))
        margin_base = gross_profit_per_customer if gross_profit_per_customer > 0 else max(data.cac, 1.0)
        contribution_score = self._clamp(contribution_margin / margin_base)

        sustainability_score = round(
            ((0.45 * ratio_score) + (0.35 * payback_score) + (0.20 * contribution_score)) * 100
        )

        return {
            "ltv_cac_ratio": round(ltv_cac_ratio, 2),
            "payback_period_months": round(payback_period, 2),
            "contribution_margin": round(contribution_margin, 2),
            "ratio_score": round(ratio_score, 3),
            "payback_score": round(payback_score, 3),
            "contribution_score": round(contribution_score, 3),
            "sustainability_score": sustainability_score,
        }
