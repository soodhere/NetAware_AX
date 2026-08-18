"""Cadence 8 — structured discovery[] view of existing runtime decisions.

Not a second decision engine. Maps the same policy/selection results already
used by live runners into Cadence 7 stage groups and reason codes.
"""
from __future__ import annotations

from typing import Any

from .graph import KnowledgeGraph
from .model import ConfigStore
from .registry import CatalogRegistry

STAGE_GROUPS = (
    "CANDIDATE_GENERATION",
    "CONFIGURED_ELIGIBILITY",
    "RUNTIME_FEASIBILITY",
    "SELECT",
)

REASON_CODES = {
    "NOT_RELEVANT",
    "PURPOSE_NOT_PERMITTED",
    "NOT_SUBSCRIBED",
    "NOT_ENTITLED",
    "CONSENT_MISSING",
    "AGREEMENT_GAP",
    "REGION_NOT_SUPPORTED",
    "PROVIDER_NOT_AVAILABLE",
    "OPERATOR_NOT_SUPPORTED",
    "ENTITLEMENT_SERVER_UNAVAILABLE",
    "ACCESS_TYPE_INCOMPATIBLE",
    "TECHNICAL_PREREQUISITE_MISSING",
    "EVIDENCE_REUSED",
    "NOT_REQUIRED",
    "AUTONOMY_FORBIDS",
    "SELECTED",
}

BUSINESS_LABELS = {
    "number_possession_verification": "Number possession",
    "sim_continuity": "SIM continuity",
    "device_continuity": "Device continuity",
    "device_identifier": "Device identifier",
    "number_recycling": "Number recycling",
    "kyc_match": "KYC Match",
    "age_verification": "Age assertion",
    "roaming_status": "Roaming",
    "location_verification": "Location",
    "device_reachability": "Reachability",
    "connectivity_insights": "Connectivity",
    "application_profiles": "Application profiles",
    "quality_on_demand": "QoD",
    "edge_discovery": "Edge discovery",
}

MATRIX_COLUMNS = [
    {"id": "relevance", "label": "Relevance", "group": "CANDIDATE_GENERATION"},
    {"id": "agentIntent", "label": "Agent / Intent", "group": "CONFIGURED_ELIGIBILITY"},
    {"id": "purpose", "label": "DPV Purpose", "group": "CONFIGURED_ELIGIBILITY"},
    {"id": "policy", "label": "Policy", "group": "CONFIGURED_ELIGIBILITY"},
    {"id": "agreement", "label": "Agreement", "group": "CONFIGURED_ELIGIBILITY"},
    {"id": "consent", "label": "Consent", "group": "CONFIGURED_ELIGIBILITY"},
    {"id": "subscription", "label": "Subscription", "group": "CONFIGURED_ELIGIBILITY"},
    {"id": "entitlement", "label": "Entitlement", "group": "CONFIGURED_ELIGIBILITY"},
    {"id": "region", "label": "Region", "group": "RUNTIME_FEASIBILITY"},
    {"id": "telcoFinder", "label": "Telco Finder", "group": "RUNTIME_FEASIBILITY"},
    {"id": "apiFinder", "label": "API Finder", "group": "RUNTIME_FEASIBILITY"},
    {"id": "provider", "label": "Provider", "group": "RUNTIME_FEASIBILITY"},
    {"id": "route", "label": "Route", "group": "RUNTIME_FEASIBILITY"},
    {"id": "evidence", "label": "Evidence", "group": "RUNTIME_FEASIBILITY"},
    {"id": "autonomy", "label": "Autonomy", "group": "RUNTIME_FEASIBILITY"},
    {"id": "usefulness", "label": "Usefulness", "group": "RUNTIME_FEASIBILITY"},
    {"id": "result", "label": "Final result", "group": "SELECT"},
]

