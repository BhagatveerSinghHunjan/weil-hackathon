import statistics
from schemas.financial_input import FinancialInput


class FinancialTrendAnalyzer:

    def analyze(self, data: FinancialInput) -> dict:

        revenue = data.monthly_revenue
        burn = data.monthly_burn
        cash = data.cash_on_hand

        revenue_growth_rates = []
        for i in range(1, len(revenue)):
            previous = revenue[i - 1]
            current = revenue[i]

            if previous == 0:
                growth = 0
            else:
                growth = (current - previous) / previous

            revenue_growth_rates.append(growth)

        avg_mom_growth = sum(revenue_growth_rates) / len(revenue_growth_rates)

        burn_growth_rates = []
        for i in range(1, len(burn)):
            previous = burn[i - 1]
            current = burn[i]

            if previous == 0:
                growth = 0
            else:
                growth = (current - previous) / previous

            burn_growth_rates.append(growth)

        avg_burn_growth = sum(burn_growth_rates) / len(burn_growth_rates)

        revenue_volatility = statistics.stdev(revenue)

        avg_burn = sum(burn) / len(burn)

        if avg_burn == 0:
            runway = float("inf")
        else:
            runway = cash / avg_burn

        return {
            "avg_mom_growth": round(avg_mom_growth, 4),
            "avg_burn_growth": round(avg_burn_growth, 4),
            "revenue_volatility": round(revenue_volatility, 2),
            "runway_months": round(runway, 2),
        }