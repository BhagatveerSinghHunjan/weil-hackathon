from schemas.financial_input import FinancialInput
from schemas.economics_input import UnitEconomicsInput
from tools.financial_trends import FinancialTrendAnalyzer
from tools.unit_economics import UnitEconomicsEngine

financial_data = FinancialInput(
    monthly_revenue=[100,110,120,130,140,150,160,170,180,190,200,210],
    monthly_burn=[80,85,90,95,100,105,110,115,120,125,130,135],
    cash_on_hand=500
)

financial_tool = FinancialTrendAnalyzer()
print("Financial Analysis:", financial_tool.analyze(financial_data))

economics_data = UnitEconomicsInput(
    ltv=900,
    cac=300,
    gross_margin=60,
    monthly_new_customers=50
)

economics_tool = UnitEconomicsEngine()
print("Unit Economics:", economics_tool.analyze(economics_data))