HUMAN_BY_CODE = {
    "NOT_RELEVANT": "Does not help this Intent.",
    "PURPOSE_NOT_PERMITTED": "Purpose does not permit this capability.",
    "NOT_SUBSCRIBED": "Application is not subscribed to this capability.",
    "NOT_ENTITLED": "Subscribed, but this application is not entitled to use it.",
    "CONSENT_MISSING": "Consent is required and is not available.",
    "AGREEMENT_GAP": "Related, but policy or agreement does not permit it for this Intent.",
    "REGION_NOT_SUPPORTED": "Not supported in this region.",
    "PROVIDER_NOT_AVAILABLE": "No provider can offer this capability here.",
    "OPERATOR_NOT_SUPPORTED": "The operator does not support this capability.",
    "ENTITLEMENT_SERVER_UNAVAILABLE": "Operator entitlement server is unavailable.",
    "ACCESS_TYPE_INCOMPATIBLE": "Current access type cannot use this path.",
    "TECHNICAL_PREREQUISITE_MISSING": "A technical prerequisite is missing.",
    "EVIDENCE_REUSED": "Valid evidence already exists — invocation skipped.",
    "NOT_REQUIRED": "Relevant, but not needed for this outcome.",
    "AUTONOMY_FORBIDS": "Autonomy rules forbid this action.",
    "SELECTED": "Selected for this Intent.",
}

STORY_REASONS: dict[tuple[str, str, str], str] = {
    ("assess_network_trust", "location_verification", "CONSENT_MISSING"): "Location filtered: consent missing.",
    ("assess_network_trust", "number_recycling", "NOT_REQUIRED"): "Number recycling: relevant but not required.",
    ("assess_network_trust", "quality_on_demand", "NOT_RELEVANT"): "QoD does not help a payment-trust assessment.",
    ("verify_pharmacy_age_gate", "kyc_match", "AGREEMENT_GAP"): "KYC Match is related, but broader than required and not permitted.",
    ("verify_pharmacy_age_gate", "age_verification", "SELECTED"): "Age assertion is sufficient, permitted and entitled.",
    ("ensure_baggage_connection", "location_verification", "CONSENT_MISSING"): "Location is relevant and available, but consent is missing.",
    ("ensure_baggage_connection", "quality_on_demand", "NOT_REQUIRED"): "QoD is available, but network quality is not the limiting factor.",
    ("maintain_inspection_experience", "quality_on_demand", "NOT_REQUIRED"): "QoD is available and permitted, but the objective is already satisfied.",
    ("maintain_inspection_experience", "quality_on_demand", "SELECTED"): "After the breach, QoD became the useful network action.",
    ("maintain_inspection_experience", "edge_discovery", "NOT_REQUIRED"): "Edge discovery is not required for this camera SLO.",
    ("assess_recovery_continuity", "sim_continuity", "EVIDENCE_REUSED"): "SIM continuity evidence found, TTL valid, purpose compatible — reused.",
    ("assess_recovery_continuity", "device_continuity", "EVIDENCE_REUSED"): "Device continuity evidence reused — invocation skipped.",
    ("assess_recovery_continuity", "roaming_status", "EVIDENCE_REUSED"): "Roaming evidence reused — invocation skipped.",
}


