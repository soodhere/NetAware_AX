"""Cadence 4 deterministic runtime. Scenario configuration drives execution."""
from __future__ import annotations

from typing import Any, Callable

import yaml
from fastapi import HTTPException

from .config import ROOT
from .graph import KnowledgeGraph
from .model import ConfigStore
from .nv_runtime import run_verify_mobile_number
from .ota_runtime import run_prepare_ota_cohort
from .registry import CatalogRegistry
from .evidence_store import find_reusable, persist_from_trace, reset_store
from .presentation import enrich_trace_presentation
from .runtime_models import (
    Beat,
    Decision,
    Evidence,
    ExecutionTrace,
    Invocation,
    Outcome,
    Plan,
    PlanStep,
    PolicyEvaluation,
)

EXECUTABLE_INTENTS = {
    "assess_network_trust",
    "assess_recovery_continuity",
    "ensure_baggage_connection",
    "maintain_inspection_experience",
    "verify_pharmacy_age_gate",
    "verify_mobile_number",
    "prepare_ota_cohort",
}


def _guided_intents() -> set[str]:
    from .guided_runtime import GUIDED_INTENTS

    return set(GUIDED_INTENTS)


EXECUTABLE_INTENTS = EXECUTABLE_INTENTS | _guided_intents()
SCENARIO_PATHS: dict[str, Any] = {
    "assess_network_trust": ROOT / "data" / "runtime" / "rocket-bank-trust.yaml",
    "assess_recovery_continuity": ROOT / "data" / "runtime" / "rocket-bank-recovery.yaml",
    "ensure_baggage_connection": ROOT / "data" / "runtime" / "high-flight-baggage.yaml",
    "maintain_inspection_experience": ROOT / "data" / "runtime" / "acme-inspection.yaml",
    "verify_pharmacy_age_gate": ROOT / "data" / "runtime" / "citycare-pharmacy.yaml",
    "verify_mobile_number": ROOT / "data" / "runtime" / "rocket-bank-nv.yaml",
    "prepare_ota_cohort": ROOT / "data" / "runtime" / "acme-ota-fleet.yaml",
}


