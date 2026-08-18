"""Explorer metadata: live scenario links and runtime capability behavior."""
from __future__ import annotations

from typing import Any

EXECUTABLE_INTENTS: set[str] = {
    "assess_network_trust",
    "ensure_baggage_connection",
    "maintain_inspection_experience",
    "verify_pharmacy_age_gate",
    "assess_recovery_continuity",
}

LIVE_INTENT_LINKS: dict[str, dict[str, str]] = {
    "assess_network_trust": {
        "enterpriseId": "rocket-bank",
        "useCaseId": "high-value-payment-protection",
        "label": "Rocket Bank trust assessment",
    },
    "assess_recovery_continuity": {
        "enterpriseId": "rocket-bank",
        "useCaseId": "account-recovery-anomaly",
        "label": "Rocket Bank recovery continuity (evidence reuse)",
    },
    "ensure_baggage_connection": {
        "enterpriseId": "high-flight-airlines",
        "useCaseId": "baggage-connection",
        "label": "High Flight baggage connection",
    },
    "maintain_inspection_experience": {
        "enterpriseId": "acme-manufacturing",
        "useCaseId": "critical-inspection-camera",
        "label": "Acme inspection closed loop",
    },
    "verify_pharmacy_age_gate": {
        "enterpriseId": "citycare-health",
        "useCaseId": "pharmacy-age-gate",
        "label": "CityCare age gate",
    },
}

CAPABILITY_LIVE_BEHAVIOR: dict[str, list[dict[str, str]]] = {
    "sim_continuity": [
        {"scenario": "Rocket Bank", "state": "INVOKED", "intentId": "assess_network_trust"},
        {"scenario": "Rocket Bank recovery", "state": "EVIDENCE_REUSED", "intentId": "assess_recovery_continuity"},
    ],
    "device_continuity": [
        {"scenario": "Rocket Bank", "state": "INVOKED", "intentId": "assess_network_trust"},
        {"scenario": "Rocket Bank recovery", "state": "EVIDENCE_REUSED", "intentId": "assess_recovery_continuity"},
    ],
    "roaming_status": [
        {"scenario": "Rocket Bank", "state": "INVOKED", "intentId": "assess_network_trust"},
        {"scenario": "Rocket Bank recovery", "state": "EVIDENCE_REUSED", "intentId": "assess_recovery_continuity"},
    ],
    "location_verification": [
        {"scenario": "Rocket Bank", "state": "BLOCKED_BY_POLICY", "intentId": "assess_network_trust"},
        {"scenario": "High Flight", "state": "BLOCKED_BY_POLICY", "intentId": "ensure_baggage_connection"},
    ],
    "quality_on_demand": [
        {"scenario": "High Flight", "state": "NOT_REQUIRED", "intentId": "ensure_baggage_connection"},
        {"scenario": "Acme", "state": "INVOKED", "intentId": "maintain_inspection_experience"},
    ],
    "age_verification": [
        {"scenario": "CityCare", "state": "SELECTED", "intentId": "verify_pharmacy_age_gate"},
    ],
    "kyc_match": [
        {"scenario": "CityCare", "state": "BLOCKED_BY_POLICY", "intentId": "verify_pharmacy_age_gate"},
    ],
    "connectivity_insights": [
        {"scenario": "High Flight", "state": "INVOKED", "intentId": "ensure_baggage_connection"},
        {"scenario": "Acme", "state": "INVOKED", "intentId": "maintain_inspection_experience"},
    ],
}

OPERATION_LIVE_HINTS: dict[str, str] = {
    "checkSimSwap": "Invoked in Rocket Bank; reused in recovery continuity",
    "verifyLocation": "Policy block in Rocket Bank and High Flight",
    "createSession": "Autonomous QoD in Acme after objective breach",
    "verifyAge": "Minimum capability selection in CityCare",
    "KYC_Match": "Blocked in CityCare — broader than required",
}

DOMAIN_LIVE_DEMOS: dict[str, dict[str, str]] = {
    "financial": {"enterpriseId": "rocket-bank", "useCaseId": "high-value-payment-protection", "label": "Run Rocket Bank demo"},
    "airlines": {"enterpriseId": "high-flight-airlines", "useCaseId": "baggage-connection", "label": "Run High Flight demo"},
    "manufacturing": {"enterpriseId": "acme-manufacturing", "useCaseId": "critical-inspection-camera", "label": "Run Acme demo"},
    "healthcare": {"enterpriseId": "citycare-health", "useCaseId": "pharmacy-age-gate", "label": "Run CityCare demo"},
}

EVIDENCE_GRADE_LABELS = {
    "SOURCE_BACKED": "SB",
    "INFERRED": "INF",
    "NEEDS_REVIEW": "NR",
}


def live_link_for_intent(intent_id: str) -> dict[str, str] | None:
    if intent_id not in EXECUTABLE_INTENTS:
        return None
    return LIVE_INTENT_LINKS.get(intent_id)


def evidence_grade_label(grade: str | None) -> dict[str, str]:
    g = str(grade or "")
    return {
        "raw": g,
        "short": EVIDENCE_GRADE_LABELS.get(g, g[:3] if g else ""),
        "note": "INFERRED mappings are configuration hypotheses, not CAMARA-defined business use cases."
        if g == "INFERRED"
        else "",
    }
