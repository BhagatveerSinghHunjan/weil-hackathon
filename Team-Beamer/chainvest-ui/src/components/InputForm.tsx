"use client";

import { useState, type FormEvent } from "react";

import type { ChainVestResult } from "@/components/types";

type Props = {
  onResult: (data: ChainVestResult) => void;
};

const MODE_OPTIONS = [
  {
    value: "vc",
    label: "Venture Capitalist",
    heading: "Venture Capital Intake",
    description:
      "Enter the core metrics and business context an investor would use to decide whether the company is worth taking into diligence.",
    buttonLabel: "Run VC Analysis",
  },
  {
    value: "startup",
    label: "Startup Evaluation",
    heading: "Startup Evaluation Intake",
    description:
      "Assess overall startup quality using financial health, business fundamentals, and readiness to scale.",
    buttonLabel: "Run Startup Evaluation",
  },
  {
    value: "loan",
    label: "SME Loans",
    heading: "SME Loan Intake",
    description:
      "Review business stability, repayment capacity, and operating context for small-business credit decisions.",
    buttonLabel: "Run SME Loan Analysis",
  },
] as const;

export default function InputForm({ onResult }: Props) {
  const [mode, setMode] = useState("vc");
  const [revenue, setRevenue] = useState("");
  const [burn, setBurn] = useState("");
  const [cash, setCash] = useState("");
  const [businessDescription, setBusinessDescription] = useState("");
  const [companyStage, setCompanyStage] = useState("seed");
  const [arrGrowthRate, setArrGrowthRate] = useState("");
  const [netRevenueRetention, setNetRevenueRetention] = useState("");
  const [ltv, setLtv] = useState("");
  const [cac, setCac] = useState("");
  const [grossMargin, setGrossMargin] = useState("75");
  const [paybackPeriodMonths, setPaybackPeriodMonths] = useState("");
  const [monthlyNewCustomers, setMonthlyNewCustomers] = useState("50");
  const [founderMarketFit, setFounderMarketFit] = useState("4");
  const [executionGrit, setExecutionGrit] = useState("4");
  const [tamSizeBillion, setTamSizeBillion] = useState("");
  const [marketPull, setMarketPull] = useState("4");
  const [moatScoreInput, setMoatScoreInput] = useState("4");
  const [marketTiming, setMarketTiming] = useState("4");
  const [proprietaryDataScore, setProprietaryDataScore] = useState("4");
  const [switchingCostScore, setSwitchingCostScore] = useState("4");
  const [dauMauRatio, setDauMauRatio] = useState("");
  const [thesisAlignment, setThesisAlignment] = useState("4");
  const [tractionValidation, setTractionValidation] = useState("4");
  const [legalHygiene, setLegalHygiene] = useState("4");
  const [customerConcentrationPercent, setCustomerConcentrationPercent] = useState("");
  const [capTableHealth, setCapTableHealth] = useState("4");
  const [prototypeReadiness, setPrototypeReadiness] = useState("4");
  const [strategicRelationships, setStrategicRelationships] = useState("3");
  const [productRollout, setProductRollout] = useState("3");
  const [dscr, setDscr] = useState("");
  const [totalDebtService, setTotalDebtService] = useState("");
  const [currentRatio, setCurrentRatio] = useState("");
  const [debtToEquityRatio, setDebtToEquityRatio] = useState("");
  const [interestCoverageRatio, setInterestCoverageRatio] = useState("");
  const [interestExpense, setInterestExpense] = useState("");
  const [netProfitMargin, setNetProfitMargin] = useState("");
  const [creditScore, setCreditScore] = useState("");
  const [yearsInBusiness, setYearsInBusiness] = useState("3");
  const [chequeBounces, setChequeBounces] = useState("0");
  const [averageBankBalance, setAverageBankBalance] = useState("");
  const [monthlyEmi, setMonthlyEmi] = useState("");
  const [taxComplianceScore, setTaxComplianceScore] = useState("4");
  const [recentDefaults, setRecentDefaults] = useState("0");
  const [nbfcLoanLoad, setNbfcLoanLoad] = useState("1");
  const [collateralValue, setCollateralValue] = useState("");
  const [requestedLoanAmount, setRequestedLoanAmount] = useState("");
  const [financialSpreadingScore, setFinancialSpreadingScore] = useState("4");
  const [loading, setLoading] = useState(false);
  const selectedMode = MODE_OPTIONS.find((option) => option.value === mode) ?? MODE_OPTIONS[0];

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    const res = await fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        mode,
        revenue: Number(revenue),
        burn: Number(burn),
        cash: Number(cash),
        business_description: businessDescription,
        company_stage: companyStage,
        arr_growth_rate: numberOrNull(arrGrowthRate),
        net_revenue_retention: numberOrNull(netRevenueRetention),
        ltv: numberOrNull(ltv),
        cac: numberOrNull(cac),
        gross_margin: numberOrNull(grossMargin),
        payback_period_months: numberOrNull(paybackPeriodMonths),
        monthly_new_customers: Number(monthlyNewCustomers || "50"),
        founder_market_fit: numberOrNull(founderMarketFit),
        execution_grit: numberOrNull(executionGrit),
        tam_size_billion: numberOrNull(tamSizeBillion),
        market_pull: numberOrNull(marketPull),
        moat_score_input: numberOrNull(moatScoreInput),
        market_timing: numberOrNull(marketTiming),
        proprietary_data_score: numberOrNull(proprietaryDataScore),
        switching_cost_score: numberOrNull(switchingCostScore),
        dau_mau_ratio: numberOrNull(dauMauRatio),
        thesis_alignment: numberOrNull(thesisAlignment),
        traction_validation: numberOrNull(tractionValidation),
        legal_hygiene: numberOrNull(legalHygiene),
        customer_concentration_percent: numberOrNull(customerConcentrationPercent),
        cap_table_health: numberOrNull(capTableHealth),
        prototype_readiness: numberOrNull(prototypeReadiness),
        strategic_relationships: numberOrNull(strategicRelationships),
        product_rollout: numberOrNull(productRollout),
        dscr: numberOrNull(dscr),
        total_debt_service: numberOrNull(totalDebtService),
        current_ratio: numberOrNull(currentRatio),
        debt_to_equity_ratio: numberOrNull(debtToEquityRatio),
        interest_coverage_ratio: numberOrNull(interestCoverageRatio),
        interest_expense: numberOrNull(interestExpense),
        net_profit_margin: numberOrNull(netProfitMargin),
        credit_score: numberOrNull(creditScore),
        years_in_business: numberOrNull(yearsInBusiness),
        cheque_bounces: numberOrNull(chequeBounces),
        average_bank_balance: numberOrNull(averageBankBalance),
        monthly_emi: numberOrNull(monthlyEmi),
        tax_compliance_score: numberOrNull(taxComplianceScore),
        recent_defaults: numberOrNull(recentDefaults),
        nbfc_loan_load: numberOrNull(nbfcLoanLoad),
        collateral_value: numberOrNull(collateralValue),
        requested_loan_amount: numberOrNull(requestedLoanAmount),
        financial_spreading_score: numberOrNull(financialSpreadingScore),
      }),
    });

    const data = await res.json();
    onResult(data);
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-xl font-semibold text-gray-900">{selectedMode.heading}</h2>
        <p className="text-sm text-gray-600">{selectedMode.description}</p>
      </div>

      <div className="grid gap-3 rounded-xl border border-emerald-100 bg-emerald-50 p-4 md:grid-cols-4">
        <MetricHint title="Revenue Quality" text="Consistent monthly revenue, healthy growth, repeatability." />
        <MetricHint title="Burn Control" text="Burn that is proportionate to growth and product traction." />
        <MetricHint title="Cash Runway" text="Enough cash to execute, usually 12-18 months is safer." />
        <MetricHint title="Narrative" text="Clear market, wedge, customer pain, and why now." />
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="space-y-2">
            <span className="text-sm font-medium text-gray-800">Evaluation Mode</span>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 focus:ring-emerald-500"
            >
              {MODE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-gray-800">Monthly Revenue</span>
            <input
              type="number"
              placeholder="e.g. 125000"
              value={revenue}
              onChange={(e) => setRevenue(e.target.value)}
              className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 focus:ring-emerald-500"
              required
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-gray-800">Monthly Burn</span>
            <input
              type="number"
              placeholder="e.g. 80000"
              value={burn}
              onChange={(e) => setBurn(e.target.value)}
              className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 focus:ring-emerald-500"
              required
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-gray-800">Cash Available</span>
            <input
              type="number"
              placeholder="e.g. 950000"
              value={cash}
              onChange={(e) => setCash(e.target.value)}
              className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 focus:ring-emerald-500"
              required
            />
          </label>
        </div>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-gray-800">Brief Business Description</span>
          <textarea
            placeholder="Describe what the company does, who the customer is, what problem it solves, how it makes money, and any traction that matters."
            value={businessDescription}
            onChange={(e) => setBusinessDescription(e.target.value)}
            rows={6}
            className="w-full resize-none rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 focus:ring-2 focus:ring-emerald-500"
          />
        </label>

        {mode === "vc" && (
          <div className="space-y-4 rounded-2xl border border-emerald-200 bg-emerald-50/70 p-5">
            <div>
              <h3 className="text-base font-semibold text-gray-900">VC Deep Dive</h3>
              <p className="mt-1 text-sm text-gray-600">
                These extra inputs drive benchmark-based approval, review, and rejection logic in VC mode.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2">
                <span className="text-sm font-medium text-gray-800">Company Stage</span>
                <select
                  value={companyStage}
                  onChange={(e) => setCompanyStage(e.target.value)}
                  className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="seed">Seed</option>
                  <option value="series_b_plus">Series B+</option>
                </select>
              </label>

              <FormField
                label="ARR / MRR Growth (%)"
                placeholder="e.g. 120"
                value={arrGrowthRate}
                onChange={setArrGrowthRate}
              />
              <FormField
                label="Net Revenue Retention (%)"
                placeholder="e.g. 118"
                value={netRevenueRetention}
                onChange={setNetRevenueRetention}
              />
              <FormField label="Gross Margin (%)" placeholder="e.g. 78" value={grossMargin} onChange={setGrossMargin} />
              <FormField label="LTV" placeholder="e.g. 18000" value={ltv} onChange={setLtv} />
              <FormField label="CAC" placeholder="e.g. 4500" value={cac} onChange={setCac} />
              <FormField
                label="Payback Period (months)"
                placeholder="e.g. 9"
                value={paybackPeriodMonths}
                onChange={setPaybackPeriodMonths}
              />
              <FormField
                label="Monthly New Customers"
                placeholder="e.g. 50"
                value={monthlyNewCustomers}
                onChange={setMonthlyNewCustomers}
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <FormField
                label="Founder-Market Fit (1-5)"
                placeholder="e.g. 4"
                value={founderMarketFit}
                onChange={setFounderMarketFit}
              />
              <FormField
                label="TAM Size ($B)"
                placeholder="e.g. 2.5"
                value={tamSizeBillion}
                onChange={setTamSizeBillion}
              />
              <FormField
                label="Defensible Moat (1-5)"
                placeholder="e.g. 4"
                value={moatScoreInput}
                onChange={setMoatScoreInput}
              />
              <FormField
                label="Market Timing (1-5)"
                placeholder="e.g. 4"
                value={marketTiming}
                onChange={setMarketTiming}
              />
              <FormField
                label="Customer Concentration (%)"
                placeholder="e.g. 18"
                value={customerConcentrationPercent}
                onChange={setCustomerConcentrationPercent}
              />
              <FormField
                label="Cap Table Health (1-5)"
                placeholder="e.g. 4"
                value={capTableHealth}
                onChange={setCapTableHealth}
              />
            </div>
          </div>
        )}

        {mode === "startup" && (
          <div className="space-y-4 rounded-2xl border border-emerald-200 bg-emerald-50/70 p-5">
            <div>
              <h3 className="text-base font-semibold text-gray-900">Startup Deep Dive</h3>
              <p className="mt-1 text-sm text-gray-600">
                These inputs drive the startup-evaluation model across qualitative pillars, traction, diligence layers, and valuation methods.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2">
                <span className="text-sm font-medium text-gray-800">Company Stage</span>
                <select
                  value={companyStage}
                  onChange={(e) => setCompanyStage(e.target.value)}
                  className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="pre_seed">Pre-Seed</option>
                  <option value="seed">Seed</option>
                  <option value="series_a">Series A+</option>
                </select>
              </label>

              <FormField label="Founder-Market Fit (1-5)" placeholder="e.g. 4" value={founderMarketFit} onChange={setFounderMarketFit} />
              <FormField label="Execution Grit (1-5)" placeholder="e.g. 4" value={executionGrit} onChange={setExecutionGrit} />
              <FormField label="TAM Size ($B)" placeholder="e.g. 3.5" value={tamSizeBillion} onChange={setTamSizeBillion} />
              <FormField label="Market Pull (1-5)" placeholder="e.g. 4" value={marketPull} onChange={setMarketPull} />
              <FormField label="Proprietary Data (1-5)" placeholder="e.g. 4" value={proprietaryDataScore} onChange={setProprietaryDataScore} />
              <FormField label="Switching Costs (1-5)" placeholder="e.g. 4" value={switchingCostScore} onChange={setSwitchingCostScore} />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <FormField label="ARR / MRR Growth (%)" placeholder="e.g. 90" value={arrGrowthRate} onChange={setArrGrowthRate} />
              <FormField label="Net Revenue Retention (%)" placeholder="e.g. 118" value={netRevenueRetention} onChange={setNetRevenueRetention} />
              <FormField label="LTV" placeholder="e.g. 15000" value={ltv} onChange={setLtv} />
              <FormField label="CAC" placeholder="e.g. 5000" value={cac} onChange={setCac} />
              <FormField label="Payback Period (months)" placeholder="e.g. 10" value={paybackPeriodMonths} onChange={setPaybackPeriodMonths} />
              <FormField label="DAU / MAU Ratio (%)" placeholder="e.g. 16" value={dauMauRatio} onChange={setDauMauRatio} />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <FormField label="Thesis Alignment (1-5)" placeholder="e.g. 4" value={thesisAlignment} onChange={setThesisAlignment} />
              <FormField label="Traction & Validation (1-5)" placeholder="e.g. 4" value={tractionValidation} onChange={setTractionValidation} />
              <FormField label="Legal Hygiene (1-5)" placeholder="e.g. 4" value={legalHygiene} onChange={setLegalHygiene} />
              <FormField label="Cap Table Health (1-5)" placeholder="e.g. 4" value={capTableHealth} onChange={setCapTableHealth} />
              <FormField label="Prototype Readiness (1-5)" placeholder="e.g. 4" value={prototypeReadiness} onChange={setPrototypeReadiness} />
              <FormField label="Strategic Relationships (1-5)" placeholder="e.g. 3" value={strategicRelationships} onChange={setStrategicRelationships} />
              <FormField label="Product Rollout (1-5)" placeholder="e.g. 3" value={productRollout} onChange={setProductRollout} />
              <FormField label="Customer Concentration (%)" placeholder="e.g. 12" value={customerConcentrationPercent} onChange={setCustomerConcentrationPercent} />
            </div>
          </div>
        )}

        {mode === "loan" && (
          <div className="space-y-4 rounded-2xl border border-emerald-200 bg-emerald-50/70 p-5">
            <div>
              <h3 className="text-base font-semibold text-gray-900">SME Loan Deep Dive</h3>
              <p className="mt-1 text-sm text-gray-600">
                These inputs drive solvency checks, credit behavior, collateral evaluation, and lending red-flag screening.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <FormField label="DSCR" placeholder="e.g. 1.4" value={dscr} onChange={setDscr} />
              <FormField label="Total Debt Service" placeholder="e.g. 25000" value={totalDebtService} onChange={setTotalDebtService} />
              <FormField label="Current Ratio" placeholder="e.g. 1.8" value={currentRatio} onChange={setCurrentRatio} />
              <FormField label="Debt-to-Equity Ratio" placeholder="e.g. 1.3" value={debtToEquityRatio} onChange={setDebtToEquityRatio} />
              <FormField label="Interest Coverage Ratio" placeholder="e.g. 3.6" value={interestCoverageRatio} onChange={setInterestCoverageRatio} />
              <FormField label="Interest Expense" placeholder="e.g. 8000" value={interestExpense} onChange={setInterestExpense} />
              <FormField label="Net Profit Margin (%)" placeholder="e.g. 12" value={netProfitMargin} onChange={setNetProfitMargin} />
              <FormField label="Credit Score" placeholder="e.g. 725" value={creditScore} onChange={setCreditScore} />
              <FormField label="Years in Business" placeholder="e.g. 4" value={yearsInBusiness} onChange={setYearsInBusiness} />
              <FormField label="Cheque Bounces" placeholder="e.g. 0" value={chequeBounces} onChange={setChequeBounces} />
              <FormField label="Average Bank Balance" placeholder="e.g. 120000" value={averageBankBalance} onChange={setAverageBankBalance} />
              <FormField label="Monthly EMI" placeholder="e.g. 40000" value={monthlyEmi} onChange={setMonthlyEmi} />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <FormField label="Tax Compliance (1-5)" placeholder="e.g. 4" value={taxComplianceScore} onChange={setTaxComplianceScore} />
              <FormField label="Recent Defaults" placeholder="e.g. 0" value={recentDefaults} onChange={setRecentDefaults} />
              <FormField label="NBFC Loan Load (1-5)" placeholder="e.g. 2" value={nbfcLoanLoad} onChange={setNbfcLoanLoad} />
              <FormField label="Customer Concentration (%)" placeholder="e.g. 22" value={customerConcentrationPercent} onChange={setCustomerConcentrationPercent} />
              <FormField label="Collateral Value" placeholder="e.g. 2500000" value={collateralValue} onChange={setCollateralValue} />
              <FormField label="Requested Loan Amount" placeholder="e.g. 1500000" value={requestedLoanAmount} onChange={setRequestedLoanAmount} />
              <FormField label="Financial Spreading Readiness (1-5)" placeholder="e.g. 4" value={financialSpreadingScore} onChange={setFinancialSpreadingScore} />
            </div>
          </div>
        )}

        <button className="w-full rounded-xl bg-emerald-600 py-3 font-medium text-white transition hover:bg-emerald-700">
          {loading ? "Analyzing..." : selectedMode.buttonLabel}
        </button>
      </form>
    </div>
  );
}

function MetricHint({ title, text }: { title: string; text: string }) {
  return (
    <div className="rounded-lg border border-emerald-200 bg-white/80 p-3">
      <p className="text-sm font-semibold text-gray-900">{title}</p>
      <p className="mt-1 text-xs leading-5 text-gray-600">{text}</p>
    </div>
  );
}

function FormField({
  label,
  placeholder,
  value,
  onChange,
}: {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="space-y-2">
      <span className="text-sm font-medium text-gray-800">{label}</span>
      <input
        type="number"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 focus:ring-emerald-500"
      />
    </label>
  );
}

function numberOrNull(value: string) {
  if (!value.trim()) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}