def load_scenario(intent_id: str) -> dict[str, Any]:
    path = SCENARIO_PATHS.get(intent_id)
    if not path:
        raise HTTPException(status_code=409, detail=f"No scenario seed for intent: {intent_id}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _op_meta(registry: CatalogRegistry, operation_id: str, source: str | None = None) -> dict[str, Any]:
    op = registry.canonical(operation_id, source) or registry.canonical(operation_id)
    if not op:
        raise HTTPException(status_code=500, detail=f"operationId not in AX_ACTIVE_CATALOG: {operation_id}")
    return op.to_public()


def _cap_ops(graph: KnowledgeGraph, capability_id: str) -> list[dict[str, Any]]:
    return list(graph.cap_ops.get(capability_id) or [])


def _primary_op(graph: KnowledgeGraph, capability_id: str) -> dict[str, Any] | None:
    preferred = {
        "number_possession_verification": "phoneNumberVerify",
        "sim_continuity": "checkSimSwap",
        "device_continuity": "checkDeviceSwap",
        "device_identifier": "retrieveIdentifier",
        "number_recycling": "checkNumberRecycling",
        "roaming_status": "getRoamingStatus",
        "location_verification": "verifyLocation",
        "device_reachability": "getReachabilityStatus",
        "connectivity_insights": "checkNetworkQuality",
        "quality_on_demand": "createSession",
        "application_profiles": "createApplicationProfile",
        "edge_discovery": "readClosestEdgeCloudZone",
        "age_verification": "verifyAge",
        "kyc_match": "KYC_Match",
    }
    want = preferred.get(capability_id)
    rows = _cap_ops(graph, capability_id)
    if want:
        for row in rows:
            if row.get("operationId") == want:
                return row
    return rows[0] if rows else None


def _family_for(registry: CatalogRegistry, capability_id: str) -> dict[str, Any] | None:
    for fam in registry.families:
        if capability_id in (fam.get("capabilities") or []):
            return fam
    return None


def _subscribed(store: ConfigStore, enterprise_id: str, capability_id: str, family: str | None) -> bool:
    return store.is_subscribed(enterprise_id, capability_id, family)


def _consent(store: ConfigStore, policy_id: str, capability_id: str) -> dict[str, Any] | None:
    for rule in store.consent_rules:
        if rule.get("policyId") == policy_id and rule.get("capabilityId") == capability_id:
            return rule
    return None


def _purpose_allows(purpose: dict[str, Any], family: str | None) -> bool:
    permitted = purpose.get("permittedCapabilityFamilies") or []
    if not permitted:
        return True
    return family in permitted


def evaluate_capability_policy(
    store: ConfigStore,
    *,
    enterprise_id: str,
    policy_id: str,
    purpose: dict[str, Any],
    capability_id: str,
    family: str | None,
) -> dict[str, Any]:
    sub = _subscribed(store, enterprise_id, capability_id, family)
    policy_row = next((p for p in store.policies if p.get("id") == policy_id), None)
    entitled = store.is_entitled(
        enterprise_id=enterprise_id,
        application_id=str((policy_row or {}).get("applicationId") or ""),
        agent_id=str((policy_row or {}).get("agentId") or ""),
        capability_id=capability_id,
        family=family,
    )
    purpose_ok = _purpose_allows(purpose, family)
    consent = _consent(store, policy_id, capability_id)
    agreement = next((a for a in store.agreements if a.get("enterpriseId") == enterprise_id), None)
    deny_rule = next(
        (
            r
            for r in store.policy_rules
            if r.get("policyId") == policy_id
            and r.get("dimension") == "capability"
            and r.get("operator") == "deny"
            and r.get("value") == capability_id
        ),
        None,
    )
    result = "PERMITTED"
    detail = "Configured policy permits this capability/API for the resolved purpose."
    if deny_rule:
        result = "BLOCKED_BY_POLICY"
        detail = str(
            deny_rule.get("note")
            or f"Configured policy denies capability {capability_id} for this intent/purpose."
        )
    elif not sub:
        result = "NOT_SUBSCRIBED"
        detail = "No active subscription for this capability."
    elif not entitled:
        result = "NOT_ENTITLED"
        detail = "Subscribed, but this application/agent is not entitled to invoke this capability."
    elif not purpose_ok:
        result = "PURPOSE_DENIED"
        detail = "Purpose configuration does not permit this capability family."
    elif consent and consent.get("required") and not consent.get("available"):
        result = "BLOCKED_BY_POLICY"
        detail = (
            "Configured demo policy: consent required for this capability and is not available. "
            "Not a universal legal conclusion."
        )
    return {
        "subscription": "YES" if sub else "NO",
        "entitlement": "YES" if entitled else "NO",
        "purpose": "permitted" if purpose_ok else "not permitted",
        "consentRequired": bool(consent and consent.get("required")),
        "consentAvailable": bool(consent and consent.get("available")) if consent else None,
        "agreement": (agreement or {}).get("label") or "Configured",
        "residency": (agreement or {}).get("dataResidency") or "Configured",
        "result": result,
        "detail": detail,
        "source": "CONFIGURED POLICY",
    }


def _provider_label(store: ConfigStore, provider_id: str, audience: str | None = None) -> str:
    if audience:
        return audience
    p = store.provider_by_id.get(provider_id) or {}
    return str(p.get("audienceLabel") or p.get("label") or provider_id)


def _provider_ops(store: ConfigStore, provider_id: str) -> set[str]:
    for block in store.provider_capabilities:
        if block.get("providerId") == provider_id:
            return {str(item["operationId"]) for item in block.get("operations") or []}
    return set()


def run_assess_network_trust(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    request: dict[str, Any],
) -> ExecutionTrace:
    intent_id = str(request.get("intent") or "")
    seed = load_scenario(intent_id).get("scenario") or {}
    if intent_id not in EXECUTABLE_INTENTS:
        raise HTTPException(status_code=409, detail=f"Intent not executable: {intent_id}")

    agent_id = str(request.get("agentId") or seed.get("agentId"))
    agent = store.agent_by_id.get(agent_id)
    if not agent:
        raise HTTPException(status_code=403, detail="Unknown agent")
    if intent_id not in (agent.get("allowedIntents") or []):
        raise HTTPException(status_code=403, detail="Agent is not authorized for this intent")

    application = store.application_by_id.get(str(agent.get("actsOnBehalfOf") or ""))
    enterprise = store.enterprise_by_id.get(str(agent.get("enterpriseId") or ""))
    if not application or not enterprise:
        raise HTTPException(status_code=403, detail="Agent application/enterprise not resolved")

    intent = store.intent_by_id.get(intent_id) or {}
    uc_id = graph.intent_use_case.get(intent_id)
    use_case = store.use_case_by_id.get(uc_id or "")
    domain = store.domain_by_id.get(str((use_case or {}).get("domainId") or enterprise.get("domainId") or ""))
    policy = next((p for p in store.policies if p.get("id") == seed.get("policyId")), None)
    if not policy:
        raise HTTPException(status_code=500, detail="Scenario policy missing")
    purpose = store.purpose_by_id.get(str(policy.get("purposeId") or intent.get("defaultPurposeId") or ""))
    if not purpose:
        raise HTTPException(status_code=500, detail="Purpose not resolved from configuration")

    corr = seed.get("correlation") or {}
    req_body = {
        "intent": intent_id,
        "subject": (request.get("subject") or seed.get("request", {}).get("subject")),
        "context": (request.get("context") or seed.get("request", {}).get("context")),
    }
    provider_id = str(seed.get("selectedProviderId"))
    provider_label = str(seed.get("providerAudienceLabel") or "Network Provider A")
    route_type = str(seed.get("selectedRouteType") or "DIRECT")
    advertised = _provider_ops(store, provider_id)
    responses = seed.get("simulatedResponses") or {}

    mapped = list(graph.intent_caps.get(intent_id) or [])
    candidates: list[dict[str, Any]] = []
    for link in mapped:
        cap_id = str(link["capabilityId"])
        cap = store.capability_by_id.get(cap_id) or {"id": cap_id}
        fam = _family_for(registry, cap_id)
        op_row = _primary_op(graph, cap_id)
        meta = _op_meta(registry, str(op_row["operationId"]), str(op_row["source"])) if op_row else {}
        pol = evaluate_capability_policy(
            store,
            enterprise_id=str(enterprise["id"]),
            policy_id=str(policy["id"]),
            purpose=purpose,
            capability_id=cap_id,
            family=str((fam or {}).get("familyGroup") or cap.get("family")),
        )
        available = bool(op_row and op_row["operationId"] in advertised)
        candidates.append(
            {
                "capability": cap,
                "role": link.get("role"),
                "family": fam,
                "operation": op_row,
                "catalog": meta,
                "policy": pol,
                "available": available,
            }
        )

    invoke_order = [
        "number_possession_verification",
        "sim_continuity",
        "device_continuity",
        "device_identifier",
        "roaming_status",
    ]
    skip_after_evidence = {"number_recycling"}
    blocked = {c["capability"]["id"] for c in candidates if c["policy"]["result"] == "BLOCKED_BY_POLICY"}

    plan_steps = [
        PlanStep(1, "Verify number possession", "number_possession_verification", "phoneNumberVerify"),
        PlanStep(2, "Check SIM continuity", "sim_continuity", "checkSimSwap"),
        PlanStep(3, "Check device continuity", "device_continuity", "checkDeviceSwap"),
        PlanStep(4, "Resolve device identity if useful", "device_identifier", "retrieveIdentifier"),
        PlanStep(5, "Check roaming context", "roaming_status", "getRoamingStatus"),
        PlanStep(6, "Consider location verification", "location_verification", "verifyLocation"),
        PlanStep(7, "Evaluate evidence", None, None),
        PlanStep(8, "Return network trust assessment", None, None),
    ]
    plan = Plan(id="plan-rb-trust", intentId=intent_id, executionId=str(corr.get("executionId")), steps=plan_steps)

    invocations: list[Invocation] = []
    evidence: list[Evidence] = []
    decisions: list[Decision] = []
    policies: list[PolicyEvaluation] = [
        PolicyEvaluation(
            "pol-actor-auth",
            "ACTOR_INTENT",
            "agent",
            "AUTHORIZED",
            "CONFIGURED POLICY",
            f"{agent.get('label')} is an authorized agent for {application.get('label')}. Identity model is simulated_placeholder.",
        ),
        PolicyEvaluation(
            "pol-actor-intent",
            "ACTOR_INTENT",
            "intent",
            "ALLOWED",
            "CONFIGURED POLICY",
            f"Intent {intent_id} is in the agent's allowedIntents.",
        ),
        PolicyEvaluation(
            "pol-actor-purpose",
            "ACTOR_INTENT",
            "purpose",
            "RESOLVED_FROM_CONFIGURATION",
            "CONFIGURED POLICY",
            f"Purpose {(purpose.get('audienceLabel') or purpose.get('label'))} resolved from application/intent policy. Not inferred from transaction data.",
        ),
    ]

    for cap_id in invoke_order:
        cand = next((c for c in candidates if c["capability"]["id"] == cap_id), None)
        if not cand:
            continue
        pol = cand["policy"]
        op_row = cand["operation"]
        meta = cand["catalog"]
        label = cand["capability"].get("label")
        fam = cand["family"] or {}
        policies.append(
            PolicyEvaluation(
                f"pol-cap-{cap_id}",
                "CAPABILITY_API",
                cap_id,
                pol["result"],
                "CONFIGURED POLICY",
                pol["detail"],
            )
        )
        if pol["result"] == "BLOCKED_BY_POLICY":
            decisions.append(
                Decision(
                    id=f"dec-{cap_id}",
                    capabilityId=cap_id,
                    familyId=fam.get("id"),
                    operationId=(op_row or {}).get("operationId"),
                    label=label,
                    relevant=True,
                    availability="YES" if cand["available"] else "NO",
                    policyResult=pol["result"],
                    state="BLOCKED_BY_POLICY",
                    why=pol["detail"],
                    stage="CAPABILITY_API",
                )
            )
            continue
        op_id = str(op_row["operationId"])
        sim = responses.get(op_id) or {}
        inv = Invocation(
            id=f"inv-{op_id}",
            operationId=op_id,
            source=str(op_row["source"]),
            familyId=str(fam.get("id") or meta.get("api_id")),
            familyLabel=str(fam.get("label") or meta.get("family")),
            specMaturity=str(meta.get("spec_maturity")),
            businessStatus=str(meta.get("business_status")),
            method=str(meta.get("method")),
            providerId=provider_id,
            providerLabel=provider_label,
            routeType=route_type,
            correlationId=str(corr.get("correlationId")),
            latencyMs=int(sim.get("latencyMs") or 40),
            httpStatus=int(sim.get("httpStatus") or 200),
            raw=sim.get("raw") or {},
        )
        invocations.append(inv)
        ev = sim.get("evidence") or {}
        evidence.append(
            Evidence(
                id=f"ev-{op_id}",
                operationId=op_id,
                type=str(ev.get("type") or op_id),
                status=str(ev.get("status") or "observed"),
                payload={k: v for k, v in ev.items() if k not in {"type"}},
                purposeId=str(purpose["id"]),
            )
        )
        decisions.append(
            Decision(
                id=f"dec-{cap_id}",
                capabilityId=cap_id,
                familyId=fam.get("id"),
                operationId=op_id,
                label=label,
                relevant=True,
                availability="YES",
                policyResult="PERMITTED",
                state="INVOKED",
                why=f"Relevant to {cand['role']} network-trust evidence. Available from {provider_label}. Permitted. Invoked.",
                stage="EXECUTION",
            )
        )

    # Location: mapped, available, blocked, replan.
    loc = next((c for c in candidates if c["capability"]["id"] == "location_verification"), None)
    if loc:
        pol = loc["policy"]
        policies.append(
            PolicyEvaluation(
                "pol-cap-location_verification",
                "CAPABILITY_API",
                "location_verification",
                pol["result"],
                "CONFIGURED POLICY",
                pol["detail"],
            )
        )
        decisions.append(
            Decision(
                id="dec-location_verification",
                capabilityId="location_verification",
                familyId=(loc["family"] or {}).get("id"),
                operationId=(loc["operation"] or {}).get("operationId"),
                label=loc["capability"].get("label"),
                relevant=True,
                availability="YES" if loc["available"] else "NO",
                policyResult=pol["result"],
                state="BLOCKED_BY_POLICY",
                why=pol["detail"] + " NetAware continues with other evidence (replan).",
                stage="CAPABILITY_API",
            )
        )
        plan.steps[5].state = "BLOCKED_BY_POLICY"

    rec = next((c for c in candidates if c["capability"]["id"] == "number_recycling"), None)
    if rec:
        pol = rec["policy"]
        policies.append(
            PolicyEvaluation(
                "pol-cap-number_recycling",
                "CAPABILITY_API",
                "number_recycling",
                "PERMITTED",
                "CONFIGURED POLICY",
                "Permitted, but not required after sufficient continuity evidence.",
            )
        )
        decisions.append(
            Decision(
                id="dec-number_recycling",
                capabilityId="number_recycling",
                familyId=(rec["family"] or {}).get("id"),
                operationId=(rec["operation"] or {}).get("operationId"),
                label=rec["capability"].get("label"),
                relevant=True,
                availability="YES" if rec["available"] else "NO",
                policyResult="PERMITTED",
                state="NOT_REQUIRED",
                why="Mapped as considered. Number possession plus SIM/device evidence is already sufficient. API economy: not invoked.",
                stage="PLAN",
            )
        )

    decisions.append(
        Decision(
            id="dec-quality_on_demand",
            capabilityId="quality_on_demand",
            familyId="quality-on-demand",
            operationId="createSession",
            label="Quality on Demand",
            relevant=False,
            availability="YES",
            policyResult="NOT_APPLICABLE",
            state="NOT_REQUIRED",
            why="Not relevant to transaction-trust assessment. Not mapped to this intent.",
            stage="PLAN",
        )
    )

    for step in plan.steps:
        if step.operationId in {i.operationId for i in invocations}:
            step.state = "INVOKED"
        elif step.capabilityId in skip_after_evidence:
            step.state = "NOT_REQUIRED"
        elif step.capabilityId in blocked or step.state == "BLOCKED_BY_POLICY":
            step.state = "BLOCKED_BY_POLICY"
        elif step.operationId is None:
            step.state = "COMPLETED"

    out_seed = seed.get("outcome") or {}
    outcome = Outcome(
        outcome=str(out_seed.get("outcome") or "STEP_UP"),
        networkTrust=str(out_seed.get("networkTrust") or "DISRUPTED"),
        confidence=float(out_seed.get("confidence") or 0.94),
        recommendedAction=str(out_seed.get("recommendedAction") or "ADDITIONAL_VERIFICATION"),
        decisionOwner=str(out_seed.get("decisionOwner") or "ENTERPRISE"),
        reasonCodes=list(out_seed.get("reasonCodes") or ["RECENT_SIM_CHANGE", "DEVICE_IDENTITY_CHANGE"]),
        summary=str(out_seed.get("summary") or "Network trust disrupted. Rocket Bank owns the financial decision."),
    )

    autonomy = {
        "gather_network_evidence": "ACT",
        "produce_assessment": "ACT",
        "recommend_step_up": "RECOMMEND",
        "decline_transaction": "NOT_AUTHORIZED",
        "selectedAction": "recommend_step_up",
        "selectedLevel": "RECOMMEND",
        "note": "Agent may recommend STEP_UP. It may not decline the payment. Rocket Bank owns the financial decision.",
        "source": "CONFIGURED POLICY",
    }
    policies.append(
        PolicyEvaluation(
            "pol-auto-gather",
            "AUTONOMY_ACTION",
            "gather_network_evidence",
            "ACT",
            "CONFIGURED POLICY",
            "Gathering permitted network evidence is allowed.",
        )
    )
    policies.append(
        PolicyEvaluation(
            "pol-auto-recommend",
            "AUTONOMY_ACTION",
            "recommend_step_up",
            "RECOMMEND",
            "CONFIGURED POLICY",
            "STEP_UP is returned as a recommendation.",
        )
    )
    policies.append(
        PolicyEvaluation(
            "pol-auto-decline",
            "AUTONOMY_ACTION",
            "decline_transaction",
            "NOT_AUTHORIZED",
            "CONFIGURED POLICY",
            "Agent is not authorized to decline the financial transaction.",
        )
    )

    finder_ops = []
    for cand in candidates:
        op_row = cand["operation"]
        if not op_row:
            continue
        finder_ops.append(
            {
                "capabilityId": cand["capability"]["id"],
                "capability": cand["capability"].get("label"),
                "operationId": op_row["operationId"],
                "family": (cand["family"] or {}).get("label"),
                "available": cand["available"],
                "provider": provider_label if cand["available"] else None,
            }
        )

    telco = seed.get("telcoFinder") or {}
    api_finder = {
        "neededBecause": "Capabilities and catalog candidates are known. API Finder resolves which API/provider combinations are available on the selected network.",
        "network": provider_label,
        "results": finder_ops,
        "simulated": True,
        "note": "Availability is simulated/configured. Not universal real-world operator coverage.",
    }

    known = {
        "source": "FROM ONBOARDING / CONFIGURATION",
        "rows": [
            {"label": "Enterprise", "value": enterprise.get("label")},
            {"label": "Application", "value": application.get("label")},
            {"label": "Authorized Agent", "value": agent.get("label")},
            {"label": "Domain", "value": (domain or {}).get("label")},
            {"label": "Use case", "value": (use_case or {}).get("label")},
            {"label": "Purpose", "value": purpose.get("audienceLabel") or purpose.get("label")},
            {"label": "Subscriptions", "value": "Configured"},
            {"label": "Entitlements", "value": "Configured"},
            {"label": "Policy", "value": policy.get("label")},
            {"label": "Consent", "value": "Configured (location required, not available)"},
            {"label": "Agreement / DPA", "value": "Configured"},
            {"label": "Region", "value": "CA"},
            {"label": "Provider relationships", "value": "Configured"},
            {"label": "Autonomy rules", "value": "Configured"},
        ],
    }

    beats = [
        Beat(1, 0, "ROCKET BANK / AGENT", "AGENT_AUTHENTICATED", "Agent authenticated", f"{agent.get('label')} acts for {application.get('label')}.", "agent"),
        Beat(2, 400, "NETAWARE AX", "INTENT_RECEIVED", "Intent received", "assess_network_trust — small business request.", "netaware"),
        Beat(3, 800, "CONTEXT / POLICY", "CONTEXT_RESOLVED", "Context resolved", "Enterprise, application, subscriptions and policy loaded from onboarding.", "policy"),
        Beat(4, 1100, "CONTEXT / POLICY", "ACTOR_CHECKED", "Agent authorization checked", "Intent is in allowedIntents.", "policy"),
        Beat(5, 1400, "CONTEXT / POLICY", "PURPOSE_RESOLVED", "Purpose resolved from configuration", str(purpose.get("audienceLabel") or purpose.get("label")), "policy"),
        Beat(6, 1700, "CATALOG / FINDERS", "USE_CASE_RESOLVED", "Intent → use case", str((use_case or {}).get("label")), "catalog"),
        Beat(7, 2000, "CATALOG / FINDERS", "CAPABILITIES_RESOLVED", "Required / potentially relevant capabilities", "Possession, SIM, device, identifier, recycling, roaming, location.", "catalog"),
        Beat(8, 2300, "CATALOG / FINDERS", "CATALOG_RESOLVED", "Capabilities → active API catalog", "Real operationIds from AX_ACTIVE_CATALOG.", "catalog"),
        Beat(9, 2700, "CATALOG / FINDERS", "TELCO_FINDER", "Telco Finder", f"{telco.get('neededBecause')}", "finder"),
        Beat(10, 3100, "CATALOG / FINDERS", "API_FINDER", "API Finder", f"Available APIs on {provider_label}.", "finder"),
        Beat(11, 3400, "NETWORK PROVIDER", "ROUTE_SELECTED", "Route selected", f"NetAware → {provider_label} ({route_type}). Not a hosting claim.", "provider"),
        Beat(12, 3700, "NETAWARE AX", "PLAN_CREATED", "Plan created", "Minimum sufficient network evidence.", "netaware"),
        Beat(13, 4100, "NETWORK PROVIDER", "INVOKED", "phoneNumberVerify", "Number possession verified.", "provider"),
        Beat(14, 4600, "NETWORK PROVIDER", "INVOKED", "checkSimSwap", "Recent SIM change.", "provider"),
        Beat(15, 5100, "NETWORK PROVIDER", "INVOKED", "checkDeviceSwap", "New device.", "provider"),
        Beat(16, 5600, "NETWORK PROVIDER", "INVOKED", "retrieveIdentifier", "Device identity changed. Initial pre-stable API version.", "provider"),
        Beat(17, 6100, "NETWORK PROVIDER", "INVOKED", "getRoamingStatus", "Not roaming.", "provider"),
        Beat(18, 6500, "CONTEXT / POLICY", "BLOCKED_BY_POLICY", "Location verification blocked", "Consent required and not available. Configured demo policy.", "policy"),
        Beat(19, 6900, "NETAWARE AX", "REPLAN", "Continue without location", "Other evidence is sufficient to assess network trust.", "netaware"),
        Beat(20, 7300, "NETAWARE AX", "NOT_REQUIRED", "Number recycling not invoked", "API economy — mapped does not mean invoked.", "netaware"),
        Beat(21, 7700, "NETAWARE AX", "EVIDENCE", "Evidence combined", "SIM disruption + new device identity.", "netaware"),
        Beat(22, 8100, "CONTEXT / POLICY", "AUTONOMY", "Autonomy check", "Recommend STEP_UP. Decline is not authorized.", "policy"),
        Beat(23, 8500, "ROCKET BANK / AGENT", "OUTCOME", "Business outcome returned", "STEP_UP. Rocket Bank owns the financial decision.", "agent"),
    ]

    invoked_ops = {i.operationId for i in invocations}
    if loc and (loc["operation"] or {}).get("operationId") in invoked_ops:
        raise HTTPException(status_code=500, detail="blocked location was invoked")

    trace = ExecutionTrace(
        executionId=str(corr.get("executionId")),
        traceId=str(corr.get("traceId")),
        correlationId=str(corr.get("correlationId")),
        intentId=intent_id,
        status="COMPLETED",
        request=req_body,
        knownFromConfiguration=known,
        purpose={
            "id": purpose.get("id"),
            "label": purpose.get("audienceLabel") or purpose.get("label"),
            "source": "RESOLVED FROM CONFIGURATION",
            "note": "Runtime context does not silently redefine Purpose.",
        },
        actor={
            "agent": agent,
            "application": application,
            "enterprise": enterprise,
            "kind": "AUTHORIZED_AGENT",
        },
        telcoFinder=telco,
        apiFinder=api_finder,
        route={
            "type": route_type,
            "from": "NetAware",
            "to": provider_label,
            "providerId": provider_id,
            "display": f"NetAware → {provider_label}",
            "note": "Configured route for this scenario. Not a commercial or hosting claim.",
        },
        plan=plan,
        decisions=decisions,
        invocations=invocations,
        evidence=evidence,
        policyEvaluations=policies,
        autonomy=autonomy,
        outcome=outcome,
        economy={
            "catalogFamiliesAvailable": len(registry.families),
            "mappedToIntent": len(mapped),
            "selected": len(invoke_order),
            "invoked": len(invocations),
            "consideredNotRequired": 1,
            "blockedByPolicy": 1,
            "notRequiredUnmapped": 1,
            "note": "13 business families available. Mapped ≠ invoked. Minimum sufficient network evidence.",
        },
        beats=beats,
        honesty={
            "simulated": True,
            "liveOperators": False,
            "policyIsConfiguredDemo": True,
            "networkSignalsAreNotFraudProof": True,
            "identityArchitectureUnresolved": True,
        },
    )
    _persist_trust_evidence(
        trace,
        enterprise_id=str(enterprise["id"]),
        application_id=str(application["id"]),
        agent_id=agent_id,
        subject=req_body["subject"],
    )
    return trace


def _persist_trust_evidence(
    trace: ExecutionTrace,
    *,
    enterprise_id: str,
    application_id: str,
    agent_id: str,
    subject: dict[str, Any],
) -> None:
    cap_map = {
        "phoneNumberVerify": "number_possession_verification",
        "checkSimSwap": "sim_continuity",
        "checkDeviceSwap": "device_continuity",
        "retrieveIdentifier": "device_identifier",
        "getRoamingStatus": "roaming_status",
    }
    persist_from_trace(
        trace,
        enterprise_id=enterprise_id,
        application_id=application_id,
        agent_id=agent_id,
        subject=subject,
        capability_for_op=cap_map,
        created_offset_ms=42_000,
    )


def run_assess_recovery_continuity(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    request: dict[str, Any],
) -> ExecutionTrace:
    intent_id = "assess_recovery_continuity"
    seed = load_scenario(intent_id).get("scenario") or {}
    if intent_id not in EXECUTABLE_INTENTS:
        raise HTTPException(status_code=409, detail=f"Intent not executable: {intent_id}")

    agent_id = str(request.get("agentId") or seed.get("agentId"))
    agent = store.agent_by_id.get(agent_id)
    if not agent:
        raise HTTPException(status_code=403, detail="Unknown agent")
    if intent_id not in (agent.get("allowedIntents") or []):
        raise HTTPException(status_code=403, detail="Agent is not authorized for this intent")

    application = store.application_by_id.get(str(agent.get("actsOnBehalfOf") or ""))
    enterprise = store.enterprise_by_id.get(str(agent.get("enterpriseId") or ""))
    if not application or not enterprise:
        raise HTTPException(status_code=403, detail="Agent application/enterprise not resolved")

    intent = store.intent_by_id.get(intent_id) or {}
    uc_id = graph.intent_use_case.get(intent_id)
    use_case = store.use_case_by_id.get(uc_id or "")
    domain = store.domain_by_id.get(str((use_case or {}).get("domainId") or enterprise.get("domainId") or ""))
    policy = next((p for p in store.policies if p.get("id") == seed.get("policyId")), None)
    if not policy:
        raise HTTPException(status_code=500, detail="Scenario policy missing")
    purpose = store.purpose_by_id.get(str(policy.get("purposeId") or intent.get("defaultPurposeId") or ""))
    if not purpose:
        raise HTTPException(status_code=500, detail="Purpose not resolved from configuration")

    corr = seed.get("correlation") or {}
    req_body = {
        "intent": intent_id,
        "subject": (request.get("subject") or seed.get("request", {}).get("subject")),
        "context": (request.get("context") or seed.get("request", {}).get("context")),
    }
    provider_id = str(seed.get("selectedProviderId"))
    provider_label = str(seed.get("providerAudienceLabel") or "Network Provider A")
    route_type = str(seed.get("selectedRouteType") or "DIRECT")
    advertised = _provider_ops(store, provider_id)
    responses = seed.get("simulatedResponses") or {}

    mapped = list(graph.intent_caps.get(intent_id) or [])
    invoke_order = ["sim_continuity", "device_continuity", "roaming_status"]

    plan_steps = [
        PlanStep(1, "Check SIM continuity", "sim_continuity", "checkSimSwap"),
        PlanStep(2, "Check device continuity", "device_continuity", "checkDeviceSwap"),
        PlanStep(3, "Check roaming context", "roaming_status", "getRoamingStatus"),
        PlanStep(4, "Evaluate recovery continuity", None, None),
        PlanStep(5, "Return continuity assessment", None, None),
    ]
    plan = Plan(
        id="plan-rb-recovery",
        intentId=intent_id,
        executionId=str(corr.get("executionId")),
        steps=plan_steps,
    )

    invocations: list[Invocation] = []
    evidence: list[Evidence] = []
    decisions: list[Decision] = []
    policies: list[PolicyEvaluation] = [
        PolicyEvaluation(
            "pol-actor-auth",
            "ACTOR_INTENT",
            "agent",
            "AUTHORIZED",
            "CONFIGURED POLICY",
            f"{agent.get('label')} is authorized for recovery continuity assessment.",
        ),
        PolicyEvaluation(
            "pol-evidence-reuse",
            "EVIDENCE_REUSE",
            "normalized_evidence",
            "EVALUATED",
            "CONFIGURED POLICY",
            "Reuse requires tenant scope, subject correlation, compatible purpose, policy permission, TTL and evidence type match.",
        ),
    ]
    reused_count = 0

    for cap_id in invoke_order:
        link = next((l for l in mapped if l.get("capabilityId") == cap_id), None)
        cap = store.capability_by_id.get(cap_id) or {"id": cap_id}
        fam = _family_for(registry, cap_id)
        op_row = _primary_op(graph, cap_id)
        if not op_row:
            continue
        op_id = str(op_row["operationId"])
        meta = _op_meta(registry, op_id, str(op_row["source"]))
        pol = evaluate_capability_policy(
            store,
            enterprise_id=str(enterprise["id"]),
            policy_id=str(policy["id"]),
            purpose=purpose,
            capability_id=cap_id,
            family=str((fam or {}).get("familyGroup") or cap.get("family")),
        )
        policies.append(
            PolicyEvaluation(
                f"pol-cap-{cap_id}",
                "CAPABILITY_API",
                cap_id,
                pol["result"],
                "CONFIGURED POLICY",
                pol["detail"],
            )
        )
        if pol["result"] != "PERMITTED":
            decisions.append(
                Decision(
                    id=f"dec-{cap_id}",
                    capabilityId=cap_id,
                    familyId=(fam or {}).get("id"),
                    operationId=op_id,
                    label=cap.get("label"),
                    relevant=True,
                    availability="YES" if op_id in advertised else "NO",
                    policyResult=pol["result"],
                    state=pol["result"],
                    why=pol["detail"],
                    stage="CAPABILITY_API",
                )
            )
            continue

        stored, audit = find_reusable(
            enterprise_id=str(enterprise["id"]),
            application_id=str(application["id"]),
            agent_id=agent_id,
            subject=req_body["subject"],
            subject_key_override=str(req_body["subject"].get("phoneNumber") or ""),
            operation_id=op_id,
            capability_id=cap_id,
            target_purpose_id=str(purpose["id"]),
            policy_allows=True,
        )
        if stored and audit.get("decision") == "EVIDENCE_REUSED":
            reused_count += 1
            evidence.append(
                Evidence(
                    id=f"ev-reuse-{op_id}",
                    operationId=op_id,
                    type=stored.evidenceType,
                    status=str(stored.payload.get("status") or "reused"),
                    payload=dict(stored.payload),
                    purposeId=str(purpose["id"]),
                    reuseEligible=True,
                    reused=True,
                    sourceExecutionId=stored.executionId,
                    sourceTraceId=stored.traceId,
                    ageSeconds=stored.age_seconds(),
                    reuseAudit=audit,
                )
            )
            decisions.append(
                Decision(
                    id=f"dec-{cap_id}",
                    capabilityId=cap_id,
                    familyId=(fam or {}).get("id"),
                    operationId=op_id,
                    label=cap.get("label"),
                    relevant=True,
                    availability="YES",
                    policyResult="PERMITTED",
                    state="EVIDENCE_REUSED",
                    why=(
                        f"Existing evidence found (age {stored.age_seconds()}s, TTL {stored.ttlSeconds}s). "
                        f"Purpose compatible. Policy permits reuse. Source execution {stored.executionId}. API invocation skipped."
                    ),
                    stage="EVIDENCE_REUSE",
                )
            )
            continue

        sim = responses.get(op_id) or {}
        inv = Invocation(
            id=f"inv-{op_id}",
            operationId=op_id,
            source=str(op_row["source"]),
            familyId=str((fam or {}).get("id") or meta.get("api_id")),
            familyLabel=str((fam or {}).get("label") or meta.get("family")),
            specMaturity=str(meta.get("spec_maturity")),
            businessStatus=str(meta.get("business_status")),
            method=str(meta.get("method")),
            providerId=provider_id,
            providerLabel=provider_label,
            routeType=route_type,
            correlationId=str(corr.get("correlationId")),
            latencyMs=int(sim.get("latencyMs") or 40),
            httpStatus=int(sim.get("httpStatus") or 200),
            raw=sim.get("raw") or {},
        )
        invocations.append(inv)
        ev = sim.get("evidence") or {}
        evidence.append(
            Evidence(
                id=f"ev-{op_id}",
                operationId=op_id,
                type=str(ev.get("type") or op_id),
                status=str(ev.get("status") or "observed"),
                payload={k: v for k, v in ev.items() if k not in {"type"}},
                purposeId=str(purpose["id"]),
            )
        )
        decisions.append(
            Decision(
                id=f"dec-{cap_id}",
                capabilityId=cap_id,
                familyId=(fam or {}).get("id"),
                operationId=op_id,
                label=cap.get("label"),
                relevant=True,
                availability="YES",
                policyResult="PERMITTED",
                state="INVOKED",
                why="No reusable evidence matched eligibility checks. Invoked fresh network evidence.",
                stage="EXECUTION",
            )
        )

    for step in plan.steps:
        if step.operationId in {i.operationId for i in invocations}:
            step.state = "INVOKED"
        elif step.capabilityId in {d.capabilityId for d in decisions if d.state == "EVIDENCE_REUSED"}:
            step.state = "EVIDENCE_REUSED"
        elif step.operationId is None:
            step.state = "COMPLETED"

    out_seed = seed.get("outcome") or {}
    outcome = Outcome(
        outcome=str(out_seed.get("outcome") or "CONTINUITY_ALIGNED"),
        networkTrust=str(out_seed.get("networkTrust") or "DISRUPTED"),
        confidence=float(out_seed.get("confidence") or 0.91),
        recommendedAction=str(out_seed.get("recommendedAction") or "STEP_UP_RECOVERY"),
        decisionOwner=str(out_seed.get("decisionOwner") or "ENTERPRISE"),
        reasonCodes=list(out_seed.get("reasonCodes") or ["RECENT_SIM_CHANGE"]),
        summary=str(
            out_seed.get("summary")
            or "Recovery continuity assessed using reusable trust evidence where eligible."
        ),
    )

    autonomy = {
        "assess_recovery_continuity": "ACT",
        "reset_recovery_credentials": "NOT_AUTHORIZED",
        "selectedAction": "assess_recovery_continuity",
        "selectedLevel": "ACT",
        "note": "Agent may assess continuity. Credential reset remains with Rocket Bank.",
        "source": "CONFIGURED POLICY",
    }

    known = {
        "source": "FROM ONBOARDING / CONFIGURATION",
        "rows": [
            {"label": "Enterprise", "value": enterprise.get("label")},
            {"label": "Application", "value": application.get("label")},
            {"label": "Authorized Agent", "value": agent.get("label")},
            {"label": "Use case", "value": (use_case or {}).get("label")},
            {"label": "Purpose", "value": purpose.get("audienceLabel") or purpose.get("label")},
            {"label": "Policy", "value": policy.get("label")},
            {"label": "Evidence reuse", "value": "Enabled when eligibility checks pass"},
        ],
    }

    beats = [
        Beat(1, 0, "ROCKET BANK / AGENT", "INTENT_RECEIVED", "Recovery intent received", "assess_recovery_continuity", "agent"),
        Beat(2, 400, "NETAWARE AX", "EVIDENCE_STORE", "Evidence store consulted", "Tenant, subject, purpose, TTL and policy evaluated.", "netaware"),
        Beat(3, 900, "NETAWARE AX", "EVIDENCE_REUSED", "SIM continuity reused", "checkSimSwap skipped — source ax-rb-trust-001.", "netaware"),
        Beat(4, 1300, "NETAWARE AX", "EVIDENCE_REUSED", "Device continuity reused", "checkDeviceSwap skipped.", "netaware"),
        Beat(5, 1700, "NETAWARE AX", "EVIDENCE_REUSED", "Roaming reused", "getRoamingStatus skipped.", "netaware"),
        Beat(6, 2200, "NETAWARE AX", "OUTCOME", "Continuity assessment returned", str(outcome.summary), "netaware"),
    ]

    return ExecutionTrace(
        executionId=str(corr.get("executionId")),
        traceId=str(corr.get("traceId")),
        correlationId=str(corr.get("correlationId")),
        intentId=intent_id,
        status="COMPLETED",
        request=req_body,
        knownFromConfiguration=known,
        purpose={
            "id": purpose.get("id"),
            "label": purpose.get("audienceLabel") or purpose.get("label"),
            "source": "CONFIGURED APPLICATION / INTENT PROFILE",
            "note": "Purpose differs from trust assessment but reuse matrix permits normalized evidence.",
        },
        actor={
            "agent": agent,
            "application": application,
            "enterprise": enterprise,
            "kind": "AUTHORIZED_AGENT",
        },
        telcoFinder=seed.get("telcoFinder") or {},
        apiFinder={"neededBecause": "Fresh invocation only when reuse eligibility fails.", "simulated": True},
        route={
            "type": route_type,
            "from": "NetAware",
            "to": provider_label,
            "providerId": provider_id,
            "display": f"NetAware → {provider_label}",
            "note": "Configured route. Not a hosting claim.",
        },
        plan=plan,
        decisions=decisions,
        invocations=invocations,
        evidence=evidence,
        policyEvaluations=policies,
        autonomy=autonomy,
        outcome=outcome,
        economy={
            "catalogFamiliesAvailable": len(registry.families),
            "mappedToIntent": len(mapped),
            "invoked": len(invocations),
            "evidenceReused": reused_count,
            "note": "Normalized policy-aware evidence reused across intents. Not raw response caching.",
        },
        beats=beats,
        honesty={
            "simulated": True,
            "liveOperators": False,
            "policyIsConfiguredDemo": True,
            "evidenceReuse": True,
        },
    )


def _domain_invocation(
    *,
    op_id: str,
    api_kind: str,
    owner: str,
    label: str,
    corr_id: str,
    sim: dict[str, Any],
) -> Invocation:
    return Invocation(
        id=f"inv-{op_id}",
        operationId=op_id,
        source="SIMULATED DOMAIN API" if api_kind == "DOMAIN" else "SIMULATED ENTERPRISE API",
        familyId=op_id,
        familyLabel=label,
        specMaturity="",
        businessStatus="SIMULATED",
        method="GET",
        providerId="",
        providerLabel=owner,
        routeType=api_kind,
        correlationId=corr_id,
        latencyMs=int(sim.get("latencyMs") or 40),
        httpStatus=int(sim.get("httpStatus") or 200),
        raw=sim.get("raw") or {},
        apiKind=api_kind,
        simulated=True,
        owner=owner,
        routeDisplay=f"{owner} · {label}",
    )


def _network_invocation(
    *,
    op_id: str,
    meta: dict[str, Any],
    fam: dict[str, Any],
    route: dict[str, Any],
    corr_id: str,
    sim: dict[str, Any],
    op_row: dict[str, Any],
) -> Invocation:
    route_type = str(route.get("routeType") or "DIRECT")
    provider_id = str(route.get("providerId") or "")
    provider_label = str(route.get("providerLabel") or "Network Provider A")
    aggregator = str(route.get("aggregatorLabel") or "")
    route_display = str(route.get("routeDisplay") or f"NetAware → {provider_label}")
    return Invocation(
        id=f"inv-{op_id}",
        operationId=op_id,
        source=str(op_row["source"]),
        familyId=str(fam.get("id") or meta.get("api_id")),
        familyLabel=str(fam.get("label") or meta.get("family")),
        specMaturity=str(meta.get("spec_maturity") or ""),
        businessStatus=str(meta.get("business_status") or ""),
        method=str(meta.get("method") or "GET"),
        providerId=provider_id,
        providerLabel=provider_label,
        routeType=route_type,
        correlationId=corr_id,
        latencyMs=int(sim.get("latencyMs") or 40),
        httpStatus=int(sim.get("httpStatus") or 200),
        raw=sim.get("raw") or {},
        apiKind="NETWORK",
        aggregatorLabel=aggregator,
        routeDisplay=route_display,
    )


def run_ensure_baggage_connection(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    request: dict[str, Any],
) -> ExecutionTrace:
    from .hf_runtime import run_ensure_baggage_connection as _run_hf

    return _run_hf(store, graph, registry, request)


def _append_network_invocation(
    *,
    invocations: list[Invocation],
    evidence: list[Evidence],
    route_records: list[dict[str, Any]],
    op_id: str,
    inv_id: str,
    meta: dict[str, Any],
    fam: dict[str, Any],
    route_cfg: dict[str, Any],
    corr_id: str,
    sim: dict[str, Any],
    op_row: dict[str, Any],
    purpose_id: str,
    ev_id: str | None = None,
) -> None:
    inv = _network_invocation(
        op_id=op_id,
        meta=meta,
        fam=fam,
        route=route_cfg,
        corr_id=corr_id,
        sim=sim,
        op_row=op_row,
    )
    inv.id = inv_id
    invocations.append(inv)
    route_records.append(
        {
            "operationId": op_id,
            "phase": inv_id.replace(f"inv-{op_id}-", "") or "default",
            "type": inv.routeType,
            "display": inv.routeDisplay,
            "providerId": inv.providerId,
            "providerLabel": inv.providerLabel,
            "aggregatorLabel": inv.aggregatorLabel,
        }
    )
    ev = sim.get("evidence") or {}
    evidence.append(
        Evidence(
            id=ev_id or f"ev-{inv_id}",
            operationId=op_id,
            type=str(ev.get("type") or op_id),
            status=str(ev.get("status") or "observed"),
            payload={k: v for k, v in ev.items() if k not in {"type"}},
            purposeId=purpose_id,
            apiKind="NETWORK",
        )
    )


def run_maintain_inspection_experience(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    request: dict[str, Any],
) -> ExecutionTrace:
    intent_id = "maintain_inspection_experience"
    seed = load_scenario(intent_id).get("scenario") or {}

    agent_id = str(request.get("agentId") or seed.get("agentId"))
    agent = store.agent_by_id.get(agent_id)
    if not agent:
        raise HTTPException(status_code=403, detail="Unknown agent")
    if intent_id not in (agent.get("allowedIntents") or []):
        raise HTTPException(status_code=403, detail="Agent is not authorized for this intent")

    application = store.application_by_id.get(str(agent.get("actsOnBehalfOf") or ""))
    enterprise = store.enterprise_by_id.get(str(agent.get("enterpriseId") or ""))
    if not application or not enterprise:
        raise HTTPException(status_code=403, detail="Agent application/enterprise not resolved")

    intent = store.intent_by_id.get(intent_id) or {}
    uc_id = graph.intent_use_case.get(intent_id)
    use_case = store.use_case_by_id.get(uc_id or "")
    domain = store.domain_by_id.get(str((use_case or {}).get("domainId") or enterprise.get("domainId") or ""))
    policy = next((p for p in store.policies if p.get("id") == seed.get("policyId")), None)
    if not policy:
        raise HTTPException(status_code=500, detail="Scenario policy missing")
    purpose = store.purpose_by_id.get(str(policy.get("purposeId") or intent.get("defaultPurposeId") or ""))
    if not purpose:
        raise HTTPException(status_code=500, detail="Purpose not resolved from configuration")

    corr = seed.get("correlation") or {}
    req_body = {
        "intent": intent_id,
        "subject": (request.get("subject") or seed.get("request", {}).get("subject")),
        "context": (request.get("context") or seed.get("request", {}).get("context")),
    }
    slo_ms = int((req_body.get("context") or {}).get("sloMs") or seed.get("sloMs") or 40)
    network_responses = seed.get("networkResponses") or {}
    network_routes = seed.get("networkRoutes") or {}
    telco = seed.get("telcoFinder") or {}
    provider_label = str((telco.get("result") or {}).get("network") or "Network Provider C")
    condition_change = seed.get("conditionChange") or {}
    mapped = list(graph.intent_caps.get(intent_id) or [])

    exec_id = str(corr.get("executionId"))
    plan_v1 = Plan(
        id="plan-acme-v1",
        intentId=intent_id,
        executionId=exec_id,
        version=1,
        label="PLAN v1",
        steps=[
            PlanStep(1, "Resolve inspection objective / SLO", None, None),
            PlanStep(2, "Observe current connectivity/network quality", "connectivity_insights", "checkNetworkQuality", "NETWORK"),
            PlanStep(3, "Determine relevant application profile", "application_profiles", "createApplicationProfile", "NETWORK"),
            PlanStep(4, "Consider closest edge if useful", "edge_discovery", "readClosestEdgeCloudZone", "NETWORK"),
            PlanStep(5, "Consider QoD if network treatment could change outcome", "quality_on_demand", "createSession", "NETWORK"),
            PlanStep(6, "Evaluate whether objective is currently satisfied", None, None),
        ],
    )
    plan_v2 = Plan(
        id="plan-acme-v2",
        intentId=intent_id,
        executionId=exec_id,
        version=2,
        label="PLAN v2",
        supersedes=plan_v1.id,
        note="Objective breached. Select permitted QoD treatment and verify restoration.",
        steps=[
            PlanStep(1, "Observe degraded experience", "connectivity_insights", "checkNetworkQuality", "NETWORK", "INVOKED", "changed"),
            PlanStep(2, "Re-evaluate available network actions", None, None),
            PlanStep(3, "Select appropriate QoS profile", "quality_on_demand", "retrieveQoSProfiles", "NETWORK", "PLANNED", "added"),
            PlanStep(4, "Create QoD session / assignment", "quality_on_demand", "createSession", "NETWORK", "PLANNED", "added"),
            PlanStep(5, "Observe resulting state", "connectivity_insights", "checkNetworkQuality", "NETWORK"),
            PlanStep(6, "Verify objective restored", "quality_on_demand", "getSession", "NETWORK"),
        ],
    )

    invocations: list[Invocation] = []
    evidence: list[Evidence] = []
    decisions: list[Decision] = []
    policies: list[PolicyEvaluation] = [
        PolicyEvaluation(
            "pol-actor-auth",
            "ACTOR_INTENT",
            "agent",
            "AUTHORIZED",
            "CONFIGURED POLICY",
            f"{agent.get('label')} is an authorized agent for {application.get('label')}.",
        ),
        PolicyEvaluation(
            "pol-actor-intent",
            "ACTOR_INTENT",
            "intent",
            "ALLOWED",
            "CONFIGURED POLICY",
            f"Intent {intent_id} is in the agent's allowedIntents.",
        ),
        PolicyEvaluation(
            "pol-actor-purpose",
            "ACTOR_INTENT",
            "purpose",
            "RESOLVED_FROM_CONFIGURATION",
            "CONFIGURED POLICY",
            f"Purpose {(purpose.get('audienceLabel') or purpose.get('label'))} resolved from application/intent profile.",
        ),
    ]
    route_records: list[dict[str, Any]] = []
    purpose_id = str(purpose["id"])

    candidates: list[dict[str, Any]] = []
    for link in mapped:
        cap_id = str(link["capabilityId"])
        cap = store.capability_by_id.get(cap_id) or {"id": cap_id}
        fam = _family_for(registry, cap_id)
        op_row = _primary_op(graph, cap_id)
        meta = _op_meta(registry, str(op_row["operationId"]), str(op_row["source"])) if op_row else {}
        pol = evaluate_capability_policy(
            store,
            enterprise_id=str(enterprise["id"]),
            policy_id=str(policy["id"]),
            purpose=purpose,
            capability_id=cap_id,
            family=str((fam or {}).get("familyGroup") or cap.get("family")),
        )
        candidates.append(
            {
                "capability": cap,
                "role": link.get("role"),
                "family": fam,
                "operation": op_row,
                "catalog": meta,
                "policy": pol,
                "available": bool(op_row),
            }
        )

    conn = next((c for c in candidates if c["capability"]["id"] == "connectivity_insights"), None)
    prof = next((c for c in candidates if c["capability"]["id"] == "application_profiles"), None)
    edge = next((c for c in candidates if c["capability"]["id"] == "edge_discovery"), None)
    qod = next((c for c in candidates if c["capability"]["id"] == "quality_on_demand"), None)

    if conn and conn["operation"]:
        op_row = conn["operation"]
        meta = conn["catalog"]
        fam = conn["family"] or {}
        op_id = str(op_row["operationId"])
        _append_network_invocation(
            invocations=invocations,
            evidence=evidence,
            route_records=route_records,
            op_id=op_id,
            inv_id="inv-checkNetworkQuality-initial",
            meta=meta,
            fam=fam,
            route_cfg=network_routes.get(op_id) or {},
            corr_id=str(corr.get("correlationId")),
            sim=network_responses.get("checkNetworkQuality_initial") or {},
            op_row=op_row,
            purpose_id=purpose_id,
            ev_id="ev-checkNetworkQuality-initial",
        )
        plan_v1.steps[1].state = "INVOKED"
        decisions.append(
            Decision(
                id="dec-connectivity_observe",
                capabilityId="connectivity_insights",
                familyId=fam.get("id"),
                operationId=op_id,
                label=conn["capability"].get("label"),
                relevant=True,
                availability="YES",
                policyResult="PERMITTED",
                state="INVOKED",
                why=f"Observe whether application objective is met. Latency 32ms within SLO {slo_ms}ms — objective SATISFIED.",
                stage="EXECUTION",
            )
        )

    if prof and prof["operation"]:
        op_row = prof["operation"]
        meta = prof["catalog"]
        fam = prof["family"] or {}
        op_id = str(op_row["operationId"])
        _append_network_invocation(
            invocations=invocations,
            evidence=evidence,
            route_records=route_records,
            op_id=op_id,
            inv_id=f"inv-{op_id}",
            meta=meta,
            fam=fam,
            route_cfg=network_routes.get(op_id) or {},
            corr_id=str(corr.get("correlationId")),
            sim=network_responses.get(op_id) or {},
            op_row=op_row,
            purpose_id=purpose_id,
        )
        plan_v1.steps[2].state = "INVOKED"
        decisions.append(
            Decision(
                id="dec-application_profiles",
                capabilityId="application_profiles",
                familyId=fam.get("id"),
                operationId=op_id,
                label=prof["capability"].get("label"),
                relevant=True,
                availability="YES",
                policyResult="PERMITTED",
                state="INVOKED",
                why="Associate inspection video service requirements with the observed network context.",
                stage="EXECUTION",
            )
        )

    if edge:
        fam = edge["family"] or {}
        policies.append(
            PolicyEvaluation(
                "pol-cap-edge_discovery",
                "CAPABILITY_API",
                "edge_discovery",
                "PERMITTED",
                "CONFIGURED POLICY",
                "Permitted but not required for this inspection objective.",
            )
        )
        decisions.append(
            Decision(
                id="dec-edge_discovery",
                capabilityId="edge_discovery",
                familyId=fam.get("id"),
                operationId=(edge["operation"] or {}).get("operationId"),
                label=edge["capability"].get("label"),
                relevant=False,
                availability="YES",
                policyResult="PERMITTED",
                state="NOT_REQUIRED",
                why="Considered only if relevant. Edge discovery is not required for this camera SLO on the plant uplink.",
                stage="PLAN",
            )
        )
        plan_v1.steps[3].state = "NOT_REQUIRED"

    if qod:
        fam = qod["family"] or {}
        policies.append(
            PolicyEvaluation(
                "pol-cap-quality_on_demand",
                "CAPABILITY_API",
                "quality_on_demand",
                "PERMITTED",
                "CONFIGURED POLICY",
                "QoD is available, entitled, and permitted. Autonomy ACT when objective requires it.",
            )
        )
        decisions.append(
            Decision(
                id="dec-qod-initial",
                capabilityId="quality_on_demand",
                familyId=fam.get("id"),
                operationId="createSession",
                label=qod["capability"].get("label"),
                relevant=True,
                availability="YES",
                policyResult="PERMITTED",
                state="NOT_REQUIRED",
                why="AVAILABLE, ENTITLED, PERMITTED, autonomy ACT — but NOT_REQUIRED because THE OUTCOME IS ALREADY SATISFIED.",
                stage="PLAN",
            )
        )
        plan_v1.steps[4].state = "NOT_REQUIRED"
        plan_v1.steps[5].state = "COMPLETED"

    replan = {
        "trigger": str(condition_change.get("trigger") or "OBJECTIVE_BREACH"),
        "constraint": str(condition_change.get("detail") or "Observed latency exceeded SLO."),
        "whatChanged": [
            "Objective changed from SATISFIED to NOT_SATISFIED",
            "QoD moved from NOT_REQUIRED to SELECTED",
            "Added QoS profile selection and session creation",
            "Added post-action observation and verification",
        ],
        "narrative": "Observed service objective violated. Select permitted QoD treatment and verify restoration.",
        "planV1": plan_v1.id,
        "planV2": plan_v2.id,
        "fromObjective": condition_change.get("fromObjective"),
        "toObjective": condition_change.get("toObjective"),
    }

    if qod:
        for op_key, cap_label, step_n in [
            ("retrieveQoSProfiles", "Select QoS profile", 3),
            ("createSession", "Create QoD session", 4),
        ]:
            op_row = _primary_op(graph, "quality_on_demand")
            if op_key == "retrieveQoSProfiles":
                op_row = next((r for r in _cap_ops(graph, "quality_on_demand") if r.get("operationId") == op_key), op_row)
            meta = _op_meta(registry, op_key, str(op_row["source"]))
            fam = qod["family"] or {}
            _append_network_invocation(
                invocations=invocations,
                evidence=evidence,
                route_records=route_records,
                op_id=op_key,
                inv_id=f"inv-{op_key}",
                meta=meta,
                fam=fam,
                route_cfg=network_routes.get(op_key) or network_routes.get("createSession") or {},
                corr_id=str(corr.get("correlationId")),
                sim=network_responses.get(op_key) or {},
                op_row={"operationId": op_key, "source": op_row["source"]},
                purpose_id=purpose_id,
            )
            plan_v2.steps[step_n - 1].state = "INVOKED"
            decisions.append(
                Decision(
                    id=f"dec-{op_key}",
                    capabilityId="quality_on_demand",
                    familyId=fam.get("id"),
                    operationId=op_key,
                    label=cap_label,
                    relevant=True,
                    availability="YES",
                    policyResult="PERMITTED",
                    state="INVOKED",
                    why="After OBJECTIVE_BREACH, QoD is the permitted network action capable of addressing the limiting factor.",
                    stage="EXECUTION",
                )
            )

    if conn and conn["operation"]:
        op_row = conn["operation"]
        meta = conn["catalog"]
        fam = conn["family"] or {}
        op_id = str(op_row["operationId"])
        _append_network_invocation(
            invocations=invocations,
            evidence=evidence,
            route_records=route_records,
            op_id=op_id,
            inv_id="inv-checkNetworkQuality-verify",
            meta=meta,
            fam=fam,
            route_cfg=network_routes.get(op_id) or {},
            corr_id=str(corr.get("correlationId")),
            sim=network_responses.get("checkNetworkQuality_verify") or {},
            op_row=op_row,
            purpose_id=purpose_id,
            ev_id="ev-checkNetworkQuality-verify",
        )
        plan_v2.steps[4].state = "INVOKED"
        decisions.append(
            Decision(
                id="dec-connectivity_verify",
                capabilityId="connectivity_insights",
                familyId=fam.get("id"),
                operationId=op_id,
                label="Post-action observe",
                relevant=True,
                availability="YES",
                policyResult="PERMITTED",
                state="INVOKED",
                why="Post-action observation verifies whether the intent outcome was achieved. HTTP success alone is not sufficient.",
                stage="VERIFICATION",
            )
        )

    get_sess_row = next((r for r in _cap_ops(graph, "quality_on_demand") if r.get("operationId") == "getSession"), None)
    if get_sess_row:
        meta = _op_meta(registry, "getSession", str(get_sess_row["source"]))
        fam = qod["family"] or {} if qod else {}
        _append_network_invocation(
            invocations=invocations,
            evidence=evidence,
            route_records=route_records,
            op_id="getSession",
            inv_id="inv-getSession",
            meta=meta,
            fam=fam,
            route_cfg=network_routes.get("getSession") or network_routes.get("createSession") or {},
            corr_id=str(corr.get("correlationId")),
            sim=network_responses.get("getSession") or {},
            op_row=get_sess_row,
            purpose_id=purpose_id,
        )
        plan_v2.steps[5].state = "INVOKED"

    out_seed = seed.get("outcome") or {}
    outcome = Outcome(
        outcome=str(out_seed.get("outcome") or "ASSURED"),
        confidence=float(out_seed.get("confidence") or 0.96),
        recommendedAction=str(out_seed.get("recommendedAction") or "NONE"),
        decisionOwner=str(out_seed.get("decisionOwner") or "ACME_QUALITY_INSPECTION"),
        reasonCodes=list(out_seed.get("reasonCodes") or ["EXPERIENCE_DEGRADED", "QOD_APPLIED", "OBJECTIVE_RESTORED"]),
        summary=str(out_seed.get("summary") or "Inspection experience assured after autonomous QoD and verification."),
        objective=str(out_seed.get("objective") or "SATISFIED"),
        sloMs=int(out_seed.get("sloMs") or slo_ms),
        networkAction=str(out_seed.get("networkAction") or "QOD_APPLIED"),
        autonomousAction=bool(out_seed.get("autonomousAction", True)),
        verification=str(out_seed.get("verification") or "PASSED"),
    )

    autonomy = {
        "observe_and_profile": "ACT",
        "invoke_qod": "ACT",
        "change_mes_routing": "NOT_AUTHORIZED",
        "selectedAction": "invoke_qod",
        "selectedLevel": "ACT",
        "approvalRequired": False,
        "note": "Network QoD treatment is authorized within configured policy. Agent may not change MES production schedule.",
        "source": "CONFIGURED POLICY",
    }
    policies.append(
        PolicyEvaluation(
            "pol-auto-qod",
            "AUTONOMY_ACTION",
            "invoke_qod",
            "ACT",
            "CONFIGURED POLICY",
            "Creating permitted QoD session is allowed without human approval for this intent.",
        )
    )
    policies.append(
        PolicyEvaluation(
            "pol-auto-mes",
            "AUTONOMY_ACTION",
            "change_mes_routing",
            "NOT_AUTHORIZED",
            "CONFIGURED POLICY",
            "Agent is not authorized to change MES production schedule.",
        )
    )

    finder_ops = []
    for cand in candidates:
        op_row = cand["operation"]
        if not op_row:
            continue
        finder_ops.append(
            {
                "capabilityId": cand["capability"]["id"],
                "capability": cand["capability"].get("label"),
                "operationId": op_row["operationId"],
                "family": (cand["family"] or {}).get("label"),
                "available": cand["available"],
                "provider": provider_label,
            }
        )

    beats = [
        Beat(1, 0, "ACME INSPECTION AGENT", "AGENT_AUTHENTICATED", "Agent authenticated", f"{agent.get('label')} acts for {application.get('label')}.", "agent"),
        Beat(2, 400, "NETAWARE AX", "INTENT_RECEIVED", "Intent received", "maintain_inspection_experience — maintain camera experience, not 'call QoD'.", "netaware"),
        Beat(3, 800, "CONTEXT / POLICY", "CONTEXT_RESOLVED", "Context resolved", "Plant, SLO, subscriptions, QoD authorization from onboarding.", "policy"),
        Beat(4, 1200, "NETAWARE AX", "PLAN_CREATED", "PLAN v1 created", "Observe-first plan for inspection objective.", "netaware"),
        Beat(5, 1600, "API CATALOG / FINDERS", "TELCO_FINDER", "Telco Finder", telco.get("neededBecause", ""), "finder"),
        Beat(6, 2000, "NETWORK PROVIDER", "OBSERVE", "checkNetworkQuality", f"Initial observe — latency within SLO {slo_ms}ms.", "provider"),
        Beat(7, 2500, "NETWORK PROVIDER", "OBSERVE", "createApplicationProfile", "Inspection video profile associated.", "provider"),
        Beat(8, 2900, "NETAWARE AX", "NOT_REQUIRED", "QoD NOT_REQUIRED", "Objective SATISFIED — autonomy does not mean always act.", "netaware"),
        Beat(9, 3300, "NETAWARE AX", "OBJECTIVE_BREACH", "Condition change", str(condition_change.get("detail")), "netaware"),
        Beat(10, 3700, "NETAWARE AX", "REPLAN", "PLAN v2", replan["narrative"], "netaware"),
        Beat(11, 4100, "NETWORK PROVIDER", "INVOKED", "retrieveQoSProfiles", "Select low-latency video profile.", "provider"),
        Beat(12, 4600, "NETWORK PROVIDER", "INVOKED", "createSession", "QoD session created autonomously (ACT).", "provider"),
        Beat(13, 5100, "NETWORK PROVIDER", "VERIFY", "checkNetworkQuality", "Post-action observe — objective restored.", "provider"),
        Beat(14, 5600, "NETWORK PROVIDER", "VERIFY", "getSession", "Session active — verification PASSED.", "provider"),
        Beat(15, 6000, "ACME INSPECTION AGENT", "OUTCOME", "ASSURED", "Verification passed. HTTP 201 alone is not the outcome.", "agent"),
    ]

    return ExecutionTrace(
        executionId=exec_id,
        traceId=str(corr.get("traceId")),
        correlationId=str(corr.get("correlationId")),
        intentId=intent_id,
        status="COMPLETED",
        request=req_body,
        knownFromConfiguration={
            "source": "FROM ONBOARDING / CONFIGURATION",
            "rows": [
                {"label": "Enterprise", "value": enterprise.get("label")},
                {"label": "Application", "value": application.get("label")},
                {"label": "Authorized Agent", "value": agent.get("label")},
                {"label": "Domain", "value": (domain or {}).get("label")},
                {"label": "Use case", "value": (use_case or {}).get("label")},
                {"label": "Purpose", "value": purpose.get("audienceLabel") or purpose.get("label")},
                {"label": "Purpose source", "value": "CONFIGURED APPLICATION / INTENT PROFILE"},
                {"label": "Configured SLO", "value": f"{slo_ms} ms"},
                {"label": "Existing systems", "value": "MES, QMS, Camera control"},
                {"label": "QoD authorization", "value": "Configured ACT"},
                {"label": "Policy", "value": policy.get("label")},
                {"label": "Region", "value": "plant_region"},
            ],
        },
        purpose={
            "id": purpose.get("id"),
            "label": purpose.get("audienceLabel") or purpose.get("label"),
            "source": "CONFIGURED APPLICATION / INTENT PROFILE",
            "note": "Intent asks for experience objective, not a specific network API.",
        },
        actor={"agent": agent, "application": application, "enterprise": enterprise, "kind": "AUTHORIZED_AGENT"},
        telcoFinder=telco,
        apiFinder={
            "neededBecause": "Plant uplink resolved. API Finder resolves Connectivity, Profiles, Edge and QoD availability.",
            "network": provider_label,
            "results": finder_ops,
            "simulated": True,
        },
        route={"type": "HYBRID", "display": "NetAware → Network Provider C (HYBRID QoD)", "note": "QoD uses configured HYBRID route."},
        routes=route_records,
        plan=plan_v2,
        planHistory=[plan_v1, plan_v2],
        replan=replan,
        conditionChange=condition_change,
        verificationResult={"status": "PASSED", "objective": "SATISFIED", "note": "Post-action observation confirms intent outcome."},
        decisions=decisions,
        invocations=invocations,
        evidence=evidence,
        policyEvaluations=policies,
        autonomy=autonomy,
        outcome=outcome,
        economy={
            "catalogFamiliesAvailable": len(registry.families),
            "mappedToIntent": len(mapped),
            "invoked": len(invocations),
            "consideredNotRequired": 2,
            "note": "Observe first. QoD invoked only after objective breach. Verification is mandatory.",
        },
        beats=beats,
        honesty={"simulated": True, "liveOperators": False, "policyIsConfiguredDemo": True, "actionNotEqualToSuccess": True},
    )


def run_verify_pharmacy_age_gate(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    request: dict[str, Any],
) -> ExecutionTrace:
    intent_id = "verify_pharmacy_age_gate"
    seed = load_scenario(intent_id).get("scenario") or {}

    agent_id = str(request.get("agentId") or seed.get("agentId"))
    agent = store.agent_by_id.get(agent_id)
    if not agent:
        raise HTTPException(status_code=403, detail="Unknown agent")
    if intent_id not in (agent.get("allowedIntents") or []):
        raise HTTPException(status_code=403, detail="Agent is not authorized for this intent")

    application = store.application_by_id.get(str(agent.get("actsOnBehalfOf") or ""))
    enterprise = store.enterprise_by_id.get(str(agent.get("enterpriseId") or ""))
    if not application or not enterprise:
        raise HTTPException(status_code=403, detail="Agent application/enterprise not resolved")

    intent = store.intent_by_id.get(intent_id) or {}
    uc_id = graph.intent_use_case.get(intent_id)
    use_case = store.use_case_by_id.get(uc_id or "")
    domain = store.domain_by_id.get(str((use_case or {}).get("domainId") or enterprise.get("domainId") or ""))
    policy = next((p for p in store.policies if p.get("id") == seed.get("policyId")), None)
    if not policy:
        raise HTTPException(status_code=500, detail="Scenario policy missing")
    purpose = store.purpose_by_id.get(str(policy.get("purposeId") or intent.get("defaultPurposeId") or ""))
    if not purpose:
        raise HTTPException(status_code=500, detail="Purpose not resolved from configuration")

    corr = seed.get("correlation") or {}
    req_body = {
        "intent": intent_id,
        "subject": (request.get("subject") or seed.get("request", {}).get("subject")),
        "context": (request.get("context") or seed.get("request", {}).get("context")),
    }
    age_threshold = int((req_body.get("context") or {}).get("ageThreshold") or 18)
    network_responses = seed.get("networkResponses") or {}
    network_routes = seed.get("networkRoutes") or {}
    telco = seed.get("telcoFinder") or {}
    provider_label = str((telco.get("result") or {}).get("network") or "Network Provider A")
    mapped = list(graph.intent_caps.get(intent_id) or [])

    plan = Plan(
        id="plan-cc-pharmacy",
        intentId=intent_id,
        executionId=str(corr.get("executionId")),
        version=1,
        label="Minimum capability plan",
        steps=[
            PlanStep(1, "Resolve age threshold from runtime context", None, None),
            PlanStep(2, "Evaluate Age Verification — minimum sufficient capability", "age_verification", "verifyAge", "NETWORK"),
            PlanStep(3, "Evaluate KYC Match — broader than required", "kyc_match", "KYC_Match", "NETWORK"),
            PlanStep(4, "Return narrow eligibility result", None, None),
        ],
    )

    invocations: list[Invocation] = []
    evidence: list[Evidence] = []
    decisions: list[Decision] = []
    policies: list[PolicyEvaluation] = [
        PolicyEvaluation(
            "pol-actor-auth",
            "ACTOR_INTENT",
            "agent",
            "AUTHORIZED",
            "CONFIGURED POLICY",
            f"{agent.get('label')} is an authorized agent for {application.get('label')}.",
        ),
        PolicyEvaluation(
            "pol-actor-intent",
            "ACTOR_INTENT",
            "intent",
            "ALLOWED",
            "CONFIGURED POLICY",
            f"Intent {intent_id} is in the agent's allowedIntents.",
        ),
        PolicyEvaluation(
            "pol-actor-purpose",
            "ACTOR_INTENT",
            "purpose",
            "RESOLVED_FROM_CONFIGURATION",
            "CONFIGURED POLICY",
            f"Purpose {(purpose.get('audienceLabel') or purpose.get('label'))} resolved from configuration.",
        ),
    ]

    candidates: list[dict[str, Any]] = []
    for link in mapped:
        cap_id = str(link["capabilityId"])
        cap = store.capability_by_id.get(cap_id) or {"id": cap_id}
        fam = _family_for(registry, cap_id)
        op_row = _primary_op(graph, cap_id)
        meta = _op_meta(registry, str(op_row["operationId"]), str(op_row["source"])) if op_row else {}
        pol = evaluate_capability_policy(
            store,
            enterprise_id=str(enterprise["id"]),
            policy_id=str(policy["id"]),
            purpose=purpose,
            capability_id=cap_id,
            family=str((fam or {}).get("familyGroup") or cap.get("family")),
        )
        candidates.append(
            {
                "capability": cap,
                "role": link.get("role"),
                "family": fam,
                "operation": op_row,
                "catalog": meta,
                "policy": pol,
                "available": bool(op_row),
            }
        )

    age = next((c for c in candidates if c["capability"]["id"] == "age_verification"), None)
    kyc = next((c for c in candidates if c["capability"]["id"] == "kyc_match"), None)

    if age and age["operation"]:
        pol = age["policy"]
        fam = age["family"] or {}
        op_row = age["operation"]
        op_id = str(op_row["operationId"])
        meta = age["catalog"]
        policies.extend(
            [
                PolicyEvaluation("pol-age-sub", "CAPABILITY_API", "age_verification/subscription", "PERMITTED", "CONFIGURED POLICY", "Subscribed."),
                PolicyEvaluation("pol-age-purpose", "CAPABILITY_API", "age_verification/purpose", "PERMITTED", "CONFIGURED POLICY", "Purpose permits age assertion."),
                PolicyEvaluation("pol-age-agreement", "CAPABILITY_API", "age_verification/agreement", "PERMITTED", "CONFIGURED POLICY", "Agreement permits age assertion for pharmacy eligibility."),
            ]
        )
        decisions.append(
            Decision(
                id="dec-age_verification",
                capabilityId="age_verification",
                familyId=fam.get("id"),
                operationId=op_id,
                label=age["capability"].get("label"),
                relevant=True,
                availability="YES",
                policyResult="PERMITTED",
                state="SELECTED",
                why="Minimum configured capability required for age threshold verification. Sufficient for the outcome.",
                stage="CAPABILITY_API",
            )
        )
        sim = network_responses.get(op_id) or {}
        _append_network_invocation(
            invocations=invocations,
            evidence=evidence,
            route_records=[],
            op_id=op_id,
            inv_id=f"inv-{op_id}",
            meta=meta,
            fam=fam,
            route_cfg=network_routes.get(op_id) or {},
            corr_id=str(corr.get("correlationId")),
            sim=sim,
            op_row=op_row,
            purpose_id=str(purpose["id"]),
        )
        plan.steps[1].state = "INVOKED"

    if kyc:
        pol = kyc["policy"]
        fam = kyc["family"] or {}
        policies.append(
            PolicyEvaluation(
                "pol-kyc-block",
                "CAPABILITY_API",
                "kyc_match",
                pol["result"],
                "CONFIGURED DEMO POLICY",
                pol["detail"],
            )
        )
        decisions.append(
            Decision(
                id="dec-kyc_match",
                capabilityId="kyc_match",
                familyId=fam.get("id"),
                operationId=(kyc["operation"] or {}).get("operationId"),
                label=kyc["capability"].get("label"),
                relevant=True,
                availability="YES" if kyc["available"] else "NO",
                policyResult=pol["result"],
                state="BLOCKED_BY_POLICY",
                why="Potentially related identity capability, but broader than required AND agreement does not permit it for this Intent/Purpose. "
                "Use the minimum configured capability required for the requested outcome.",
                stage="CAPABILITY_API",
            )
        )
        plan.steps[2].state = "BLOCKED_BY_POLICY"

    plan.steps[0].state = "COMPLETED"
    plan.steps[3].state = "COMPLETED"

    out_seed = seed.get("outcome") or {}
    outcome = Outcome(
        outcome=str(out_seed.get("outcome") or "ELIGIBLE"),
        confidence=float(out_seed.get("confidence") or 0.93),
        recommendedAction=str(out_seed.get("recommendedAction") or "PROCEED_WITH_PHARMACIST_REVIEW"),
        decisionOwner=str(out_seed.get("decisionOwner") or "CITYCARE_PHARMACY"),
        reasonCodes=list(out_seed.get("reasonCodes") or ["AGE_ABOVE_THRESHOLD", "MINIMUM_CAPABILITY_SELECTED"]),
        summary=str(out_seed.get("summary") or "Age threshold met using minimum permitted capability."),
        ageThreshold=int(out_seed.get("ageThreshold") or age_threshold),
        ageVerified=bool(out_seed.get("ageVerified", True)),
        dataUsed=str(out_seed.get("dataUsed") or "AGE_ASSERTION_ONLY"),
        broaderKycUsed=bool(out_seed.get("broaderKycUsed", False)),
    )

    autonomy = {
        "gather_age_assertion": "ACT",
        "return_eligibility_result": "ACT",
        "recommend_pharmacist_action": "RECOMMEND",
        "dispense_or_refuse_medication": "NOT_AUTHORIZED",
        "selectedAction": "return_eligibility_result",
        "selectedLevel": "ACT",
        "note": "Agent may return eligibility assertion. Pharmacist/enterprise owns dispensing decision.",
        "source": "CONFIGURED POLICY",
    }
    policies.append(
        PolicyEvaluation(
            "pol-auto-dispense",
            "AUTONOMY_ACTION",
            "dispense_or_refuse_medication",
            "NOT_AUTHORIZED",
            "CONFIGURED POLICY",
            "Agent may not dispense or refuse medication.",
        )
    )

    finder_ops = []
    for cand in candidates:
        op_row = cand["operation"]
        if not op_row:
            continue
        finder_ops.append(
            {
                "capabilityId": cand["capability"]["id"],
                "capability": cand["capability"].get("label"),
                "operationId": op_row["operationId"],
                "family": (cand["family"] or {}).get("label"),
                "available": cand["available"],
                "provider": provider_label,
            }
        )

    beats = [
        Beat(1, 0, "CITYCARE AGENT", "AGENT_AUTHENTICATED", "Agent authenticated", f"{agent.get('label')} acts for {application.get('label')}.", "agent"),
        Beat(2, 400, "NETAWARE AX", "INTENT_RECEIVED", "Intent received", "verify_pharmacy_age_gate — age threshold only.", "netaware"),
        Beat(3, 800, "CONTEXT / POLICY", "PURPOSE_RESOLVED", "Purpose from configuration", str(purpose.get("audienceLabel") or purpose.get("label")), "policy"),
        Beat(4, 1200, "API CATALOG / FINDERS", "API_FINDER", "API Finder", "Age Verification and KYC Match both in catalog.", "finder"),
        Beat(5, 1600, "CONTEXT / POLICY", "CAPABILITY_SELECTION", "Age Verification SELECTED", "Minimum sufficient capability.", "policy"),
        Beat(6, 2000, "CONTEXT / POLICY", "BLOCKED_BY_POLICY", "KYC Match blocked", "Broader KYC not permitted for this purpose.", "policy"),
        Beat(7, 2400, "NETWORK PROVIDER", "INVOKED", "verifyAge", "Age assertion returned — no broad KYC.", "provider"),
        Beat(8, 2800, "CITYCARE AGENT", "OUTCOME", "ELIGIBLE", "Narrow business result. Pharmacist owns dispensing.", "agent"),
    ]

    invoked_ops = {i.operationId for i in invocations}
    if "KYC_Match" in invoked_ops:
        raise HTTPException(status_code=500, detail="KYC_Match was invoked but should be blocked")

    return ExecutionTrace(
        executionId=str(corr.get("executionId")),
        traceId=str(corr.get("traceId")),
        correlationId=str(corr.get("correlationId")),
        intentId=intent_id,
        status="COMPLETED",
        request=req_body,
        knownFromConfiguration={
            "source": "FROM ONBOARDING / CONFIGURATION",
            "rows": [
                {"label": "Enterprise", "value": enterprise.get("label")},
                {"label": "Application", "value": application.get("label")},
                {"label": "Authorized Agent", "value": agent.get("label")},
                {"label": "Domain", "value": (domain or {}).get("label")},
                {"label": "Use case", "value": (use_case or {}).get("label")},
                {"label": "Purpose", "value": purpose.get("audienceLabel") or purpose.get("label")},
                {"label": "Purpose source", "value": "CONFIGURED APPLICATION / INTENT PROFILE"},
                {"label": "Agreement / DPA", "value": "Age assertion permitted; broader KYC Match not permitted"},
                {"label": "Policy", "value": policy.get("label")},
            ],
        },
        purpose={
            "id": purpose.get("id"),
            "label": purpose.get("audienceLabel") or purpose.get("label"),
            "source": "CONFIGURED APPLICATION / INTENT PROFILE",
            "note": "Configured demo governance. Not a universal healthcare/privacy law claim.",
        },
        actor={"agent": agent, "application": application, "enterprise": enterprise, "kind": "AUTHORIZED_AGENT"},
        telcoFinder=telco,
        apiFinder={
            "neededBecause": "API Finder resolves catalog availability. Policy and minimization decide selection.",
            "network": provider_label,
            "results": finder_ops,
            "simulated": True,
        },
        route={
            "type": "DIRECT",
            "display": f"NetAware → {provider_label}",
            "note": "Age Verification only.",
        },
        plan=plan,
        decisions=decisions,
        invocations=invocations,
        evidence=evidence,
        policyEvaluations=policies,
        autonomy=autonomy,
        outcome=outcome,
        economy={
            "catalogFamiliesAvailable": len(registry.families),
            "mappedToIntent": len(mapped),
            "invoked": len(invocations),
            "blockedByPolicy": 1,
            "note": "Catalog availability ≠ permission ≠ need. Minimum capability selected.",
        },
        beats=beats,
        honesty={"simulated": True, "liveOperators": False, "policyIsConfiguredDemo": True, "dataMinimization": True},
    )


_INTENT_RUNNERS: dict[str, Callable[..., ExecutionTrace]] = {
    "assess_network_trust": run_assess_network_trust,
    "assess_recovery_continuity": run_assess_recovery_continuity,
    "ensure_baggage_connection": run_ensure_baggage_connection,
    "maintain_inspection_experience": run_maintain_inspection_experience,
    "verify_pharmacy_age_gate": run_verify_pharmacy_age_gate,
    "verify_mobile_number": run_verify_mobile_number,
    "prepare_ota_cohort": run_prepare_ota_cohort,
}


_LAST: dict[str, Any] = {}


def execute_intent(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry, body: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(body, dict) or not body.get("intent"):
        raise HTTPException(status_code=400, detail="intent is required")
    intent_id = str(body.get("intent"))
    runner = _INTENT_RUNNERS.get(intent_id)
    if not runner:
        from .guided_runtime import GUIDED_INTENTS, run_guided_intent

        if intent_id in GUIDED_INTENTS:
            runner = run_guided_intent
    if not runner:
        raise HTTPException(status_code=409, detail=f"Intent not executable: {intent_id}")
    trace = runner(store, graph, registry, body)
    from .discovery_trace import attach_discovery

    from .intent_profile import attach_intent_profile

    payload = attach_discovery(enrich_trace_presentation(trace.to_public(), registry), store, graph, registry)
    payload = attach_intent_profile(payload, store)
    _LAST[payload["executionId"]] = payload
    _LAST["latest"] = payload
    return payload


def get_execution(execution_id: str) -> dict[str, Any]:
    if execution_id == "latest":
        payload = _LAST.get("latest")
    else:
        payload = _LAST.get(execution_id)
    if not payload:
        raise HTTPException(status_code=404, detail="No execution yet")
    return payload


def reset_executions() -> dict[str, Any]:
    _LAST.clear()
    reset_store()
    return {"ok": True, "executions": 0, "evidenceStore": 0}
