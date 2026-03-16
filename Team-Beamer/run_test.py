from agent.workflow import build_graph


# -------------------------------
# Combined Startup Input Data
# -------------------------------
startup_data = {
    "monthly_revenue": [100,110,120,130,140,150,160,170,180,190,200,210],
    "monthly_burn": [80,85,90,95,100,105,110,115,120,125,130,135],
    "cash_on_hand": 500,
    "business_description": "B2B SaaS finance workflow platform for CFO teams with recurring revenue and strong retention.",
    "ltv": 900,
    "cac": 300,
    "gross_margin": 60,
    "monthly_new_customers": 50
}


# -------------------------------
# Build and Run LangGraph
# -------------------------------
graph = build_graph()

initial_state = {
    "mode": "vc",
    "startup_data": startup_data,
    "financial_result": None,
    "unit_result": None,
    "business_result": None,
    "mcp_result": None,
    "final_score": None,
    "risk_scores": None,
    "vc_assessment": None,
    "decision": None,
    "logs":[],
    "tx_hashes":[],
    "audit_logs":[],
    "planner_history": [],
    "tool_history": [],
    "onchain_audit": [],
    "next_action":None,
    "terminated":False,
    "finished": False,
    "termination_reason": None,
    "iteration_count": 0,
    "max_iterations": 12,

}

result = graph.invoke(initial_state)


# -------------------------------
# Extract Results
# -------------------------------
financial = result["financial_result"]
decision = result["decision"]
score = result["final_score"]


# -------------------------------
# Generate Reasons
# -------------------------------
reasons = []

if financial["runway_months"] < 6:
    reasons.append("Cash runway is less than 6 months.")

if financial["avg_mom_growth"] < 0.05:
    reasons.append("Revenue growth is weak.")

if financial["revenue_volatility"] > 30:
    reasons.append("Revenue shows high volatility.")

if not reasons:
    reasons.append("Financial performance is stable and healthy.")


# -------------------------------
# Clean Structured Output
# -------------------------------
print("\n========== STARTUP RISK EVALUATION ==========\n")

print("Financial Metrics:")
print(f"  • Avg MoM Revenue Growth : {financial['avg_mom_growth']}")
print(f"  • Avg Burn Growth        : {financial['avg_burn_growth']}")
print(f"  • Revenue Volatility     : {financial['revenue_volatility']}")
print(f"  • Runway (months)        : {financial['runway_months']}")

print("\nDecision:")
print(f"  • Final Score : {score}")
print(f"  • Status      : {decision}")

print("\nReason:")
for r in reasons:
    print(f"  • {r}")

print("\nBlockchain Logs:")
for log in result["logs"]:
    print(f"  • {log}")

print("\nTransaction Hashes:")
for tx in result["tx_hashes"]:
    print(f"  • {tx}")    

print("\n==============================================\n")
