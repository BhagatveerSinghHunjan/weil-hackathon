from __future__ import annotations

import re


class BusinessAssessmentEngine:
    _SECTOR_KEYWORDS = {
        "fintech": {"fintech", "payments", "banking", "lending", "cfo", "treasury"},
        "healthtech": {"health", "healthcare", "clinical", "hospital", "medical", "ehr"},
        "ai": {"ai", "artificial intelligence", "llm", "machine learning", "automation"},
        "saas": {"saas", "software", "platform", "workflow", "api", "dashboard"},
        "deeptech": {"robotics", "semiconductor", "manufacturing", "infrastructure", "energy"},
        "consumer": {"consumer", "marketplace", "creator", "social", "ecommerce", "commerce"},
    }

    _POSITIVE_MARKERS = {
        "traction": {"growth", "retention", "expansion", "repeat", "recurring", "pipeline", "traction"},
        "distribution": {"sales-led", "product-led", "channel", "partners", "self-serve", "inbound"},
        "defensibility": {"moat", "network effects", "proprietary", "exclusive", "data advantage", "switching costs"},
        "market": {"enterprise", "mid-market", "global", "regulated", "mission-critical", "large market"},
    }

    _RISK_MARKERS = {
        "services": {"agency", "consulting", "services", "custom development", "outsourcing"},
        "concentration": {"single customer", "few customers", "concentrated", "dependency"},
        "unclear": {"idea stage", "pre-revenue", "exploring", "experiment", "pivot"},
    }

    @staticmethod
    def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
        return max(lower, min(value, upper))

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").strip().lower())

    @staticmethod
    def _keyword_score(text: str, keywords: set[str]) -> float:
        return 1.0 if any(keyword in text for keyword in keywords) else 0.0

    def analyze(self, business_description: str, mode: str = "vc") -> dict:
        text = self._normalize(business_description)
        if not text:
            return {
                "sector": "unknown",
                "sector_score": 0.45,
                "scalability_score": 0.4,
                "market_score": 0.4,
                "moat_score": 0.35,
                "traction_score": 0.35,
                "business_score": 40,
                "flags": ["missing_business_description"],
            }

        sector_hits = {
            sector: self._keyword_score(text, keywords)
            for sector, keywords in self._SECTOR_KEYWORDS.items()
        }
        sector = max(sector_hits, key=sector_hits.get)
        sector_score = 0.55
        if sector_hits[sector] > 0:
            sector_score = 0.72 if sector in {"ai", "fintech", "healthtech", "deeptech"} else 0.64

        recurring_bonus = 0.15 if any(token in text for token in {"subscription", "recurring", "saas", "annual contract"}) else 0.0
        enterprise_bonus = 0.1 if any(token in text for token in {"enterprise", "b2b", "workflow", "infrastructure"}) else 0.0
        services_penalty = 0.18 if any(token in text for token in self._RISK_MARKERS["services"]) else 0.0
        scalability_score = self._clamp(0.45 + recurring_bonus + enterprise_bonus - services_penalty)

        market_score = self._clamp(
            0.4
            + 0.18 * self._keyword_score(text, self._POSITIVE_MARKERS["market"])
            + 0.12 * self._keyword_score(text, {"category leader", "growing market", "tailwind", "regulatory tailwind"})
        )

        moat_score = self._clamp(
            0.35
            + 0.22 * self._keyword_score(text, self._POSITIVE_MARKERS["defensibility"])
            + 0.10 * self._keyword_score(text, {"integration", "embedded", "compliance", "workflow lock-in"})
        )

        traction_score = self._clamp(
            0.35
            + 0.2 * self._keyword_score(text, self._POSITIVE_MARKERS["traction"])
            + 0.1 * self._keyword_score(text, self._POSITIVE_MARKERS["distribution"])
        )

        flags: list[str] = []
        if any(token in text for token in self._RISK_MARKERS["concentration"]):
            flags.append("customer_concentration_risk")
            traction_score = self._clamp(traction_score - 0.12)
        if any(token in text for token in self._RISK_MARKERS["unclear"]):
            flags.append("early_or_unclear_positioning")
            market_score = self._clamp(market_score - 0.1)
            moat_score = self._clamp(moat_score - 0.08)
        if mode == "loan":
            market_score = self._clamp(market_score - 0.05)

        business_score = round(
            (
                0.20 * sector_score
                + 0.30 * scalability_score
                + 0.20 * market_score
                + 0.15 * moat_score
                + 0.15 * traction_score
            )
            * 100
        )

        return {
            "sector": sector if sector_hits[sector] > 0 else "general",
            "sector_score": round(sector_score, 3),
            "scalability_score": round(scalability_score, 3),
            "market_score": round(market_score, 3),
            "moat_score": round(moat_score, 3),
            "traction_score": round(traction_score, 3),
            "business_score": business_score,
            "flags": flags,
        }