def attach_discovery(
    payload: dict[str, Any],
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
) -> dict[str, Any]:
    """Add discovery[] / summary / matrix derived from the existing public trace."""
    from .runtime import _family_for, evaluate_capability_policy

    intent_id = str(payload.get("intentId") or "")
    actor = payload.get("actor") or {}
    enterprise = actor.get("enterprise") or {}
    application = actor.get("application") or {}
    agent = actor.get("agent") or {}
    enterprise_id = str(enterprise.get("id") or "")
    agent_id = str(agent.get("id") or "")
    purpose_cfg = store.purpose_by_id.get(str((payload.get("purpose") or {}).get("id") or "")) or {}
    policy = _policy_for(store, enterprise_id, intent_id, agent_id)
    policy_id = str((policy or {}).get("id") or "")

    purpose_public = _enrich_purpose(payload.get("purpose") or {}, purpose_cfg)
    telco = payload.get("telcoFinder") or {}
    api_finder = payload.get("apiFinder") or {}
    route = payload.get("route") or {}
    provider_label = str(route.get("to") or (telco.get("result") or {}).get("network") or api_finder.get("network") or "")
    route_display = str(route.get("display") or "")
    region = _region_from_known(payload.get("knownFromConfiguration") or {})

    candidates = _collect_candidates(payload, store, graph, registry, _family_for)
    events: list[dict[str, Any]] = []
    matrix_rows: list[dict[str, Any]] = []

    for cand in candidates:
        cap_id = cand["capabilityId"]
        fam = cand.get("family") or {}
        family_key = str(fam.get("familyGroup") or (store.capability_by_id.get(cap_id) or {}).get("family") or "")
        pol = evaluate_capability_policy(
            store,
            enterprise_id=enterprise_id,
            policy_id=policy_id,
            purpose=purpose_cfg or payload.get("purpose") or {},
            capability_id=cap_id,
            family=family_key,
        )
        finder_row = _finder_row(api_finder, cap_id, cand.get("operationId"))
        available = bool(finder_row.get("available") if finder_row else cand.get("available"))
        telco_ok = bool((telco.get("result") or {}).get("network") or telco.get("network"))
        moments = cand.get("moments") or [{"decision": cand["decision"], "moment": None}]
        for moment in moments:
            decision = moment["decision"]
            reason = _reason_code(decision, pol, intent_id)
            human = _human_reason(intent_id, cap_id, reason, decision)
            action = _action(reason, decision)
            checks = _checks(
                decision=decision,
                pol=pol,
                reason=reason,
                available=available,
                telco_ok=telco_ok,
                provider_label=provider_label,
                route_display=route_display,
                region=region,
                agent=agent,
                intent_id=intent_id,
                moment=moment.get("moment"),
            )
            events.extend(
                _events_for_candidate(
                    cand=cand,
                    fam=fam,
                    reason=reason,
                    human=human,
                    action=action,
                    checks=checks,
                    provider_label=provider_label,
                    route_display=route_display,
                    moment=moment.get("moment"),
                )
            )
            matrix_rows.append(
                {
                    "id": f"{cap_id}:{moment.get('moment') or 'final'}",
                    "capabilityId": cap_id,
                    "label": cand["businessLabel"],
                    "technicalLabel": cand["label"],
                    "operationId": cand.get("operationId"),
                    "apiFamily": (fam or {}).get("id") or (fam or {}).get("label"),
                    "moment": moment.get("moment"),
                    "reasonCode": reason,
                    "humanReason": human,
                    "action": action,
                    "checks": checks,
                    "subscription": pol.get("subscription"),
                    "entitlement": pol.get("entitlement"),
                    "consent": _consent_cell(pol),
                    "sourceConfigured": "ONBOARDING",
                    "sourceRuntime": "RUNTIME",
                }
            )

    summary = _summary(
        intent_id=intent_id,
        payload=payload,
        purpose_public=purpose_public,
        candidates=candidates,
        matrix_rows=matrix_rows,
        events=events,
        telco=telco,
        api_finder=api_finder,
        route=route,
    )
    views = dict(payload.get("views") or {})
    views["discovery"] = True
    views["basic"] = True
    views["advanced"] = True
    views["lens"] = "PRESENTATION_ONLY"
    return {
        **payload,
        "purpose": purpose_public,
        "discovery": events,
        "discoverySummary": summary,
        "discoveryMatrix": {
            "columnGroups": [
                {"id": "CANDIDATE_GENERATION", "label": "Candidate", "source": "CONFIGURATION"},
                {"id": "CONFIGURED_ELIGIBILITY", "label": "Configured / onboarding", "source": "ONBOARDING"},
                {"id": "RUNTIME_FEASIBILITY", "label": "Runtime discovered / evaluated", "source": "RUNTIME"},
                {"id": "SELECT", "label": "Select", "source": "RUNTIME"},
            ],
            "columns": MATRIX_COLUMNS,
            "rows": matrix_rows,
        },
        "views": views,
    }


