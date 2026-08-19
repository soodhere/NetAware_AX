"""Cadence 10 — Intent Profile loader and trace attachment.

Profiles describe and constrain existing runtime behavior.
They are not a second planner and are not sent on the HTTP request.
"""
from __future__ import annotations

from typing import Any

from .config import MODEL_DIR, SCHEMAS_DIR

LIVE_PROFILE_INTENTS = (
    "verify_mobile_number",
    "assess_network_trust",
    "assess_recovery_continuity",
    "maintain_inspection_experience",
    "verify_pharmacy_age_gate",
    "ensure_baggage_connection",
    "prepare_ota_cohort",
)

PRESENTATION_LENS = {
    "BASIC": "BUSINESS_VIEW",
    "ADVANCED": "TECHNICAL_VIEW",
}

POLICY_LAYERS = (
    "GLOBAL / PLATFORM",
    "ENTERPRISE",
    "APPLICATION",
    "INTENT",
    "REGION",
    "PURPOSE / DATA",
    "AGENT DELEGATION",
    "COMMERCIAL",
    "RUNTIME",
    "AUTONOMY",
)


def load_intent_profiles() -> list[dict[str, Any]]:
    import yaml

    path = MODEL_DIR / "intent-profiles.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return list(data.get("intentProfiles") or [])


def profile_schema_path():
    return SCHEMAS_DIR / "intent-profile.json"


def public_profile(profile: dict[str, Any] | None) -> dict[str, Any] | None:
    if not profile:
        return None
    return {
        "intentId": profile.get("intentId"),
        "label": profile.get("label"),
        "businessOutcome": profile.get("businessOutcome"),
        "complexity": profile.get("complexity"),
        "scenarioComplexity": profile.get("complexity"),
        "enterpriseId": profile.get("enterpriseId"),
        "applicationId": profile.get("applicationId"),
        "authorizedActors": list(profile.get("authorizedActors") or []),
        "purposeId": profile.get("purposeId"),
        "regions": list(profile.get("regions") or []),
        "candidateCapabilities": list(profile.get("candidateCapabilities") or []),
        "minimumEvidence": list(profile.get("minimumEvidence") or []),
        "optionalEvidence": list(profile.get("optionalEvidence") or []),
        "dataMinimization": bool(profile.get("dataMinimization")),
        "reusePolicy": profile.get("reusePolicy") or {},
        "failurePolicy": profile.get("failurePolicy"),
        "autonomy": profile.get("autonomy"),
        "decisionOwner": profile.get("decisionOwner"),
        "verificationRequirement": profile.get("verificationRequirement"),
        "networkContributionTier": profile.get("networkContributionTier"),
        "workingAlias": profile.get("workingAlias"),
        "note": profile.get("note"),
        "source": "FROM ONBOARDING / CONFIGURATION",
        "notARuntimeRequest": True,
        "notASecondPlanner": True,
    }


def layer_for_evaluation(row: dict[str, Any]) -> str:
    if row.get("layer"):
        return str(row["layer"])
    stage = str(row.get("stage") or "")
    subject = str(row.get("subject") or "").lower()
    if stage == "AUTONOMY_ACTION":
        return "AUTONOMY"
    if stage == "EVIDENCE_REUSE":
        return "PURPOSE / DATA"
    if stage == "ACTOR_INTENT":
        if "purpose" in subject:
            return "PURPOSE / DATA"
        if "intent" in subject:
            return "INTENT"
        if "agent" in subject or "actor" in subject:
            return "AGENT DELEGATION"
        return "APPLICATION"
    if stage == "CAPABILITY_API":
        if "consent" in subject or "agreement" in subject:
            return "PURPOSE / DATA"
        if "entitlement" in subject or "subscription" in subject:
            return "COMMERCIAL"
        return "PURPOSE / DATA"
    source = str(row.get("source") or "").upper()
    if "RUNTIME" in source or "FINDER" in source:
        return "RUNTIME"
    if "PLATFORM" in source or "CATALOG" in source:
        return "GLOBAL / PLATFORM"
    return "RUNTIME"


def five_states_from_discovery(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event in payload.get("discovery") or []:
        if event.get("stage") != "SELECT":
            continue
        checks = event.get("checks") or {}
        reason = str(event.get("reasonCode") or "")
        action = str(event.get("action") or "")
        if reason == "OPERATOR_NOT_SUPPORTED" or event.get("result") == "UNAVAILABLE":
            action = "UNAVAILABLE"
        needed = "YES"
        if reason in {"NOT_REQUIRED", "NOT_RELEVANT"}:
            needed = "NO"
        elif reason == "EVIDENCE_REUSED":
            needed = "ALREADY_HAVE"
        rows.append(
            {
                "candidate": event.get("candidate") or event.get("capability"),
                "capability": event.get("capability"),
                "relevant": checks.get("relevance") or ("YES" if reason != "NOT_RELEVANT" else "NO"),
                "available": checks.get("apiFinder") or "—",
                "entitled": checks.get("entitlement") or "—",
                "permitted": checks.get("policy") or checks.get("purpose") or "—",
                "needed": needed,
                "action": action,
                "reasonCode": reason,
            }
        )
    return rows


def attach_intent_profile(payload: dict[str, Any], store: Any) -> dict[str, Any]:
    intent_id = str(payload.get("intentId") or "")
    profile = (getattr(store, "intent_profile_by_id", {}) or {}).get(intent_id)
    public = public_profile(profile)
    gap = (profile or {}).get("decisionGap")
    policies = []
    for row in payload.get("policyEvaluations") or []:
        item = dict(row)
        item["layer"] = layer_for_evaluation(item)
        policies.append(item)
    body = {
        **payload,
        "intentProfile": public,
        "decisionGap": gap,
        "scenarioComplexity": (profile or {}).get("complexity"),
        "presentationLens": {
            "BASIC": "BUSINESS_VIEW",
            "ADVANCED": "TECHNICAL_VIEW",
            "note": "Lens is presentation depth of the same trace. Complexity is a different dimension.",
        },
        "policyEvaluations": policies or payload.get("policyEvaluations"),
        "candidateFiveStates": five_states_from_discovery(payload),
    }
    if intent_id == "ensure_baggage_connection":
        demand = payload.get("demandSupply") or payload.get("networkOpportunity") or {}
        if demand and "apiSuccessfullyReportedUnreachable" not in demand:
            body["demandSupply"] = {
                **demand,
                "note": "API success that reports a device unreachable is fulfilled demand, not unfulfilled demand.",
            }
    return body
