export type ChainVestResult = {
  decision?: string;
  final_score?: number;
  decision_reasoning?: {
    summary?: string;
    threshold_context?: string;
    score_breakdown?: {
      overall_score?: number;
      financial_score?: number | string | null;
      unit_score?: number | string | null;
      business_score?: number | string | null;
      vc_score?: number | string | null;
      startup_score?: number | string | null;
      loan_score?: number | string | null;
    };
    highlights?: string[];
    concerns?: string[];
    diligence_checklist?: string[];
  };
  risk_scores?: Record<string, number | string | null | undefined>;
  mode?: string;
  business_result?: {
    sector?: string;
    sector_score?: number;
    scalability_score?: number;
    market_score?: number;
    moat_score?: number;
    traction_score?: number;
    business_score?: number;
    flags?: string[];
  };
  mcp_result?: {
    decision?: string;
    score?: number;
    financial_score?: number;
    business_score?: number;
    scalability_score?: number;
    market_score?: number;
    moat_score?: number;
    sector_score?: number;
    sector?: string;
    audit?: {
      on_chain?: boolean;
      details?: {
        status?: string;
      };
    };
    deployment?: {
      source?: string;
      contract_address?: string | null;
      status?: string;
    };
  };
  vc_assessment?: {
    stage?: string;
    score?: number;
    decision?: string;
    weighting?: {
      label?: string;
      weight?: number;
    }[];
    quantitative_metrics?: {
      name?: string;
      value?: string;
      benchmark?: string;
      status?: string;
      score?: number;
      note?: string;
    }[];
    qualitative_pillars?: {
      name?: string;
      value?: string;
      benchmark?: string;
      status?: string;
      score?: number;
      note?: string;
    }[];
    category_scores?: {
      team_vision?: number;
      market_opportunity?: number;
      early_traction_product?: number;
      unit_efficiency?: number;
      market_dominance?: number;
    };
    red_flags?: string[];
    diligence_checklist?: string[];
  };
  startup_assessment?: {
    stage?: string;
    score?: number;
    decision?: string;
    weighting?: {
      label?: string;
      weight?: number;
    }[];
    quantitative_metrics?: {
      name?: string;
      value?: string;
      benchmark?: string;
      status?: string;
      score?: number;
      note?: string;
    }[];
    qualitative_pillars?: {
      name?: string;
      value?: string;
      benchmark?: string;
      status?: string;
      score?: number;
      note?: string;
    }[];
    diligence_layers?: {
      name?: string;
      value?: string;
      benchmark?: string;
      status?: string;
      score?: number;
      note?: string;
    }[];
    red_flags?: string[];
    diligence_checklist?: string[];
    advanced_valuation?: {
      berkus_estimate?: number;
      scorecard_percentile?: number;
      valuation_drivers?: {
        monthly_revenue?: number;
        monthly_burn?: number;
        cash_available?: number;
        runway_months?: number;
        revenue_scale_score?: number;
        burn_discipline_score?: number;
        cash_reserve_score?: number;
        valuation_financial_signal?: number;
      };
    };
  };
  loan_assessment?: {
    score?: number;
    decision?: string;
    risk_band?: string;
    solvency_metrics?: {
      name?: string;
      value?: string;
      benchmark?: string;
      status?: string;
      score?: number;
      note?: string;
    }[];
    credit_metrics?: {
      name?: string;
      value?: string;
      benchmark?: string;
      status?: string;
      score?: number;
      note?: string;
    }[];
    playbook_layers?: {
      name?: string;
      value?: string;
      benchmark?: string;
      status?: string;
      score?: number;
      note?: string;
    }[];
    red_flags?: string[];
    diligence_checklist?: string[];
    collateral?: {
      requested_loan_amount?: number;
      collateral_value?: number;
      ltv_ratio?: number | null;
    };
  };
  tx_hashes?: string[];
  logs?: string[];
};