def discovery_event_valid(event: dict[str, Any], codes: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    codes = codes or REASON_CODES
    if event.get("stage") not in STAGE_GROUPS:
        errors.append(f"bad stage {event.get('stage')}")
    if not event.get("candidate"):
        errors.append("missing candidate")
    if not event.get("candidateType"):
        errors.append("missing candidateType")
    if event.get("reasonCode") and event.get("reasonCode") not in codes:
        errors.append(f"reasonCode {event.get('reasonCode')} not in Cadence 7 enum")
    if not event.get("humanReason"):
        errors.append("missing humanReason")
    if event.get("source") not in {"ONBOARDING", "CONFIGURATION", "RUNTIME"}:
        errors.append(f"bad source {event.get('source')}")
    return errors


def _enrich_purpose(existing: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    dpv = cfg.get("dpv") or {}
    return {
        **existing,
        "id": existing.get("id") or cfg.get("id"),
        "label": existing.get("label") or cfg.get("audienceLabel") or cfg.get("label"),
        "audienceLabel": cfg.get("audienceLabel") or existing.get("label"),
        "source": existing.get("source") or "RESOLVED FROM CONFIGURATION",
        "dpv": {
            "id": dpv.get("id"),
            "label": dpv.get("label"),
            "iri": dpv.get("iri"),
            "context": dpv.get("context"),
            "version": dpv.get("version"),
        }
        if dpv
        else existing.get("dpv"),
    }


def _policy_for(store: ConfigStore, enterprise_id: str, intent_id: str, agent_id: str) -> dict[str, Any] | None:
    for policy in store.policies:
        if policy.get("intentId") != intent_id:
            continue
        if policy.get("enterpriseId") == enterprise_id or policy.get("agentId") == agent_id:
            return policy
    return next((p for p in store.policies if p.get("intentId") == intent_id), None)


def _region_from_known(known: dict[str, Any]) -> str:
    for row in known.get("rows") or []:
        if str(row.get("label") or "").lower() == "region":
            return str(row.get("value") or "Configured")
    return "Configured"


def _collect_candidates(
    payload: dict[str, Any],
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    family_for,
) -> list[dict[str, Any]]:
    decisions = [d for d in (payload.get("decisions") or []) if d.get("capabilityId")]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for decision in decisions:
        grouped.setdefault(str(decision["capabilityId"]), []).append(decision)

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    # Preserve decision order (first occurrence).
    for decision in decisions:
        cap_id = str(decision["capabilityId"])
        if cap_id in seen:
            continue
        seen.add(cap_id)
        cap = store.capability_by_id.get(cap_id) or {"id": cap_id, "label": decision.get("label")}
        fam = family_for(registry, cap_id)
        cap_decisions = grouped[cap_id]
        moments = _moments(payload.get("intentId"), cap_id, cap_decisions)
        rows.append(
            {
                "capabilityId": cap_id,
                "label": cap.get("label") or decision.get("label"),
                "businessLabel": BUSINESS_LABELS.get(cap_id) or cap.get("label") or decision.get("label"),
                "family": fam,
                "operationId": decision.get("operationId") or cap_decisions[-1].get("operationId"),
                "available": str(decision.get("availability") or "").upper() == "YES",
                "decision": cap_decisions[-1],
                "moments": moments,
            }
        )
    return rows


def _moments(intent_id: str, cap_id: str, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if intent_id == "maintain_inspection_experience" and cap_id == "quality_on_demand" and len(decisions) >= 2:
        initial = next((d for d in decisions if d.get("state") == "NOT_REQUIRED"), decisions[0])
        later = next((d for d in reversed(decisions) if d.get("state") in {"INVOKED", "SELECTED"}), decisions[-1])
        return [
            {"decision": initial, "moment": "INITIAL"},
            {"decision": later, "moment": "AFTER_BREACH"},
        ]
    return [{"decision": decisions[-1], "moment": None}]


def _reason_code(decision: dict[str, Any], pol: dict[str, Any], intent_id: str = "") -> str:
    state = str(decision.get("state") or "")
    policy_result = str(decision.get("policyResult") or pol.get("result") or "")
    why = str(decision.get("why") or "").lower()
    if state == "EVIDENCE_REUSED":
        return "EVIDENCE_REUSED"
    if state == "NOT_REQUIRED":
        if "not mapped" in why or (intent_id == "assess_network_trust" and not decision.get("relevant", True)):
            return "NOT_RELEVANT"
        return "NOT_REQUIRED"
    if state in {"INVOKED", "SELECTED"}:
        return "SELECTED"
    if policy_result == "NOT_SUBSCRIBED" or state == "NOT_SUBSCRIBED":
        return "NOT_SUBSCRIBED"
    if policy_result == "NOT_ENTITLED" or state == "NOT_ENTITLED":
        return "NOT_ENTITLED"
    if policy_result == "PURPOSE_DENIED":
        return "PURPOSE_NOT_PERMITTED"
    if pol.get("consentRequired") and not pol.get("consentAvailable"):
        return "CONSENT_MISSING"
    if state == "BLOCKED_BY_POLICY" or policy_result == "BLOCKED_BY_POLICY":
        detail = f"{decision.get('why') or ''} {pol.get('detail') or ''}".lower()
        if "consent" in detail:
            return "CONSENT_MISSING"
        return "AGREEMENT_GAP"
    return "SELECTED"


def _human_reason(intent_id: str, cap_id: str, reason: str, decision: dict[str, Any]) -> str:
    story = STORY_REASONS.get((intent_id, cap_id, reason))
    if story:
        return story
    if reason == "SELECTED" and decision.get("state") == "INVOKED":
        return HUMAN_BY_CODE["SELECTED"]
    return HUMAN_BY_CODE.get(reason) or str(decision.get("why") or reason)


def _action(reason: str, decision: dict[str, Any]) -> str:
    if reason == "EVIDENCE_REUSED":
        return "REUSE"
    if reason == "SELECTED":
        return "CALL"
    if reason == "NOT_REQUIRED":
        return "SKIP"
    return "FILTER"


def _consent_cell(pol: dict[str, Any]) -> str:
    if not pol.get("consentRequired"):
        return "NOT_REQUIRED"
    if pol.get("consentAvailable"):
        return "YES"
    return "MISSING"


def _finder_row(api_finder: dict[str, Any], cap_id: str, operation_id: str | None) -> dict[str, Any]:
    for row in api_finder.get("results") or []:
        if row.get("capabilityId") == cap_id or (operation_id and row.get("operationId") == operation_id):
            return row
    return {}


def _checks(
    *,
    decision: dict[str, Any],
    pol: dict[str, Any],
    reason: str,
    available: bool,
    telco_ok: bool,
    provider_label: str,
    route_display: str,
    region: str,
    agent: dict[str, Any],
    intent_id: str,
    moment: str | None,
) -> dict[str, Any]:
    relevant = bool(decision.get("relevant", True)) or reason != "NOT_RELEVANT"
    purpose_ok = str(pol.get("purpose") or "") == "permitted"
    consent = _consent_cell(pol)
    policy_pass = reason not in {"PURPOSE_NOT_PERMITTED", "CONSENT_MISSING", "AGREEMENT_GAP", "NOT_SUBSCRIBED", "NOT_ENTITLED"}
    agreement = "DENIED" if reason == "AGREEMENT_GAP" else "PERMITTED"
    usefulness = "NOT_REQUIRED" if reason == "NOT_REQUIRED" else ("YES" if reason in {"SELECTED", "EVIDENCE_REUSED"} else "—")
    if moment == "INITIAL" and reason == "NOT_REQUIRED":
        usefulness = "NOT_REQUIRED · objective satisfied"
    if moment == "AFTER_BREACH" and reason == "SELECTED":
        usefulness = "YES · after objective breach"
    evidence = "REUSED" if reason == "EVIDENCE_REUSED" else ("INVOKED" if reason == "SELECTED" else "NOT_CALLED")
    return {
        "relevance": "YES" if relevant and reason != "NOT_RELEVANT" else "NO",
        "agentIntent": "AUTHORIZED" if agent else "—",
        "purpose": "PERMITTED" if purpose_ok else "NOT_PERMITTED",
        "policy": "PERMITTED" if policy_pass or reason in {"NOT_REQUIRED", "NOT_RELEVANT", "SELECTED", "EVIDENCE_REUSED"} else reason,
        "agreement": agreement,
        "consent": consent,
        "subscription": pol.get("subscription") or "—",
        "entitlement": pol.get("entitlement") or "—",
        "region": region or "Configured",
        "telcoFinder": (provider_label or "Resolved") if telco_ok else "NOT_RESOLVED",
        "apiFinder": "AVAILABLE" if available else "NOT_AVAILABLE",
        "provider": provider_label or "—",
        "route": route_display or "—",
        "evidence": evidence,
        "autonomy": "ALLOWED",
        "usefulness": usefulness,
        "result": reason,
        "moment": moment,
        "intentId": intent_id,
    }


def _event(
    *,
    stage: str,
    cand: dict[str, Any],
    fam: dict[str, Any],
    result: str,
    reason: str | None,
    human: str,
    source: str,
    provider: str,
    route: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "stage": stage,
        "candidate": cand["capabilityId"],
        "candidateType": "CAPABILITY",
        "capability": cand["capabilityId"],
        "capabilityLabel": cand["label"],
        "businessLabel": cand["businessLabel"],
        "apiFamily": (fam or {}).get("id"),
        "operationId": cand.get("operationId"),
        "result": result,
        "reasonCode": reason,
        "humanReason": human,
        "source": source,
        "provider": provider or None,
        "route": route or None,
        "metadata": metadata,
    }


def _events_for_candidate(
    *,
    cand: dict[str, Any],
    fam: dict[str, Any],
    reason: str,
    human: str,
    action: str,
    checks: dict[str, Any],
    provider_label: str,
    route_display: str,
    moment: str | None,
) -> list[dict[str, Any]]:
    meta_base = {
        **checks,
        "action": action,
        "subscription": checks.get("subscription"),
        "entitlement": checks.get("entitlement"),
        "moment": moment,
    }
    events = [
        _event(
            stage="CANDIDATE_GENERATION",
            cand=cand,
            fam=fam,
            result="FILTERED" if reason == "NOT_RELEVANT" else "PASSED",
            reason="NOT_RELEVANT" if reason == "NOT_RELEVANT" else None,
            human=human if reason == "NOT_RELEVANT" else f"{cand['businessLabel']} could help this Intent.",
            source="CONFIGURATION",
            provider=provider_label,
            route=route_display,
            metadata=meta_base,
        )
    ]
    if reason == "NOT_RELEVANT":
        events.append(
            _event(
                stage="SELECT",
                cand=cand,
                fam=fam,
                result="FILTERED",
                reason=reason,
                human=human,
                source="RUNTIME",
                provider=provider_label,
                route=route_display,
                metadata=meta_base,
            )
        )
        return events

    config_filter = reason in {
        "PURPOSE_NOT_PERMITTED",
        "NOT_SUBSCRIBED",
        "NOT_ENTITLED",
        "CONSENT_MISSING",
        "AGREEMENT_GAP",
        "AUTONOMY_FORBIDS",
    }
    events.append(
        _event(
            stage="CONFIGURED_ELIGIBILITY",
            cand=cand,
            fam=fam,
            result="FILTERED" if config_filter else "PASSED",
            reason=reason if config_filter else None,
            human=human if config_filter else "Allowed by purpose, policy, subscription and entitlement.",
            source="ONBOARDING" if reason in {"NOT_SUBSCRIBED", "NOT_ENTITLED"} else "CONFIGURATION",
            provider=provider_label,
            route=route_display,
            metadata=meta_base,
        )
    )
    if config_filter:
        events.append(
            _event(
                stage="SELECT",
                cand=cand,
                fam=fam,
                result="FILTERED",
                reason=reason,
                human=human,
                source="CONFIGURATION",
                provider=provider_label,
                route=route_display,
                metadata=meta_base,
            )
        )
        return events

    runtime_filter = reason in {
        "REGION_NOT_SUPPORTED",
        "PROVIDER_NOT_AVAILABLE",
        "OPERATOR_NOT_SUPPORTED",
        "ENTITLEMENT_SERVER_UNAVAILABLE",
        "ACCESS_TYPE_INCOMPATIBLE",
        "TECHNICAL_PREREQUISITE_MISSING",
        "NOT_REQUIRED",
        "EVIDENCE_REUSED",
    }
    runtime_result = "PASSED"
    runtime_reason = None
    runtime_human = "Available on this operator / provider right now."
    if reason == "NOT_REQUIRED":
        runtime_result = "FILTERED"
        runtime_reason = reason
        runtime_human = human
    elif reason == "EVIDENCE_REUSED":
        runtime_result = "REUSED"
        runtime_reason = reason
        runtime_human = human
    elif runtime_filter:
        runtime_result = "FILTERED"
        runtime_reason = reason
        runtime_human = human
    events.append(
        _event(
            stage="RUNTIME_FEASIBILITY",
            cand=cand,
            fam=fam,
            result=runtime_result,
            reason=runtime_reason,
            human=runtime_human,
            source="RUNTIME",
            provider=provider_label,
            route=route_display,
            metadata=meta_base,
        )
    )
    select_result = {"EVIDENCE_REUSED": "REUSED", "SELECTED": "SELECTED", "NOT_REQUIRED": "SKIPPED"}.get(reason, "FILTERED")
    events.append(
        _event(
            stage="SELECT",
            cand=cand,
            fam=fam,
            result=select_result,
            reason=reason,
            human=human,
            source="RUNTIME",
            provider=provider_label,
            route=route_display,
            metadata=meta_base,
        )
    )
    return events


def _summary(
    *,
    intent_id: str,
    payload: dict[str, Any],
    purpose_public: dict[str, Any],
    candidates: list[dict[str, Any]],
    matrix_rows: list[dict[str, Any]],
    events: list[dict[str, Any]],
    telco: dict[str, Any],
    api_finder: dict[str, Any],
    route: dict[str, Any],
) -> dict[str, Any]:
    # Use the latest moment per capability for pipeline counts.
    latest: dict[str, dict[str, Any]] = {}
    for row in matrix_rows:
        cap = row["capabilityId"]
        if cap not in latest or row.get("moment") == "AFTER_BREACH":
            latest[cap] = row
        if row.get("moment") is None:
            latest[cap] = row

    finals = list(latest.values())
    could_help = [r for r in finals if r["checks"].get("relevance") == "YES"]
    allowed = [
        r
        for r in could_help
        if r["reasonCode"]
        not in {"PURPOSE_NOT_PERMITTED", "NOT_SUBSCRIBED", "NOT_ENTITLED", "CONSENT_MISSING", "AGREEMENT_GAP", "AUTONOMY_FORBIDS"}
    ]
    available = [r for r in allowed if r["checks"].get("apiFinder") == "AVAILABLE"]
    useful = [r for r in available if r["reasonCode"] not in {"NOT_REQUIRED"}]
    selected = [r for r in useful if r["reasonCode"] in {"SELECTED", "EVIDENCE_REUSED"}]
    filtered = [r for r in finals if r["reasonCode"] not in {"SELECTED", "EVIDENCE_REUSED"}]

    layers = [
        {
            "id": "application",
            "title": "Your application",
            "count": None,
            "detail": "What it already knows, and the Intent it sent.",
        },
        {
            "id": "couldAdd",
            "title": "What the network could add",
            "count": len(could_help),
            "detail": "Business capabilities that might help this outcome.",
            "items": [r["label"] for r in could_help],
        },
        {
            "id": "configuration",
            "title": "What your configuration allows",
            "count": len(allowed),
            "detail": "Purpose, policy, subscription, entitlement, consent.",
        },
        {
            "id": "possibleNow",
            "title": "What is possible right now",
            "count": len(available),
            "detail": "Region, operator, API availability, provider / route.",
        },
        {
            "id": "selected",
            "title": "What NetAware selected",
            "count": len(selected),
            "detail": "Invoked, reused, skipped, or not required.",
            "items": [r["label"] for r in selected],
        },
    ]

    pipeline = [
        {"label": "potentially relevant capabilities", "count": len(could_help)},
        {"label": "allowed by enterprise configuration", "count": len(allowed)},
        {"label": "available on this provider / network", "count": len(available)},
        {"label": "actually useful", "count": len(useful)},
        {"label": "selected", "count": len(selected)},
    ]

    actor = payload.get("actor") or {}
    request = payload.get("request") or {}
    outcome = payload.get("outcome") or {}
    return {
        "intentId": intent_id,
        "application": (actor.get("application") or {}).get("label"),
        "enterprise": (actor.get("enterprise") or {}).get("label"),
        "agent": (actor.get("agent") or {}).get("label"),
        "intent": intent_id,
        "purposeLabel": purpose_public.get("audienceLabel") or purpose_public.get("label"),
        "purposeDpv": (purpose_public.get("dpv") or {}).get("id"),
        "purposeContext": (purpose_public.get("dpv") or {}).get("context"),
        "knownFromConfiguration": payload.get("knownFromConfiguration"),
        "request": request,
        "layers": layers,
        "pipeline": pipeline,
        "filtered": [
            {
                "label": r["label"],
                "reasonCode": r["reasonCode"],
                "humanReason": r["humanReason"],
                "action": r["action"],
            }
            for r in filtered
        ],
        "selected": [
            {
                "label": r["label"],
                "reasonCode": r["reasonCode"],
                "humanReason": r["humanReason"],
                "action": r["action"],
                "operationId": r.get("operationId"),
                "provider": r["checks"].get("provider"),
                "route": r["checks"].get("route"),
            }
            for r in selected
        ],
        "outcome": {
            "outcome": outcome.get("outcome"),
            "summary": outcome.get("summary"),
            "decisionOwner": outcome.get("decisionOwner"),
            "recommendedAction": outcome.get("recommendedAction"),
        },
        "finders": {
            "telcoFinder": {
                "role": "Which operator / network applies to this subject?",
                "result": (telco.get("result") or {}).get("network") or telco.get("network"),
                "neededBecause": telco.get("neededBecause"),
                "source": "RUNTIME",
            },
            "apiFinder": {
                "role": "Which candidate API operations are available through which provider?",
                "network": api_finder.get("network"),
                "results": api_finder.get("results") or [],
                "source": "RUNTIME",
            },
            "providerRoute": {
                "role": "Where will the selected operation actually be invoked?",
                "display": route.get("display"),
                "type": route.get("type"),
                "source": "RUNTIME",
            },
        },
        "eventCount": len(events),
        "candidateCount": len(finals),
        "dynamicUsefulness": _dynamic_usefulness(intent_id, matrix_rows),
    }


def _dynamic_usefulness(intent_id: str, matrix_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if intent_id != "maintain_inspection_experience":
        return None
    qod = [r for r in matrix_rows if r.get("capabilityId") == "quality_on_demand"]
    if len(qod) < 2:
        return None
    return {
        "capability": "QoD",
        "initial": next((r["reasonCode"] for r in qod if r.get("moment") == "INITIAL"), "NOT_REQUIRED"),
        "afterBreach": next((r["reasonCode"] for r in qod if r.get("moment") == "AFTER_BREACH"), "SELECTED"),
        "note": "The same capability is reconsidered when runtime usefulness changes.",
    }
