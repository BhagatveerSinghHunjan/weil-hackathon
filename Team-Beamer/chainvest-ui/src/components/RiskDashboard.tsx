import type { ReactNode } from "react";

import type { ChainVestResult } from "@/components/types";

type Props = { result: ChainVestResult };

function DashboardCard({
  title,
  value,
}: {
  title: string;
  value: ReactNode;
}) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <p className="text-sm text-gray-600">{title}</p>
      <p className="text-xl font-semibold text-gray-900">
        {value !== undefined && value !== null && value !== "" ? value : "N/A"}
      </p>
    </div>
  );
}

export default function RiskDashboard({ result }: Props) {
  if (!result) return null;

  const scores = result.risk_scores || {};
  const mcp = result.mcp_result || null;
  const audit = mcp?.audit || null;
  const auditDetails = audit?.details || null;
  const business = result.business_result || null;
  const vc = result.vc_assessment || null;
  const startup = result.startup_assessment || null;
  const loan = result.loan_assessment || null;

  const boolLabel = (value: unknown) => {
    if (value === true) return "YES";
    if (value === false) return "NO";
    return "N/A";
  };

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Risk Overview
      </h2>

      {/* TOP ROW */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <DashboardCard title="Decision" value={result.decision} />
        <DashboardCard title="Overall Score" value={scores.overall_score} />
        <DashboardCard title="Financial Score" value={scores.financial_score} />
        <DashboardCard title="Unit Score" value={scores.unit_score} />
      </div>

      {/* SECOND ROW */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <DashboardCard title="Growth Score" value={scores.growth_score} />
        <DashboardCard title="Runway Score" value={scores.runway_score} />
        <DashboardCard title="Volatility Score" value={scores.volatility_score} />
        <DashboardCard
          title={vc ? "VC Score" : startup ? "Startup Score" : loan ? "Loan Score" : "Business Score"}
          value={vc ? scores.vc_score : startup ? scores.startup_score : loan ? scores.loan_score : scores.business_score}
        />
      </div>

      {vc && (
        <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h3 className="text-md font-semibold text-emerald-900">VC Decision Engine</h3>
            <div className="rounded-full border border-emerald-300 bg-white px-3 py-1 text-sm font-medium text-emerald-900">
              {vc.stage} weighting
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {vc.weighting?.map((item) => (
              <DashboardCard
                key={item.label}
                title={item.label ?? "Weight"}
                value={item.weight ? `${item.weight}%` : "N/A"}
              />
            ))}
          </div>

          {vc.red_flags && vc.red_flags.length > 0 && (
            <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 p-4">
              <h4 className="mb-2 font-semibold text-rose-900">Auto-Reject Red Flags</h4>
              <ul className="list-disc ml-6 space-y-1 text-sm text-rose-900">
                {vc.red_flags.map((flag, index) => (
                  <li key={index}>{flag}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {startup && (
        <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h3 className="text-md font-semibold text-emerald-900">Startup Decision Engine</h3>
            <div className="rounded-full border border-emerald-300 bg-white px-3 py-1 text-sm font-medium text-emerald-900">
              {startup.stage}
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            {startup.weighting?.map((item) => (
              <DashboardCard
                key={item.label}
                title={item.label ?? "Weight"}
                value={item.weight ? `${item.weight}%` : "N/A"}
              />
            ))}
          </div>

          {startup.red_flags && startup.red_flags.length > 0 && (
            <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 p-4">
              <h4 className="mb-2 font-semibold text-rose-900">Startup Red Flags</h4>
              <ul className="list-disc ml-6 space-y-1 text-sm text-rose-900">
                {startup.red_flags.map((flag, index) => (
                  <li key={index}>{flag}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {loan && (
        <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h3 className="text-md font-semibold text-emerald-900">SME Loan Decision Engine</h3>
            <div className="rounded-full border border-emerald-300 bg-white px-3 py-1 text-sm font-medium text-emerald-900">
              {loan.risk_band}
            </div>
          </div>

          {loan.red_flags && loan.red_flags.length > 0 && (
            <div className="rounded-lg border border-rose-200 bg-rose-50 p-4">
              <h4 className="mb-2 font-semibold text-rose-900">Auto-Reject Red Flags</h4>
              <ul className="list-disc ml-6 space-y-1 text-sm text-rose-900">
                {loan.red_flags.map((flag, index) => (
                  <li key={index}>{flag}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {business && (
        <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <h3 className="mb-2 text-md font-semibold text-emerald-900">
            Business Quality Assessment
          </h3>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
            <DashboardCard title="Sector" value={business.sector} />
            <DashboardCard title="Scalability" value={business.scalability_score} />
            <DashboardCard title="Market" value={business.market_score} />
            <DashboardCard title="Moat" value={business.moat_score} />
            <DashboardCard title="Traction" value={business.traction_score} />
          </div>
        </div>
      )}

      {vc && (
        <>
          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="mb-3 text-md font-semibold text-emerald-900">
              VC Benchmarks
            </h3>
            <div className="space-y-3">
              {vc.quantitative_metrics?.map((metric) => (
                <MetricRow key={metric.name} metric={metric} />
              ))}
            </div>
          </div>

          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="mb-3 text-md font-semibold text-emerald-900">
              Qualitative Pillars
            </h3>
            <div className="space-y-3">
              {vc.qualitative_pillars?.map((metric) => (
                <MetricRow key={metric.name} metric={metric} />
              ))}
            </div>
          </div>
        </>
      )}

      {startup && (
        <>
          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="mb-3 text-md font-semibold text-emerald-900">
              Early-Stage Qualitative Pillars
            </h3>
            <div className="space-y-3">
              {startup.qualitative_pillars?.map((metric) => (
                <MetricRow key={metric.name} metric={metric} />
              ))}
            </div>
          </div>

          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="mb-3 text-md font-semibold text-emerald-900">
              Quantitative Performance Metrics
            </h3>
            <div className="space-y-3">
              {startup.quantitative_metrics?.map((metric) => (
                <MetricRow key={metric.name} metric={metric} />
              ))}
            </div>
          </div>

          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="mb-3 text-md font-semibold text-emerald-900">
              Evaluation Playbook
            </h3>
            <div className="space-y-3">
              {startup.diligence_layers?.map((metric) => (
                <MetricRow key={metric.name} metric={metric} />
              ))}
            </div>
          </div>

          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="mb-3 text-md font-semibold text-emerald-900">
              Advanced Valuation Methods
            </h3>
            <div className="grid gap-4 md:grid-cols-2">
              <DashboardCard
                title="Berkus Estimate"
                value={
                  startup.advanced_valuation?.berkus_estimate !== undefined
                    ? `$${startup.advanced_valuation.berkus_estimate.toLocaleString()}`
                    : "N/A"
                }
              />
              <DashboardCard
                title="Scorecard Method"
                value={
                  startup.advanced_valuation?.scorecard_percentile !== undefined
                    ? `${startup.advanced_valuation.scorecard_percentile}%`
                    : "N/A"
                }
              />
            </div>

            {startup.advanced_valuation?.valuation_drivers && (
              <div className="mt-4">
                <h4 className="mb-3 font-semibold text-emerald-900">Valuation Financial Drivers</h4>
                <div className="grid gap-4 md:grid-cols-4">
                  <DashboardCard
                    title="Monthly Revenue"
                    value={formatCurrency(startup.advanced_valuation.valuation_drivers.monthly_revenue)}
                  />
                  <DashboardCard
                    title="Monthly Burn"
                    value={formatCurrency(startup.advanced_valuation.valuation_drivers.monthly_burn)}
                  />
                  <DashboardCard
                    title="Cash Available"
                    value={formatCurrency(startup.advanced_valuation.valuation_drivers.cash_available)}
                  />
                  <DashboardCard
                    title="Runway"
                    value={
                      startup.advanced_valuation.valuation_drivers.runway_months !== undefined
                        ? `${startup.advanced_valuation.valuation_drivers.runway_months} mo`
                        : "N/A"
                    }
                  />
                </div>

                <div className="mt-4 grid gap-4 md:grid-cols-4">
                  <DashboardCard
                    title="Revenue Scale"
                    value={formatPercent(startup.advanced_valuation.valuation_drivers.revenue_scale_score)}
                  />
                  <DashboardCard
                    title="Burn Discipline"
                    value={formatPercent(startup.advanced_valuation.valuation_drivers.burn_discipline_score)}
                  />
                  <DashboardCard
                    title="Cash Reserve"
                    value={formatPercent(startup.advanced_valuation.valuation_drivers.cash_reserve_score)}
                  />
                  <DashboardCard
                    title="Valuation Signal"
                    value={formatPercent(startup.advanced_valuation.valuation_drivers.valuation_financial_signal)}
                  />
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {loan && (
        <>
          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="mb-3 text-md font-semibold text-emerald-900">
              Financial Stability & Solvency
            </h3>
            <div className="space-y-3">
              {loan.solvency_metrics?.map((metric) => (
                <MetricRow key={metric.name} metric={metric} />
              ))}
            </div>
          </div>

          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="mb-3 text-md font-semibold text-emerald-900">
              Credit & Behavioral Metrics
            </h3>
            <div className="space-y-3">
              {loan.credit_metrics?.map((metric) => (
                <MetricRow key={metric.name} metric={metric} />
              ))}
            </div>
          </div>

          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="mb-3 text-md font-semibold text-emerald-900">
              SME Lending Playbook
            </h3>
            <div className="space-y-3">
              {loan.playbook_layers?.map((metric) => (
                <MetricRow key={metric.name} metric={metric} />
              ))}
            </div>
          </div>

          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="mb-3 text-md font-semibold text-emerald-900">
              Collateral Evaluation
            </h3>
            <div className="grid gap-4 md:grid-cols-3">
              <DashboardCard
                title="Requested Loan"
                value={formatCurrency(loan.collateral?.requested_loan_amount)}
              />
              <DashboardCard
                title="Collateral Value"
                value={formatCurrency(loan.collateral?.collateral_value)}
              />
              <DashboardCard
                title="Loan-to-Value"
                value={loan.collateral?.ltv_ratio !== undefined && loan.collateral?.ltv_ratio !== null ? `${loan.collateral.ltv_ratio.toFixed(2)}x` : "Unsecured"}
              />
            </div>
          </div>
        </>
      )}

      {/* 🔥 MCP SECTION */}
      {mcp && (
        <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <h3 className="mb-2 text-md font-semibold text-emerald-900">
            Weil MCP Structured Evaluation
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <DashboardCard title="MCP Decision" value={mcp.decision} />
            <DashboardCard title="MCP Score" value={mcp.score} />
            <DashboardCard title="MCP Financial" value={mcp.financial_score} />
            <DashboardCard title="MCP Business" value={mcp.business_score} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <DashboardCard title="On-Chain Audit" value={boolLabel(audit?.on_chain)} />
            <DashboardCard title="Audit Status" value={auditDetails?.status || "N/A"} />
          </div>
        </div>
      )}
    </div>
  );
}

function formatCurrency(value?: number) {
  if (value === undefined) return "N/A";
  return `$${Math.round(value).toLocaleString()}`;
}

function formatPercent(value?: number) {
  if (value === undefined) return "N/A";
  return `${value}%`;
}

function MetricRow({
  metric,
}: {
  metric: {
    name?: string;
    value?: string;
    benchmark?: string;
    status?: string;
    note?: string;
  };
}) {
  return (
    <div className="rounded-lg border border-emerald-200 bg-white/90 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-gray-900">{metric.name}</p>
          <p className="mt-1 text-sm text-gray-600">{metric.note}</p>
        </div>
        <StatusPill status={metric.status} />
      </div>
      <div className="mt-3 grid gap-3 text-sm text-gray-700 md:grid-cols-2">
        <div>
          <span className="font-medium text-gray-900">Current:</span> {metric.value}
        </div>
        <div>
          <span className="font-medium text-gray-900">Benchmark:</span> {metric.benchmark}
        </div>
      </div>
    </div>
  );
}

function StatusPill({ status }: { status?: string }) {
  const palette =
    status === "Exceptional"
      ? "border-emerald-300 bg-emerald-100 text-emerald-900"
      : status === "Strong"
        ? "border-teal-300 bg-teal-100 text-teal-900"
        : status === "Watch"
          ? "border-amber-300 bg-amber-100 text-amber-900"
          : "border-rose-300 bg-rose-100 text-rose-900";

  return (
    <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${palette}`}>
      {status ?? "N/A"}
    </span>
  );
}
