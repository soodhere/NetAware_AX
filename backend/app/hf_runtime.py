"""Cadence 10 — High Flight ramp-scanner operability.

One Intent (`ensure_baggage_connection`). Two presenter-simulated operational states.
Bag HF123456 remains domain context. Network subject is scanner HF-HDL-0192.
"""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from .graph import KnowledgeGraph
from .model import ConfigStore
from .registry import CatalogRegistry
from .runtime_models import (
    Beat,
    Decision,
    Evidence,
    ExecutionTrace,
    Outcome,
    Plan,
    PlanStep,
    PolicyEvaluation,
)

HF_VARIANTS = ("scanner-ready", "scanner-unreachable")


def resolve_hf_variant(request: dict[str, Any], seed: dict[str, Any]) -> str:
    ctx = request.get("context") or {}
    raw = str(ctx.get("hfVariant") or ctx.get("operationalScenario") or "").strip()
    if raw in HF_VARIANTS:
        return raw
    if str(ctx.get("scannerReachable") or "").lower() in {"false", "no", "0"}:
        return "scanner-unreachable"
    return str(seed.get("defaultVariant") or "scanner-ready")


def run_ensure_baggage_connection(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    request: dict[str, Any],
) -> ExecutionTrace:
    from .runtime import (
        _domain_invocation,
        _family_for,
        _network_invocation,
        _op_meta,
        _primary_op,
        evaluate_capability_policy,
        load_scenario,
    )

    intent_id = "ensure_baggage_connection"
    seed = load_scenario(intent_id).get("scenario") or {}
    variant_id = resolve_hf_variant(request, seed)
    variant = (seed.get("variants") or {}).get(variant_id) or (seed.get("variants") or {}).get("scanner-ready") or {}

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
        "context": {
            **(seed.get("request", {}).get("context") or {}),
            **(request.get("context") or {}),
            "hfVariant": variant_id,
        },
    }
    # Presenter simulation is not an application-chosen Intent field.
    network_subject = seed.get("networkSubject") or {}
    domain_responses = seed.get("domainResponses") or {}
    network_routes = seed.get("networkRoutes") or {}
    telco = seed.get("telcoFinder") or {}
    provider_label = str((telco.get("result") or {}).get("network") or "Network Provider A")
    reachable = bool(variant.get("reachable", True))
    network_responses = variant.get("networkResponses") or {}

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
        route_cfg = network_routes.get(str((op_row or {}).get("operationId"))) or {}
        advertised = cap_id in {
            "device_reachability",
            "connectivity_insights",
            "location_verification",
            "quality_on_demand",
            "roaming_status",
        }
        candidates.append(
            {
                "capability": cap,
                "role": link.get("role"),
                "family": fam,
                "operation": op_row,
                "catalog": meta,
                "policy": pol,
                "available": advertised or bool(op_row and route_cfg),
                "route": route_cfg,
            }
        )

    exec_id = str(corr.get("executionId"))
    plan_v1 = Plan(
        id="plan-hf-ramp-v1",
        intentId=intent_id,
        executionId=exec_id,
        version=1,
        label="PLAN v1",
        steps=[
            PlanStep(1, "Read BRS custody requirement for bag HF123456", None, "getBaggageJourney", "DOMAIN"),
            PlanStep(2, "Read DCS flight / load-close for HF281", None, "getFlightStatus", "DOMAIN"),
            PlanStep(3, "Read Ground Operations assignment (scanner HF-HDL-0192)", None, "getRampAssignment", "ENTERPRISE"),
            PlanStep(4, "Map bag / worker → assigned scanner → network identifier", None, None),
            PlanStep(5, "Check DATA reachability of assigned scanner", "device_reachability", "getReachabilityStatus", "NETWORK"),
            PlanStep(6, "Location Verification — not required (not bag tracking)", "location_verification", "verifyLocation", "NETWORK", "NOT_REQUIRED"),
            PlanStep(7, "QoD — not required by default", "quality_on_demand", "createSession", "NETWORK", "NOT_REQUIRED"),
            PlanStep(8, "Connectivity — skip unless it changes CONTINUE vs SWAP", "connectivity_insights", "checkNetworkQuality", "NETWORK", "NOT_REQUIRED"),
            PlanStep(9, "Return operational recommendation", None, None),
        ],
    )
    plan_v2 = None
    if not reachable:
        plan_v2 = Plan(
            id="plan-hf-ramp-v2",
            intentId=intent_id,
            executionId=exec_id,
            version=2,
            label="PLAN v2",
            supersedes=plan_v1.id,
            note="Assigned scanner cannot complete the connected custody operation. Select an alternate device from enterprise inventory.",
            steps=[
                PlanStep(1, "BRS custody requirement", None, "getBaggageJourney", "DOMAIN", "INVOKED"),
                PlanStep(2, "DCS load-close window", None, "getFlightStatus", "DOMAIN", "INVOKED"),
                PlanStep(3, "Ramp assignment", None, "getRampAssignment", "ENTERPRISE", "INVOKED"),
                PlanStep(4, "Reachability of HF-HDL-0192", "device_reachability", "getReachabilityStatus", "NETWORK", "INVOKED"),
                PlanStep(
                    5,
                    "Assign alternate scanner from enterprise handheld inventory",
                    None,
                    "assignAlternateScanner",
                    "ENTERPRISE",
                    "PLANNED",
                    "added",
                ),
                PlanStep(6, "Location / QoD remain NOT_REQUIRED", "location_verification", "verifyLocation", "NETWORK", "NOT_REQUIRED"),
                PlanStep(7, "Recommend SWAP_DEVICE — airline still owns physical bag handling", None, None),
            ],
        )

    invocations = []
    evidence = []
    decisions = []
    policies = [
        PolicyEvaluation(
            "pol-actor-auth",
            "ACTOR_INTENT",
            "agent",
            "AUTHORIZED",
            "CONFIGURED POLICY",
            f"{agent.get('label')} is an authorized agent for {application.get('label')}.",
            layer="AGENT DELEGATION",
        ),
        PolicyEvaluation(
            "pol-actor-intent",
            "ACTOR_INTENT",
            "intent",
            "ALLOWED",
            "CONFIGURED POLICY",
            f"Intent {intent_id} is in the agent's allowedIntents.",
            layer="INTENT",
        ),
        PolicyEvaluation(
            "pol-actor-purpose",
            "ACTOR_INTENT",
            "purpose",
            "RESOLVED_FROM_CONFIGURATION",
            "CONFIGURED POLICY",
            f"Purpose {(purpose.get('audienceLabel') or purpose.get('label'))} resolved from application/intent profile. Not inferred from runtime text.",
            layer="PURPOSE / DATA",
        ),
    ]

    owner = str(enterprise.get("label") or "High Flight Airlines")
    domain_ops = [
        ("getBaggageJourney", "BRS", "DOMAIN"),
        ("getFlightStatus", "DCS", "DOMAIN"),
        ("getRampAssignment", "Ground Operations", "ENTERPRISE"),
    ]

    for op_id, label, api_kind in domain_ops:
        sim = domain_responses.get(op_id) or {}
        inv = _domain_invocation(
            op_id=op_id,
            api_kind=api_kind,
            owner=owner,
            label=label,
            corr_id=str(corr.get("correlationId")),
            sim=sim,
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
                apiKind=api_kind,
            )
        )
        decisions.append(
            Decision(
                id=f"dec-{op_id}",
                capabilityId=None,
                familyId=None,
                operationId=op_id,
                label=label,
                relevant=True,
                availability="YES",
                policyResult="PERMITTED",
                state="INVOKED",
                why=f"{label} is an existing airline system. Complements network evidence. Does not get replaced by NetAware.",
                stage="EXECUTION",
            )
        )
        for step in plan_v1.steps:
            if step.operationId == op_id:
                step.state = "INVOKED"

    loc = next((c for c in candidates if c["capability"]["id"] == "location_verification"), None)
    if loc:
        fam = loc["family"] or {}
        policies.append(
            PolicyEvaluation(
                "pol-cap-location_verification",
                "CAPABILITY_API",
                "location_verification",
                "NOT_REQUIRED",
                "CONFIGURED POLICY",
                "Location is not the Decision Gap. BRS already has bag/flight/custody events. Network Location is not bag tracking.",
                layer="INTENT",
            )
        )
        decisions.append(
            Decision(
                id="dec-location_verification",
                capabilityId="location_verification",
                familyId=fam.get("id"),
                operationId=(loc["operation"] or {}).get("operationId"),
                label=loc["capability"].get("label"),
                relevant=False,
                availability="YES" if loc["available"] else "NO",
                policyResult="PERMITTED",
                state="NOT_REQUIRED",
                why="NOT_REQUIRED for this Intent. Enterprise already knows bag, flight and custody events. Network Location must not be used as bag tracking.",
                stage="PLAN",
                reasonCode="NOT_REQUIRED",
            )
        )

    qod = next((c for c in candidates if c["capability"]["id"] == "quality_on_demand"), None)
    if qod:
        fam = qod["family"] or {}
        policies.append(
            PolicyEvaluation(
                "pol-cap-quality_on_demand",
                "CAPABILITY_API",
                "quality_on_demand",
                "NOT_REQUIRED",
                "CONFIGURED POLICY",
                "QoD does not close the ramp-scan Decision Gap by default.",
                layer="INTENT",
            )
        )
        decisions.append(
            Decision(
                id="dec-quality_on_demand",
                capabilityId="quality_on_demand",
                familyId=fam.get("id"),
                operationId=(qod["operation"] or {}).get("operationId"),
                label=qod["capability"].get("label"),
                relevant=False,
                availability="YES" if qod["available"] else "NO",
                policyResult="PERMITTED",
                state="NOT_REQUIRED",
                why="NOT_REQUIRED by default. The question is whether the assigned handheld is DATA reachable, not whether to boost session quality.",
                stage="PLAN",
                reasonCode="NOT_REQUIRED",
            )
        )

    conn = next((c for c in candidates if c["capability"]["id"] == "connectivity_insights"), None)
    if conn:
        fam = conn["family"] or {}
        decisions.append(
            Decision(
                id="dec-connectivity_insights",
                capabilityId="connectivity_insights",
                familyId=fam.get("id"),
                operationId=(conn["operation"] or {}).get("operationId"),
                label=conn["capability"].get("label"),
                relevant=True,
                availability="YES" if conn["available"] else "NO",
                policyResult="PERMITTED",
                state="NOT_REQUIRED",
                why="Considered, but DATA reachability already decides CONTINUE vs SWAP. Connectivity would not change the operational action.",
                stage="PLAN",
                reasonCode="NOT_REQUIRED",
            )
        )

    roam = next((c for c in candidates if c["capability"]["id"] == "roaming_status"), None)
    if roam:
        fam = roam["family"] or {}
        decisions.append(
            Decision(
                id="dec-roaming_status",
                capabilityId="roaming_status",
                familyId=fam.get("id"),
                operationId=(roam["operation"] or {}).get("operationId"),
                label=roam["capability"].get("label"),
                relevant=True,
                availability="YES" if roam["available"] else "NO",
                policyResult="PERMITTED",
                state="NOT_REQUIRED",
                why="Roaming is only useful if it would explain unreachability or change SWAP vs HOLD. It does not in this configured seed.",
                stage="PLAN",
                reasonCode="NOT_REQUIRED",
            )
        )

    reach = next((c for c in candidates if c["capability"]["id"] == "device_reachability"), None)
    route_records: list[dict[str, Any]] = []
    if reach:
        pol = reach["policy"]
        op_row = reach["operation"]
        meta = reach["catalog"]
        fam = reach["family"] or {}
        op_id = str(op_row["operationId"])
        route_cfg = reach["route"] or network_routes.get(op_id) or {}
        policies.append(
            PolicyEvaluation(
                "pol-cap-device_reachability",
                "CAPABILITY_API",
                "device_reachability",
                pol["result"],
                "CONFIGURED POLICY",
                pol["detail"],
                layer="COMMERCIAL",
            )
        )
        sim = network_responses.get(op_id) or {}
        inv = _network_invocation(
            op_id=op_id,
            meta=meta,
            fam=fam,
            route=route_cfg,
            corr_id=str(corr.get("correlationId")),
            sim=sim,
            op_row=op_row,
        )
        invocations.append(inv)
        route_records.append(
            {
                "operationId": op_id,
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
                id=f"ev-{op_id}",
                operationId=op_id,
                type=str(ev.get("type") or "DEVICE_REACHABILITY"),
                status=str(ev.get("status") or "observed"),
                payload={k: v for k, v in ev.items() if k not in {"type"}},
                purposeId=str(purpose["id"]),
                apiKind="NETWORK",
            )
        )
        decisions.append(
            Decision(
                id="dec-device_reachability",
                capabilityId="device_reachability",
                familyId=fam.get("id"),
                operationId=op_id,
                label=reach["capability"].get("label"),
                relevant=True,
                availability="YES",
                policyResult="PERMITTED",
                state="INVOKED",
                why="Closes the Network Decision Gap: can assigned scanner HF-HDL-0192 participate in the operator data network right now? Does not locate the bag.",
                stage="EXECUTION",
                reasonCode="SELECTED",
            )
        )
        for step in plan_v1.steps:
            if step.operationId == op_id:
                step.state = "INVOKED"

    replan = None
    if not reachable:
        sim = domain_responses.get("assignAlternateScanner") or {}
        inv = _domain_invocation(
            op_id="assignAlternateScanner",
            api_kind="ENTERPRISE",
            owner=owner,
            label="Handheld inventory",
            corr_id=str(corr.get("correlationId")),
            sim=sim,
        )
        invocations.append(inv)
        ev = sim.get("evidence") or {}
        evidence.append(
            Evidence(
                id="ev-assignAlternateScanner",
                operationId="assignAlternateScanner",
                type=str(ev.get("type") or "DEVICE_SWAP"),
                status=str(ev.get("status") or "assigned_alternate"),
                payload={k: v for k, v in ev.items() if k not in {"type"}},
                purposeId=str(purpose["id"]),
                apiKind="ENTERPRISE",
            )
        )
        decisions.append(
            Decision(
                id="dec-assignAlternateScanner",
                capabilityId=None,
                familyId=None,
                operationId="assignAlternateScanner",
                label="Handheld inventory",
                relevant=True,
                availability="YES",
                policyResult="PERMITTED",
                state="INVOKED",
                why="DOMAIN / ENTERPRISE action. Alternate scanner HF-HDL-0208 comes from airline inventory. Not a Network API. Network does not move baggage.",
                stage="EXECUTION",
            )
        )
        if plan_v2:
            for step in plan_v2.steps:
                if step.operationId == "assignAlternateScanner":
                    step.state = "INVOKED"
                if step.operationId == "getReachabilityStatus":
                    step.state = "INVOKED"
        replan = {
            "trigger": "ASSIGNED_SCANNER_NOT_DATA_REACHABLE",
            "constraint": "Required connected custody scan cannot complete on HF-HDL-0192",
            "whatChanged": [
                "Reachability evidence changed the operational action",
                "Added enterprise handheld-inventory assignment",
                "Location and QoD remain NOT_REQUIRED",
            ],
            "narrative": "Assigned scanner cannot participate. Swap device from enterprise inventory. Airline still owns physical bag handling.",
            "planV1": plan_v1.id,
            "planV2": plan_v2.id if plan_v2 else None,
        }

    out_seed = variant.get("outcome") or {}
    outcome = Outcome(
        outcome=str(out_seed.get("outcome") or ("CONTINUE" if reachable else "SWAP_DEVICE")),
        confidence=float(out_seed.get("confidence") or 0.9),
        recommendedAction=str(out_seed.get("recommendedAction") or ("CONTINUE" if reachable else "SWAP_DEVICE")),
        decisionOwner=str(out_seed.get("decisionOwner") or "HIGH_FLIGHT_OPERATIONS"),
        reasonCodes=list(out_seed.get("reasonCodes") or []),
        summary=str(out_seed.get("summary") or ""),
        approvalRequired=bool(out_seed.get("approvalRequired", False)),
        limitingFactor=str(out_seed.get("limitingFactor") or ""),
        networkConstraint=bool(out_seed.get("networkConstraint", False)),
    )

    autonomy = {
        "observe_and_assess": "ACT",
        "recommend_continue": "RECOMMEND" if reachable else "NOT_SELECTED",
        "recommend_swap_device": "ACT" if not reachable else "NOT_SELECTED",
        "change_flight_plan": "NOT_AUTHORIZED",
        "move_baggage": "NOT_AUTHORIZED",
        "selectedAction": "recommend_continue" if reachable else "recommend_swap_device",
        "selectedLevel": "RECOMMEND" if reachable else "ACT",
        "approvalRequired": False,
        "note": "NetAware may observe reachability and recommend CONTINUE or SWAP_DEVICE. It may not change the flight plan or physically move baggage.",
        "source": "CONFIGURED POLICY",
    }
    policies.append(
        PolicyEvaluation(
            "pol-auto-observe",
            "AUTONOMY_ACTION",
            "observe_and_assess",
            "ACT",
            "CONFIGURED POLICY",
            "Observing BRS/DCS/assignment and network reachability is allowed.",
            layer="AUTONOMY",
        )
    )
    policies.append(
        PolicyEvaluation(
            "pol-auto-swap",
            "AUTONOMY_ACTION",
            "recommend_swap_device / SWAP_DEVICE",
            "ACT" if not reachable else "NOT_SELECTED",
            "CONFIGURED POLICY",
            "Swap device is an enterprise inventory action after network evidence. Not a Network API.",
            layer="AUTONOMY",
        )
    )
    policies.append(
        PolicyEvaluation(
            "pol-auto-flight",
            "AUTONOMY_ACTION",
            "change_flight_plan",
            "NOT_AUTHORIZED",
            "CONFIGURED POLICY",
            "Agent is not authorized to change the flight plan or physically move baggage.",
            layer="AUTONOMY",
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

    api_finder = {
        "neededBecause": "Network subject resolved to assigned scanner HF-HDL-0192. API Finder lists Network APIs on that operator. Policy and need decide what is invoked.",
        "network": provider_label,
        "networkSubject": network_subject,
        "results": finder_ops,
        "simulated": True,
        "note": "Availability is simulated/configured. Location remaining listed does not mean it should be used to track the bag.",
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
            {"label": "Purpose source", "value": "CONFIGURED APPLICATION / INTENT PROFILE"},
            {"label": "BRS / DCS / Ground Operations", "value": "Existing airline systems"},
            {"label": "Network subject", "value": f"Scanner {network_subject.get('scannerId')} → {network_subject.get('networkIdentifier')}"},
            {"label": "Bag (domain context)", "value": network_subject.get("bagId")},
            {"label": "Subscriptions", "value": "Configured"},
            {"label": "Entitlements", "value": "Configured"},
            {"label": "Policy", "value": policy.get("label")},
            {"label": "Region", "value": "CA"},
            {"label": "Autonomy rules", "value": "Configured"},
        ],
    }

    hf_visual = {
        "businessEvent": "BAG HF123456 NEEDS CUSTODY/LOAD SCAN BEFORE LOAD-CLOSE",
        "headline": (
            "Assigned scanner can complete the connected custody operation."
            if reachable
            else "Assigned scanner cannot participate — swap a device from airline inventory."
        ),
        "baggageWorld": [
            {"id": "bag", "label": "Bag HF123456", "detail": "Domain context — not the network subject", "state": "ok"},
            {"id": "brs", "label": "BRS", "detail": "Required CUSTODY_LOAD_SCAN", "state": "ok"},
            {"id": "dcs", "label": "DCS · Flight HF281", "detail": "Load-close in 28 minutes", "state": "ok"},
            {"id": "ramp", "label": "Ramp assignment", "detail": "Worker HF-RAMP-441", "state": "ok"},
            {"id": "scanner", "label": "Scanner HF-HDL-0192", "detail": "Network subject", "state": "ok" if reachable else "break"},
        ],
        "gap": "Can this scanner complete the connected custody operation?",
        "networkAdds": "Device Reachability",
        "ax": "Discover · govern · select Reachability · skip Location/QoD",
        "outcome": outcome.outcome,
        "variantId": variant_id,
        "presenterControl": "SIMULATE OPERATIONAL CONTEXT",
        "applicationDoesNotChooseVariant": True,
    }

    demand_fulfilled = True
    demand_class = "FULFILLED_QUALIFIED_DEMAND"
    demand_note = (
        "Reachability API succeeded and reported DATA reachable."
        if reachable
        else "Reachability API succeeded and reported the device unreachable. That is fulfilled demand, not an unfulfilled Network API."
    )
    network_opportunity = {
        "businessDemand": "Assure assigned ramp scanner can complete connected baggage custody scan",
        "businessDemandQualified": True,
        "qualified": True,
        "fulfilled": demand_fulfilled,
        "demandFulfilled": demand_fulfilled,
        "demandClass": demand_class,
        "capability": "device_reachability",
        "provider": provider_label,
        "route": "DIRECT",
        "blockingReadinessGap": None,
        "networkApiInvocations": ["getReachabilityStatus"],
        "apiSuccessfullyReportedUnreachable": (not reachable),
        "note": demand_note,
    }

    beats = [
        Beat(1, 0, "HIGH FLIGHT AGENT", "AGENT_AUTHENTICATED", "Business event received", "Bag HF123456 needs custody/load scan before load-close.", "agent"),
        Beat(2, 400, "NETAWARE AX", "INTENT_RECEIVED", "Intent resolved", "Assure the assigned connected scanner can complete the required digital operation.", "netaware"),
        Beat(3, 800, "CONTEXT / POLICY", "CONTEXT_RESOLVED", "Context resolved", "Enterprise, application, purpose and policy from onboarding.", "policy"),
        Beat(4, 1200, "DOMAIN APIs", "INVOKED", "getBaggageJourney", "BRS — required CUSTODY_LOAD_SCAN for HF123456.", "domain"),
        Beat(5, 1600, "DOMAIN APIs", "INVOKED", "getFlightStatus", "DCS — HF281 load-close in 28 minutes.", "domain"),
        Beat(6, 2000, "ENTERPRISE GROUND OPERATIONS", "INVOKED", "getRampAssignment", "Assigned scanner HF-HDL-0192 / worker HF-RAMP-441.", "enterprise"),
        Beat(7, 2400, "NETAWARE AX", "CONTEXT_RESOLVED", "Network subject mapped", "Bag / worker → scanner HF-HDL-0192 → network identifier. Bag stays domain context.", "netaware"),
        Beat(8, 2800, "TELCO FINDER", "TELCO_FINDER", "Telco Finder", telco.get("neededBecause", ""), "finder"),
        Beat(9, 3100, "API FINDER", "API_FINDER", "API Finder", f"Network APIs available on {provider_label}.", "finder"),
        Beat(10, 3400, "NETAWARE AX", "NOT_REQUIRED", "Location and QoD skipped", "They do not close this Decision Gap. Location is not bag tracking.", "netaware"),
        Beat(
            11,
            3800,
            "NETWORK PROVIDER",
            "INVOKED",
            "getReachabilityStatus",
            "HF-HDL-0192 DATA reachable (DIRECT)." if reachable else "HF-HDL-0192 not DATA reachable — API success (DIRECT).",
            "provider",
        ),
    ]
    n = 12
    t = 4200
    if not reachable:
        beats.append(Beat(n, t, "NETAWARE AX", "REPLAN", "Operational decision changed", replan["narrative"] if replan else "", "netaware"))
        n += 1
        t += 400
        beats.append(Beat(n, t, "ENTERPRISE GROUND OPERATIONS", "INVOKED", "assignAlternateScanner", "Enterprise inventory assigns HF-HDL-0208. Not a Network API.", "enterprise"))
        n += 1
        t += 400
    beats.append(Beat(n, t, "CONTEXT / POLICY", "AUTONOMY", "Autonomy check", autonomy["note"], "policy"))
    n += 1
    t += 400
    beats.append(
        Beat(
            n,
            t,
            "HIGH FLIGHT AGENT",
            "OUTCOME",
            "Business outcome returned",
            f"{outcome.outcome}. Airline owns physical baggage handling.",
            "agent",
        )
    )

    invoked_ops = {i.operationId for i in invocations}
    if "verifyLocation" in invoked_ops or "createSession" in invoked_ops:
        raise HTTPException(status_code=500, detail="Location or QoD invoked for ramp-scan Intent")
    if any(e.type in {"NETWORK_LOCATION", "LOCATION_VERIFICATION"} for e in evidence):
        raise HTTPException(status_code=500, detail="synthetic location evidence generated")

    active_plan = plan_v2 or plan_v1
    for step in active_plan.steps:
        if step.operationId in invoked_ops and step.state not in {"NOT_REQUIRED", "BLOCKED_BY_POLICY"}:
            step.state = "INVOKED"
        elif step.capabilityId in {"location_verification", "quality_on_demand", "connectivity_insights"}:
            step.state = "NOT_REQUIRED"
        elif step.operationId is None and step.n >= 8:
            step.state = "COMPLETED"

    return ExecutionTrace(
        executionId=exec_id,
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
            "note": "Purpose comes from configuration. Not inferred from arbitrary runtime text.",
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
            "type": "DIRECT",
            "from": "NetAware",
            "display": "DIRECT — Reachability to Network Provider A",
            "note": "Connectivity/Location routes exist in configuration but are not invoked for this Decision Gap.",
        },
        routes=route_records,
        plan=active_plan,
        planHistory=[plan_v1, plan_v2] if plan_v2 else [plan_v1],
        replan=replan,
        decisions=decisions,
        invocations=invocations,
        evidence=evidence,
        policyEvaluations=policies,
        autonomy=autonomy,
        outcome=outcome,
        economy={
            "catalogFamiliesAvailable": len(registry.families),
            "mappedToIntent": len(mapped),
            "domainInvoked": sum(1 for i in invocations if i.apiKind in {"DOMAIN", "ENTERPRISE"}),
            "networkInvoked": sum(1 for i in invocations if i.apiKind == "NETWORK"),
            "invoked": len(invocations),
            "consideredNotRequired": 3,
            "blockedByPolicy": 0,
            "note": "BRS/DCS/Ground Ops remain airline systems. Network adds DATA reachability of the assigned scanner.",
        },
        beats=beats,
        honesty={
            "simulated": True,
            "liveOperators": False,
            "policyIsConfiguredDemo": True,
            "noSyntheticLocation": True,
            "domainApisAreSimulated": True,
            "networkDoesNotMoveBags": True,
        },
        networkOpportunity=network_opportunity,
        demandSupply={
            "businessDemandQualified": True,
            "demandFulfilled": True,
            "provider": provider_label,
            "route": "DIRECT",
            "capability": "device_reachability",
            "path": None,
            "blockingReadinessGap": None,
            "networkApiInvocations": ["getReachabilityStatus"],
            "apiSuccessfullyReportedUnreachable": (not reachable),
            "demandClass": demand_class,
            "note": demand_note,
        },
        hfVisual=hf_visual,
    )
