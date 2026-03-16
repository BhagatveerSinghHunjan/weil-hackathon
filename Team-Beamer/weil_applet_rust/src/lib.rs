use serde::{Deserialize, Serialize};
use weil_macros::{constructor, query, smart_contract, WeilType};

trait ChainVestMCP {
    fn new() -> Result<Self, String>
    where
        Self: Sized;

    async fn evaluate_startup(
        &self,
        revenue: f64,
        burn: f64,
        cash: f64,
        business_description: String,
    ) -> StartupEvaluation;
    fn tools(&self) -> String;
    fn prompts(&self) -> String;
}

#[derive(Serialize, Deserialize, WeilType)]
pub struct StartupEvaluation {
    pub decision: String,
    pub score: f64,
    pub financial_score: f64,
    pub business_score: f64,
    pub scalability_score: f64,
    pub market_score: f64,
    pub moat_score: f64,
    pub sector_score: f64,
    pub sector: String,
}

#[derive(Serialize, Deserialize, WeilType, Default)]
pub struct ChainVestMCPContractState {}

fn clamp_non_negative(value: f64) -> f64 {
    if value.is_finite() && value > 0.0 {
        value
    } else {
        0.0
    }
}

fn clamp_score(value: f64) -> f64 {
    value.clamp(0.0, 1.0)
}

fn normalize_text(value: &str) -> String {
    value.to_lowercase().split_whitespace().collect::<Vec<_>>().join(" ")
}

fn score_business_description(description: &str) -> (String, f64, f64, f64, f64, f64) {
    let text = normalize_text(description);
    if text.is_empty() {
        return ("general".to_string(), 0.45, 0.40, 0.40, 0.35, 0.40);
    }

    let mut sector = "general".to_string();
    let mut sector_score = 0.58;
    if ["ai", "artificial intelligence", "llm", "automation"].iter().any(|token| text.contains(token)) {
        sector = "ai".to_string();
        sector_score = 0.74;
    } else if ["fintech", "payments", "banking", "lending", "treasury"].iter().any(|token| text.contains(token)) {
        sector = "fintech".to_string();
        sector_score = 0.72;
    } else if ["health", "healthcare", "clinical", "medical"].iter().any(|token| text.contains(token)) {
        sector = "healthtech".to_string();
        sector_score = 0.70;
    } else if ["software", "saas", "api", "platform"].iter().any(|token| text.contains(token)) {
        sector = "saas".to_string();
        sector_score = 0.66;
    }

    let recurring_bonus = if ["recurring", "subscription", "annual contract", "saas"].iter().any(|token| text.contains(token)) { 0.16 } else { 0.0 };
    let enterprise_bonus = if ["enterprise", "b2b", "workflow", "infrastructure"].iter().any(|token| text.contains(token)) { 0.12 } else { 0.0 };
    let services_penalty = if ["agency", "consulting", "services", "outsourcing"].iter().any(|token| text.contains(token)) { 0.18 } else { 0.0 };
    let scalability_score = clamp_score(0.44 + recurring_bonus + enterprise_bonus - services_penalty);

    let market_score = clamp_score(
        0.42
            + if ["large market", "growing market", "global", "regulated", "mission-critical"].iter().any(|token| text.contains(token)) { 0.18 } else { 0.0 }
            + if ["enterprise", "mid-market", "compliance"].iter().any(|token| text.contains(token)) { 0.08 } else { 0.0 }
    );

    let moat_score = clamp_score(
        0.35
            + if ["moat", "network effects", "proprietary", "data advantage", "switching costs"].iter().any(|token| text.contains(token)) { 0.22 } else { 0.0 }
            + if ["embedded", "integration", "compliance"].iter().any(|token| text.contains(token)) { 0.08 } else { 0.0 }
    );

    let business_score = clamp_score((0.20 * sector_score) + (0.35 * scalability_score) + (0.25 * market_score) + (0.20 * moat_score));
    (sector, sector_score, scalability_score, market_score, moat_score, business_score)
}

fn score_startup(revenue: f64, burn: f64, cash: f64, business_description: &str) -> StartupEvaluation {
    let revenue = clamp_non_negative(revenue);
    let burn = clamp_non_negative(burn);
    let cash = clamp_non_negative(cash);
    let financial_score = clamp_score(((revenue / (burn + 1.0)) * (cash / 10_000.0)) / 8.0);
    let (sector, sector_score, scalability_score, market_score, moat_score, business_score) =
        score_business_description(business_description);
    let score = (0.65 * financial_score) + (0.35 * business_score);
    let decision = if score > 0.75 {
        "APPROVE"
    } else if score > 0.5 {
        "REVIEW"
    } else {
        "REJECT"
    };

    StartupEvaluation {
        decision: decision.to_string(),
        score: (score * 1000.0).round() / 1000.0,
        financial_score: (financial_score * 1000.0).round() / 1000.0,
        business_score: (business_score * 1000.0).round() / 1000.0,
        scalability_score: (scalability_score * 1000.0).round() / 1000.0,
        market_score: (market_score * 1000.0).round() / 1000.0,
        moat_score: (moat_score * 1000.0).round() / 1000.0,
        sector_score: (sector_score * 1000.0).round() / 1000.0,
        sector,
    }
}

#[smart_contract]
impl ChainVestMCP for ChainVestMCPContractState {
    #[constructor]
    fn new() -> Result<Self, String>
    where
        Self: Sized,
    {
        Ok(Self::default())
    }

    #[query]
    async fn evaluate_startup(
        &self,
        revenue: f64,
        burn: f64,
        cash: f64,
        business_description: String,
    ) -> StartupEvaluation {
        score_startup(revenue, burn, cash, &business_description)
    }

    #[query]
    fn tools(&self) -> String {
        r#"[
  {
    "type": "function",
    "function": {
      "name": "evaluate_startup",
      "description": "Evaluate startup health from latest revenue, burn, and cash snapshot.\n",
      "parameters": {
        "type": "object",
        "properties": {
          "revenue": {
            "type": "number",
            "description": "latest recurring or monthly revenue\n"
          },
          "burn": {
            "type": "number",
            "description": "current monthly burn rate\n"
          },
          "cash": {
            "type": "number",
            "description": "current cash reserves\n"
          },
          "business_description": {
            "type": "string",
            "description": "short description of business model, customer, and market\n"
          }
        },
        "required": [
          "revenue",
          "burn",
          "cash",
          "business_description"
        ]
      }
    }
  }
]"#
        .to_string()
    }

    #[query]
    fn prompts(&self) -> String {
        r#"{
  "prompts": []
}"#
        .to_string()
    }
}
