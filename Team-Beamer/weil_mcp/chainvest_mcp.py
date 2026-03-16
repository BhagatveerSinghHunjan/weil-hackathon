from __future__ import annotations

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Optional

try:
    from weil_wallet import PrivateKey, Wallet, WeilClient

    WEIL_WALLET_AVAILABLE = True
except Exception:
    PrivateKey = Wallet = WeilClient = None  # type: ignore[assignment]
    WEIL_WALLET_AVAILABLE = False

try:
    from fastmcp import FastMCP
except Exception:
    FastMCP = None  # type: ignore[assignment]

try:
    from weil_ai.mcp import secured, weil_middleware
except Exception:
    secured = None  # type: ignore[assignment]
    weil_middleware = None  # type: ignore[assignment]


def _safe_float(value: Any, *, minimum: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = minimum
    return max(parsed, minimum)


def _normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _clamp_score(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(value, upper))


def _score_business_description(description: str) -> dict[str, Any]:
    text = _normalize_text(description)
    if not text:
        return {
            "sector": "general",
            "sector_score": 0.45,
            "scalability_score": 0.4,
            "market_score": 0.4,
            "moat_score": 0.35,
            "business_score": 0.4,
        }

    sector = "general"
    sector_score = 0.58
    if any(token in text for token in {"ai", "artificial intelligence", "llm", "automation"}):
        sector = "ai"
        sector_score = 0.74
    elif any(token in text for token in {"fintech", "payments", "banking", "lending", "treasury"}):
        sector = "fintech"
        sector_score = 0.72
    elif any(token in text for token in {"health", "healthcare", "clinical", "medical"}):
        sector = "healthtech"
        sector_score = 0.70
    elif any(token in text for token in {"software", "saas", "api", "platform"}):
        sector = "saas"
        sector_score = 0.66

    recurring_bonus = 0.16 if any(token in text for token in {"recurring", "subscription", "annual contract", "saas"}) else 0.0
    enterprise_bonus = 0.12 if any(token in text for token in {"enterprise", "b2b", "workflow", "infrastructure"}) else 0.0
    services_penalty = 0.18 if any(token in text for token in {"agency", "consulting", "services", "outsourcing"}) else 0.0
    scalability_score = _clamp_score(0.44 + recurring_bonus + enterprise_bonus - services_penalty)

    market_score = _clamp_score(
        0.42
        + (0.18 if any(token in text for token in {"large market", "growing market", "global", "regulated", "mission-critical"}) else 0.0)
        + (0.08 if any(token in text for token in {"enterprise", "mid-market", "compliance"}) else 0.0)
    )

    moat_score = _clamp_score(
        0.35
        + (0.22 if any(token in text for token in {"moat", "network effects", "proprietary", "data advantage", "switching costs"}) else 0.0)
        + (0.08 if any(token in text for token in {"embedded", "integration", "compliance"}) else 0.0)
    )

    business_score = _clamp_score(
        (0.20 * sector_score) + (0.35 * scalability_score) + (0.25 * market_score) + (0.20 * moat_score)
    )

    return {
        "sector": sector,
        "sector_score": round(sector_score, 3),
        "scalability_score": round(scalability_score, 3),
        "market_score": round(market_score, 3),
        "moat_score": round(moat_score, 3),
        "business_score": round(business_score, 3),
    }


def _score_startup(revenue: float, burn: float, cash: float, business_description: str) -> dict[str, Any]:
    financial_score = _clamp_score((revenue / (burn + 1.0)) * (cash / 10000.0) / 8.0)
    business = _score_business_description(business_description)
    score = (0.65 * financial_score) + (0.35 * business["business_score"])

    if score > 0.75:
        decision = "APPROVE"
    elif score > 0.5:
        decision = "REVIEW"
    else:
        decision = "REJECT"

    return {
        "decision": decision,
        "score": round(score, 3),
        "financial_score": round(financial_score, 3),
        "business_score": business["business_score"],
        "scalability_score": business["scalability_score"],
        "market_score": business["market_score"],
        "moat_score": business["moat_score"],
        "sector_score": business["sector_score"],
        "sector": business["sector"],
    }


def _resolve_private_key_path() -> Optional[str]:
    candidates = [
        os.getenv("WEIL_PRIVATE_KEY_PATH"),
        os.getenv("WEIL_PRIVATE_KEY_FILE"),
        os.path.join(os.getcwd(), "private_key.wc"),
        os.path.join(os.path.dirname(__file__), "private_key.wc"),
    ]

    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def _run_sync(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    # If already inside an event loop, run in a worker thread.
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


async def _audit_on_weil(payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    if not WEIL_WALLET_AVAILABLE:
        return None

    key_path = _resolve_private_key_path()
    if not key_path:
        return None

    sentinel_host = os.getenv("WEIL_SENTINEL_HOST")
    verify_tls = os.getenv("WEIL_SENTINEL_VERIFY", "true").lower() not in {
        "0",
        "false",
        "no",
    }

    try:
        pk = PrivateKey.from_file(key_path)
        wallet = Wallet(pk)

        kwargs = {"verify": verify_tls}
        if sentinel_host:
            kwargs["sentinel_host"] = sentinel_host

        async with WeilClient(wallet, **kwargs) as client:
            tx = await client.audit(json.dumps(payload))
            return {
                "status": str(getattr(tx, "status", "UNKNOWN")),
                "block_height": getattr(tx, "block_height", None),
                "batch_id": getattr(tx, "batch_id", None),
                "tx_idx": getattr(tx, "tx_idx", None),
                "creation_time": getattr(tx, "creation_time", None),
                "txn_result": getattr(tx, "txn_result", None),
            }
    except Exception as exc:
        return {"error": str(exc)}


def evaluate_startup(revenue: float, burn: float, cash: float, business_description: str = "") -> dict[str, Any]:
    revenue = _safe_float(revenue)
    burn = _safe_float(burn)
    cash = _safe_float(cash)

    result = _score_startup(revenue, burn, cash, business_description)
    payload = {
        "source": "chainvest",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "revenue": revenue,
            "burn": burn,
            "cash": cash,
            "business_description": business_description,
        },
        "evaluation": result,
    }

    result["audit"] = {
        "enabled": WEIL_WALLET_AVAILABLE,
        "key_found": _resolve_private_key_path() is not None,
        "on_chain": False,
    }

    onchain = _run_sync(_audit_on_weil(payload))
    if onchain:
        result["audit"]["on_chain"] = "error" not in onchain
        result["audit"]["details"] = onchain

    return result


def create_mcp_app():
    if FastMCP is None:
        raise RuntimeError("fastmcp is not installed. Install it to run ChainVest MCP.")

    mcp = FastMCP("chainvest-mcp")
    secured_service = os.getenv("WEIL_MCP_SERVICE_NAME")

    if secured is not None and secured_service:

        @mcp.tool()
        @secured(secured_service)
        async def evaluate_startup_tool(revenue: float, burn: float, cash: float, business_description: str = "") -> str:
            return json.dumps(evaluate_startup(revenue, burn, cash, business_description))

    else:

        @mcp.tool()
        async def evaluate_startup_tool(revenue: float, burn: float, cash: float, business_description: str = "") -> str:
            return json.dumps(evaluate_startup(revenue, burn, cash, business_description))

    app = mcp.http_app(transport="streamable-http")
    if weil_middleware is not None:
        app.add_middleware(weil_middleware())
    return app


__all__ = ["create_mcp_app", "evaluate_startup"]


if __name__ == "__main__":
    import uvicorn

    app = create_mcp_app()
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("MCP_PORT", "8001")))
