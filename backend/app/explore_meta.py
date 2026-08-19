"""Explorer metadata: live scenario links and runtime capability behavior."""
from __future__ import annotations

from typing import Any

EXECUTABLE_INTENTS: set[str] = {
    "assess_network_trust",
    "ensure_baggage_connection",
    "maintain_inspection_experience",
    "verify_pharmacy_age_gate",
    "assess_recovery_continuity",
    "verify_mobile_number",
    "prepare_ota_cohort",
    "assure_delivery_device",
    "assess_checkout_trust",
    "assess_claim_device_trust",
    "assure_ground_device",
    "assure_technician_device",
    "assure_live_broadcast",
}

LIVE_INTENT_LINKS: dict[str, dict[str, str]] = {
    "verify_mobile_number": {
        "enterpriseId": "rocket-bank",
        "useCaseId": "passwordless-mobile-sign-in",
        "label": "Passwordless mobile sign-in",
    },
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
    "prepare_ota_cohort": {
        "enterpriseId": "acme-manufacturing",
        "useCaseId": "fleet-firmware-rollout",
        "label": "Acme fleet firmware rollout",
    },
    "assure_delivery_device": {
        "enterpriseId": "swiftship-logistics",
        "useCaseId": "delivery-device-readiness",
        "label": "SwiftShip delivery device readiness",
    },
    "assess_checkout_trust": {
        "enterpriseId": "megamart-retail",
        "useCaseId": "checkout-trust",
        "label": "MegaMart checkout trust",
    },
    "assess_claim_device_trust": {
        "enterpriseId": "northstar-insurance",
        "useCaseId": "claim-device-trust",
        "label": "Northstar digital claim trust",
    },
    "assure_ground_device": {
        "enterpriseId": "high-flight-airlines",
        "useCaseId": "ground-device-readiness",
        "label": "High Flight ground device readiness",
    },
    "assure_technician_device": {
        "enterpriseId": "acme-manufacturing",
        "useCaseId": "connected-maintenance",
        "label": "Acme connected maintenance",
    },
    "assure_live_broadcast": {
        "enterpriseId": "apex-media",
        "useCaseId": "live-broadcast",
        "label": "Apex live contribution",
    },
}

CAPABILITY_LIVE_BEHAVIOR: dict[str, list[dict[str, str]]] = {
    "number_possession_verification": [
        {"scenario": "Passwordless mobile sign-in", "state": "PATH_SELECTED", "intentId": "verify_mobile_number"},
        {"scenario": "Rocket Bank", "state": "INVOKED", "intentId": "assess_network_trust"},
    ],
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
        {"scenario": "Acme OTA cohort", "state": "INVOKED", "intentId": "prepare_ota_cohort"},
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
        {"scenario": "Acme OTA cohort", "state": "NOT_REQUIRED", "intentId": "prepare_ota_cohort"},
    ],
    "device_reachability": [
        {"scenario": "High Flight", "state": "INVOKED", "intentId": "ensure_baggage_connection"},
        {"scenario": "Acme OTA cohort", "state": "INVOKED", "intentId": "prepare_ota_cohort"},
        {"scenario": "SwiftShip delivery", "state": "INVOKED", "intentId": "assure_delivery_device"},
    ],
}

