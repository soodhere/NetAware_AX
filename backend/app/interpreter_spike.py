"""Cadence 10 spike — configuration-driven interpreter.

Read-only / parallel. Does not replace live runners and must not fork outcomes.
Used to prove BASIC/COMPOSED cases can be described from IntentProfile without
a dedicated Python engine per use case.
"""
from __future__ import annotations

from typing import Any


def interpret_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Emit expected CALL / FILTER / SKIP actions from profile roles only."""
    actions: list[dict[str, Any]] = []
    minimize = bool(profile.get("dataMinimization"))
    for row in profile.get("candidateCapabilities") or []:
        cap_id = str(row.get("id") or "")
        role = str(row.get("role") or "considered")
        if role == "required":
            action = "CALL"
            reason = "minimum evidence for this Intent"
        elif minimize:
            action = "FILTER"
            reason = "broader than required — data minimization"
        else:
            action = "SKIP"
            reason = "considered, not required"
        actions.append({"capabilityId": cap_id, "role": role, "action": action, "reason": reason})
    return {
        "intentId": profile.get("intentId"),
        "source": "INTENT_PROFILE_SPIKE",
        "notALiveRunner": True,
        "actions": actions,
        "decisionGap": profile.get("decisionGap"),
        "complexity": profile.get("complexity"),
    }


def citycare_spike_agrees_with_live(profile: dict[str, Any], live_outcome: str) -> bool:
    """Spike may describe Age CALL / KYC FILTER. It must not change ELIGIBLE."""
    interpreted = interpret_profile(profile)
    by_cap = {row["capabilityId"]: row["action"] for row in interpreted["actions"]}
    if by_cap.get("age_verification") != "CALL":
        return False
    if by_cap.get("kyc_match") != "FILTER":
        return False
    return live_outcome == "ELIGIBLE"