OPERATION_LIVE_HINTS: dict[str, str] = {
    "phoneNumberVerify": "Claimed-MSISDN operation in Number Verification path selection — not equal to NV1",
    "phoneNumberShare": "Share is not NV2. Claimed number uses verify.",
    "checkSimSwap": "Invoked in Rocket Bank; reused in recovery continuity",
    "verifyLocation": "Policy block in Rocket Bank and High Flight",
    "createSession": "Autonomous QoD in Acme after objective breach",
    "verifyAge": "Minimum capability selection in CityCare",
    "KYC_Match": "Blocked in CityCare — broader than required",
    "getReachabilityStatus": "Primary OTA cohort evidence and High Flight scanner operability",
    "getRoamingStatus": "OTA policy interpretation; also Rocket Bank continuity",
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

DISCOVERY_LINKS: dict[str, dict[str, str]] = {
    "verify_mobile_number": {
        "label": "See Number Verification path Discovery",
        "note": "Same Intent. Cellular selects NV1. Wi-Fi selects NV2 when the operator is ready.",
        **LIVE_INTENT_LINKS["verify_mobile_number"],
    },
    "assess_network_trust": {
        "label": "See Discovery model",
        "note": "Rocket Bank — relevant, allowed, available, useful, selected.",
        **LIVE_INTENT_LINKS["assess_network_trust"],
    },
    "assess_recovery_continuity": {
        "label": "See evidence reuse in Discovery",
        "note": "SIM continuity reused — invocation skipped.",
        **LIVE_INTENT_LINKS["assess_recovery_continuity"],
    },
    "ensure_baggage_connection": {
        "label": "See Discovery model",
        "note": "Secondary example — location consent-filtered; QoD not required.",
        **LIVE_INTENT_LINKS["ensure_baggage_connection"],
    },
    "maintain_inspection_experience": {
        "label": "See Discovery over time",
        "note": "QoD starts NOT_REQUIRED, then SELECTED after breach.",
        **LIVE_INTENT_LINKS["maintain_inspection_experience"],
    },
    "verify_pharmacy_age_gate": {
        "label": "See Discovery model",
        "note": "Age selected; KYC filtered — availability is not permission or need.",
        **LIVE_INTENT_LINKS["verify_pharmacy_age_gate"],
    },
    "prepare_ota_cohort": {
        "label": "See fleet firmware Discovery",
        "note": "Reachability and Roaming qualify a simulated OTA cohort. QoD and Location are not required.",
        **LIVE_INTENT_LINKS["prepare_ota_cohort"],
    },
}

CAPABILITY_DISCOVERY_NOTES: dict[str, str] = {
    "number_possession_verification": "Used in live Discovery — selected for Rocket Bank evidence, and as the NV path-selection capability.",
    "sim_continuity": "Used in live Discovery — invoked for trust, reused for recovery.",
    "device_continuity": "Used in live Discovery — invoked for trust, reused for recovery.",
    "device_identifier": "Used in live Discovery — selected for Rocket Bank evidence.",
    "roaming_status": "Used in live Discovery — selected for Rocket Bank evidence and Acme OTA cohort policy interpretation.",
    "connectivity_insights": "Used in live Discovery — selected in High Flight and Acme.",
}

FAMILY_DISCOVERY_NOTES: dict[str, str] = {
    "sim-swap": "See selected / reused examples in Rocket Bank Discovery.",
    "device-swap": "See selected / reused examples in Rocket Bank Discovery.",
    "number-verification": "See path vs operation in passwordless mobile sign-in. NV1/NV2 are paths, not verify/share.",
    "device-identifier": "See selected example in Rocket Bank Discovery.",
    "roaming": "See selected / reused examples in Rocket Bank Discovery.",
    "number-recycling": "See filtered example (not required) in Rocket Bank Discovery.",
    "location": "See filtered examples (consent missing) in Rocket Bank and High Flight Discovery.",
    "quality-on-demand": "See dynamic usefulness in Acme Discovery; NOT_REQUIRED in High Flight.",
    "age-verification": "See selected example in CityCare Discovery.",
    "kyc-match": "See filtered example in CityCare Discovery.",
    "reachability": "See selected examples in High Flight and Acme fleet firmware Discovery.",
    "roaming": "See selected / reused examples in Rocket Bank Discovery, and policy interpretation in Acme OTA.",
    "connectivity-insights": "See selected examples in High Flight and Acme Discovery.",
}

POLICY_DISCOVERY_NOTES: dict[str, str] = {
    "rocket-bank-iam-policy": "See Number Verification path selection — NV1 vs NV2 vs ECS gap.",
    "rocket-bank-trust-policy": "See where Location was filtered in live Discovery (consent missing).",
    "high-flight-baggage-policy": "See where Location was filtered in live Discovery (consent missing).",
    "citycare-pharmacy-policy": "See where KYC Match was filtered in live Discovery (broader than required).",
    "acme-inspection-policy": "See QoD move from NOT_REQUIRED to SELECTED in live Discovery.",
    "acme-ota-policy": "See Reachability / Roaming cohort qualification. QoD and Location are not required.",
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
