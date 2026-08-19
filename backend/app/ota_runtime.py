"""Cadence 11 — Acme Connected Device Operations / network-aware OTA cohort.

One Intent (`prepare_ota_cohort`). Two presenter waves: prepare, then reassess.
NetAware does not install firmware. Fleet counts are SIMULATED.
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

OTA_VARIANTS = ("prepare", "reassess")
NOT_REQUIRED_CAPS = ("connectivity_insights", "quality_on_demand", "location_verification")


def resolve_ota_variant(request: dict[str, Any], seed: dict[str, Any]) -> str:
    ctx = request.get("context") or {}
    raw = str(ctx.get("otaWave") or ctx.get("otaVariant") or "").strip()
    if raw in OTA_VARIANTS:
        return raw
    return str(seed.get("defaultVariant") or "prepare")


def _n(d: dict[str, Any], key: str, default: int = 0) -> int:
    return int(d.get(key) if d.get(key) is not None else default)


def run_prepare_ota_cohort(
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

    intent_id = "prepare_ota_cohort"
    seed = load_scenario(intent_id).get("scenario") or {}
    variant_id = resolve_ota_variant(request, seed)
    reassess = variant_id == "reassess"

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
    fleet = seed.get("fleet") or {}
    fleet_r = fleet.get("reassess") or {}
    providers = list(seed.get("providers") or [])
    volume = seed.get("volume") or {}
    vol_wave = (volume.get("reassess") if reassess else volume.get("prepare")) or {}
    domain_responses = seed.get("domainResponses") or {}
    network_routes = seed.get("networkRoutes") or {}
    samples = list(seed.get("samples") or [])

    roll_out = _n(fleet_r if reassess else fleet, "rollOutNow", _n(fleet, "rollOutNow"))
    defer = _n(fleet_r if reassess else fleet, "defer", _n(fleet, "defer"))
    unreachable = _n(fleet_r if reassess else fleet, "deferUnreachable", _n(fleet, "deferUnreachable"))
    roaming_defer = _n(fleet_r if reassess else fleet, "deferRoamingPolicy", _n(fleet, "deferRoamingPolicy"))
    api_gap = _n(fleet_r if reassess else fleet, "unfulfilledRoamingApi", _n(fleet, "unfulfilledRoamingApi"))
    eligible = _n(fleet, "enterpriseEligible")
    campaign_n = _n(fleet, "campaignTarget")
    reused = _n(fleet, "evidenceReused")
    eval_n = _n(fleet, "networkEvaluationRequired")

    if eligible != roll_out + defer:
        raise HTTPException(status_code=500, detail="OTA fleet roll-out + defer must equal enterprise-eligible")
    if defer != unreachable + roaming_defer + api_gap:
        raise HTTPException(status_code=500, detail="OTA deferred reasons must sum to defer total")
    if campaign_n != eligible + _n(fleet, "enterpriseNotEligible"):
        raise HTTPException(status_code=500, detail="OTA campaign target must equal eligible + not eligible")

    req_body = {
        "intent": intent_id,
        "subject": (request.get("subject") or seed.get("request", {}).get("subject")),
        "context": {
            **(seed.get("request", {}).get("context") or {}),
            **(request.get("context") or {}),
            "otaWave": variant_id,
            "simulatedFleet": True,
        },
    }

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
        candidates.append(
            {
                "capability": cap,
                "role": link.get("role"),
                "family": fam,
                "operation": op_row,
                "catalog": meta,
                "policy": pol,
            }
        )

    exec_id = str(corr.get("executionId")) + ("-reassess" if reassess else "-prepare")
    plan_v1 = Plan(
        id="plan-ota-v1",
        intentId=intent_id,
        executionId=exec_id,
        version=1,
        label="PLAN v1 — PREPARE",
        steps=[
            PlanStep(1, "Load OTA campaign context from enterprise system", None, "listDevices", "ENTERPRISE"),
            PlanStep(2, "Determine enterprise-eligible devices (firmware / model / health)", None, "getTwin", "ENTERPRISE"),
            PlanStep(3, "Resolve network subjects / providers (Telco Finder)", None, None),
            PlanStep(4, "Discover relevant Network APIs (API Finder)", None, None),
            PlanStep(5, "Evaluate policy / subscription / entitlement", None, None),
            PlanStep(6, "Check network readiness (Reachability / Roaming)", "device_reachability", "getReachabilityStatus", "NETWORK"),
            PlanStep(7, "Segment devices under configured OTA policy", None, None),
            PlanStep(8, "Produce initial rollout cohort", None, None),
            PlanStep(9, "Return / optionally approve enterprise rollout", None, "addDevicesToCampaign", "ENTERPRISE"),
        ],
    )
    plan_v2 = None
    if reassess:
        plan_v2 = Plan(
            id="plan-ota-v2",
            intentId=intent_id,
            executionId=exec_id,
            version=2,
            label="PLAN v2 — REASSESS",
            supersedes=plan_v1.id,
            note="Some previously deferred devices are now reachable / no longer roaming. Expand the network-qualified cohort. Firmware is still not installed by NetAware.",
            steps=[
                PlanStep(1, "Observe deferred cohort", None, "listDevices", "ENTERPRISE", "INVOKED"),
                PlanStep(2, "Recheck previously unreachable / roaming devices", "device_reachability", "getReachabilityStatus", "NETWORK", "PLANNED"),
                PlanStep(3, "Re-interpret roaming through configured policy", "roaming_status", "getRoamingStatus", "NETWORK", "PLANNED"),
                PlanStep(4, "Expand ROLL OUT NOW cohort", None, None, None, "PLANNED"),
                PlanStep(5, "Submit expanded cohort to enterprise OTA (simulated)", None, "addDevicesToCampaign", "ENTERPRISE", "PLANNED"),
                PlanStep(6, "Firmware install remains outside NetAware", None, "installFirmware", "ENTERPRISE", "NOT_AUTHORIZED"),
            ],
        )

    invocations = []
    evidence = []
    decisions = []
    policies = [
        PolicyEvaluation("pol-actor-auth", "ACTOR_INTENT", "agent", "AUTHORIZED", "CONFIGURED POLICY", f"{agent.get('label')} is an authorized agent for {application.get('label')}.", layer="AGENT DELEGATION"),
        PolicyEvaluation("pol-actor-intent", "ACTOR_INTENT", "intent", "ALLOWED", "CONFIGURED POLICY", f"Intent {intent_id} is in the agent's allowedIntents.", layer="INTENT"),
        PolicyEvaluation("pol-actor-purpose", "ACTOR_INTENT", "purpose", "RESOLVED_FROM_CONFIGURATION", "CONFIGURED POLICY", f"Purpose {(purpose.get('audienceLabel') or purpose.get('label'))} resolved from application/intent profile. Not inferred from runtime text.", layer="PURPOSE / DATA"),
        PolicyEvaluation("pol-region", "CAPABILITY_API", "region", "PERMITTED", "CONFIGURED POLICY", "Canada / Germany / Singapore are configured enterprise regions for this campaign. Not a live regulatory claim.", layer="REGION"),
        PolicyEvaluation("pol-roaming-interpret", "CAPABILITY_API", "roaming_status", "PERMITTED", "CONFIGURED POLICY", "Network returns roaming state. Configured enterprise OTA policy defers roaming devices on this campaign. Roaming is not automatically bad.", layer="RUNTIME"),
    ]

    owner = str(enterprise.get("label") or "Acme Manufacturing")
    for op_id, label, api_kind in [
        ("listDevices", "Device Management / OTA Platform", "ENTERPRISE"),
        ("getTwin", "Device Twin", "ENTERPRISE"),
        ("getPackage", "Firmware Campaign", "ENTERPRISE"),
    ]:
        sim = domain_responses.get(op_id) or {}
        invocations.append(_domain_invocation(op_id=op_id, api_kind=api_kind, owner=owner, label=label, corr_id=str(corr.get("correlationId")), sim=sim))
        ev = sim.get("evidence") or {}
        evidence.append(Evidence(id=f"ev-{op_id}", operationId=op_id, type=str(ev.get("type") or op_id), status=str(ev.get("status") or "observed"), payload={k: v for k, v in ev.items() if k not in {"type"}}, purposeId=str(purpose["id"]), apiKind=api_kind))
        decisions.append(Decision(id=f"dec-{op_id}", capabilityId=None, familyId=None, operationId=op_id, label=label, relevant=True, availability="YES", policyResult="PERMITTED", state="INVOKED", why=f"{label} is an existing enterprise system. Complements network evidence. NetAware does not replace it.", stage="EXECUTION"))

    skip_why = {
        "connectivity_insights": "Connectivity Insights is experimental and would not change which devices enter the OTA cohort now. Not invoked. NOT AVAILABLE as a required signal for this Decision Gap.",
        "quality_on_demand": "QoD does not determine whether a device is network-suitable to enter the OTA cohort now. Not forced into OTA.",
        "location_verification": "Network Location is not required to qualify the OTA cohort. Not used as device tracking.",
    }
    for cap_id in NOT_REQUIRED_CAPS:
        cand = next((c for c in candidates if c["capability"]["id"] == cap_id), None)
        if not cand:
            continue
        fam = cand["family"] or {}
        op_row = cand["operation"] or {}
        why = skip_why[cap_id]
        decisions.append(Decision(id=f"dec-{cap_id}", capabilityId=cap_id, familyId=str(fam.get("id") or ""), operationId=str(op_row.get("operationId") or ""), label=str(cand["capability"].get("label") or cap_id), relevant=cap_id == "connectivity_insights", availability="YES" if cap_id != "connectivity_insights" else "EXPERIMENTAL", policyResult="NOT_REQUIRED", state="NOT_REQUIRED", why=why, stage="SELECT"))
        policies.append(PolicyEvaluation(f"pol-cap-{cap_id}", "CAPABILITY_API", cap_id, "NOT_REQUIRED", "CONFIGURED POLICY", why, layer="PURPOSE / DATA"))

    reach_cand = next((c for c in candidates if c["capability"]["id"] == "device_reachability"), None)
    roam_cand = next((c for c in candidates if c["capability"]["id"] == "roaming_status"), None)
    if not reach_cand or not roam_cand:
        raise HTTPException(status_code=500, detail="OTA Intent missing required Reachability/Roaming mappings")

    def _invoke_network(op_id: str, cand: dict[str, Any], provider_row: dict[str, Any], sim: dict[str, Any], inv_id: str) -> None:
        op_row = cand["operation"] or {}
        inv = _network_invocation(op_id=op_id, meta=cand["catalog"] or {}, fam=cand["family"] or {}, route=((network_routes.get(op_id) or {}).get(str(provider_row["id"])) or {}), corr_id=str(corr.get("correlationId")), sim=sim, op_row=op_row)
        inv.id = inv_id
        invocations.append(inv)
        evidence.append(Evidence(id=f"ev-{inv_id}", operationId=op_id, type=op_id, status="observed", payload={**(sim.get("raw") or {}), "simulatedFleet": True, "representativeSample": True}, purposeId=str(purpose["id"]), apiKind="NETWORK"))

    live_samples = [s for s in samples if s.get("evidence") == "live" and not s.get("prepareCohort")]
    for sample in live_samples:
        prow = next((p for p in providers if p.get("id") == sample.get("provider")), None)
        if not prow:
            continue
        reachable = bool(sample.get("reachable"))
        _invoke_network("getReachabilityStatus", reach_cand, prow, {"latencyMs": 38, "httpStatus": 200, "raw": {"deviceId": sample["id"], "reachabilityStatus": "DATA" if reachable else "UNREACHABLE", "simulatedOperatorResponse": True, "note": "API success reporting UNREACHABLE is fulfilled demand, not an API availability failure."}}, f"inv-reach-{sample['id']}")
        if prow.get("roamingAvailable") and sample.get("roaming") not in (None, "unknown"):
            _invoke_network("getRoamingStatus", roam_cand, prow, {"latencyMs": 34, "httpStatus": 200, "raw": {"deviceId": sample["id"], "roaming": bool(sample.get("roaming")), "simulatedOperatorResponse": True, "policyInterprets": True}}, f"inv-roam-{sample['id']}")

    if reassess:
        for sample in [s for s in samples if s.get("reassessCohort") == "ROLL_OUT_NOW"]:
            prow = next((p for p in providers if p.get("id") == sample.get("provider")), None)
            if not prow:
                continue
            _invoke_network("getReachabilityStatus", reach_cand, prow, {"latencyMs": 36, "httpStatus": 200, "raw": {"deviceId": sample["id"], "reachabilityStatus": "DATA", "wave": "reassess", "simulatedOperatorResponse": True}}, f"inv-reach-reassess-{sample['id']}")
            if prow.get("roamingAvailable"):
                _invoke_network("getRoamingStatus", roam_cand, prow, {"latencyMs": 32, "httpStatus": 200, "raw": {"deviceId": sample["id"], "roaming": False, "wave": "reassess", "simulatedOperatorResponse": True}}, f"inv-roam-reassess-{sample['id']}")

    decisions.append(Decision(id="dec-device_reachability", capabilityId="device_reachability", familyId=str((reach_cand["family"] or {}).get("id") or "reachability"), operationId="getReachabilityStatus", label="Device Reachability", relevant=True, availability="YES", policyResult="PERMITTED", state="INVOKED", why="Primary network evidence. DATA reachable devices may enter the cohort. Unreachable devices are deferred. An unreachable report is API success, not unfulfilled Network API demand.", stage="SELECT"))
    decisions.append(Decision(id="dec-roaming_status", capabilityId="roaming_status", familyId=str((roam_cand["family"] or {}).get("id") or "roaming"), operationId="getRoamingStatus", label="Roaming Status", relevant=True, availability="PARTIAL", policyResult="PERMITTED", state="INVOKED", why="Roaming state is supplied by the network. Configured enterprise policy defers roaming devices on this campaign. Network Provider C cannot offer Roaming Status — that gap is unfulfilled qualified demand, not device unreachability.", stage="SELECT"))
    decisions.append(Decision(id="dec-evidence-reuse", capabilityId="device_reachability", familyId="reachability", operationId="getReachabilityStatus", label="Fresh reachability evidence reused", relevant=True, availability="YES", policyResult="PERMITTED", state="EVIDENCE_REUSED", why=f"{reused:,} devices (SIMULATED FLEET) reuse fresh reachability/roaming evidence under the same enterprise, purpose and TTL. Secondary API-economy signal — not the main story.", stage="SELECT"))

    submit = domain_responses.get("addDevicesToCampaign") or {}
    invocations.append(_domain_invocation(op_id="addDevicesToCampaign", api_kind="ENTERPRISE", owner=owner, label="Enterprise OTA Platform", corr_id=str(corr.get("correlationId")), sim=submit))
    decisions.append(Decision(id="dec-addDevicesToCampaign", capabilityId=None, familyId=None, operationId="addDevicesToCampaign", label="Enterprise OTA Platform · addDevicesToCampaign", relevant=True, availability="YES", policyResult="ACT_WITH_APPROVAL", state="INVOKED", why="SIMULATED ENTERPRISE API. Not a CAMARA operationId. Submits the network-qualified cohort. Does not install firmware.", stage="EXECUTION"))
    decisions.append(Decision(id="dec-install_firmware", capabilityId=None, familyId=None, operationId="installFirmware", label="Install firmware", relevant=False, availability="OUTSIDE_NETAWARE", policyResult="NOT_AUTHORIZED", state="NOT_AUTHORIZED", why="Firmware installation belongs to the enterprise OTA platform. NetAware never performs it.", stage="AUTONOMY"))

    for action, level, detail in [
        ("read_campaign_context", "ACT", "Reading campaign context from the enterprise OTA platform is allowed."),
        ("gather_network_readiness", "ACT", "Gathering Reachability / Roaming evidence is allowed."),
        ("segment_cohort", "ACT", "Segmenting ROLL OUT NOW vs DEFER is allowed."),
        ("recommend_rollout_cohort", "ACT", "Recommending the network-qualified cohort is allowed."),
        ("submit_cohort_to_ota", "ACT_WITH_APPROVAL", "Submitting the cohort to the enterprise OTA platform requires approval. Simulated enterprise API."),
        ("install_firmware", "NOT_AUTHORIZED", "Installing firmware is outside NetAware."),
    ]:
        policies.append(PolicyEvaluation(f"pol-auto-{action}", "AUTONOMY_ACTION", action, level, "CONFIGURED POLICY", detail, layer="AUTONOMY"))

    telco_groups = [{"providerId": p.get("id"), "label": p.get("label"), "region": p.get("region"), "route": p.get("route"), "via": p.get("via"), "campaignDevices": p.get("campaign"), "enterpriseEligible": p.get("eligible"), "simulatedFleet": True} for p in providers]
    telco = {
        "neededBecause": "A cellular industrial fleet must be grouped by serving network before capability discovery.",
        "stage": "TELCO_FINDER",
        "separateFromApiFinder": True,
        "input": f"{campaign_n:,} campaign devices (SIMULATED FLEET)",
        "result": {"grouped": True, "network": "multiple providers", "groups": telco_groups},
        "simulated": True,
        "note": "Telco Finder groups network subjects. It does not evaluate Reachability or Roaming.",
    }
    api_finder = {
        "stage": "API_FINDER",
        "separateFromTelcoFinder": True,
        "results": [
            {"capabilityId": "device_reachability", "operationId": "getReachabilityStatus", "available": True, "capability": "Device Reachability"},
            {"capabilityId": "roaming_status", "operationId": "getRoamingStatus", "available": True, "capability": "Roaming Status", "note": "Unavailable on Network Provider C — that is a capability gap, not device unreachability."},
        ],
        "providerGroups": [{"label": p.get("label"), "region": p.get("region"), "route": p.get("route"), "via": p.get("via"), "reachability": bool(p.get("reachabilityAvailable")), "roaming": bool(p.get("roamingAvailable")), "gap": None if p.get("roamingAvailable") else "Roaming Status not advertised"} for p in providers],
        "simulated": True,
        "note": "API Finder is separate from Telco Finder. Availability is simulated/configured.",
    }

    known = {
        "source": "FROM ONBOARDING / CONFIGURATION",
        "rows": [
            {"label": "Enterprise", "value": enterprise.get("label")},
            {"label": "Application", "value": application.get("label")},
            {"label": "Adjacent application", "value": "Quality Inspection (unchanged) — same enterprise, different Intent"},
            {"label": "Authorized Agent", "value": agent.get("label")},
            {"label": "Domain", "value": (domain or {}).get("label")},
            {"label": "Use case", "value": (use_case or {}).get("label")},
            {"label": "Purpose", "value": purpose.get("audienceLabel") or purpose.get("label")},
            {"label": "DPV", "value": ((purpose.get("dpv") or {}).get("id") or "configured")},
            {"label": "Region", "value": "Canada / Germany / Singapore (configured)"},
            {"label": "Subscriptions", "value": "CONNECTIVITY + LOCATION_AND_MOBILITY (Configured)"},
            {"label": "Entitlements", "value": "Connected Device Operations application only"},
            {"label": "Policy", "value": policy.get("label")},
            {"label": "Autonomy", "value": "ACT discover/segment; ACT_WITH_APPROVAL submit; NOT_AUTHORIZED install firmware"},
            {"label": "Fleet", "value": "SIMULATED FLEET"},
        ],
    }

    added = _n(fleet_r, "newlyReachable") + _n(fleet_r, "noLongerRoaming")
    outcome = Outcome(
        outcome="COHORT_EXPANDED" if reassess else "NETWORK_QUALIFIED_COHORT",
        confidence=0.91,
        recommendedAction=(f"Add {added:,} previously deferred devices to the enterprise OTA campaign." if reassess else f"Submit {roll_out:,} network-suitable devices to the enterprise OTA platform. Defer {defer:,}."),
        decisionOwner="ACME_OTA_PLATFORM",
        reasonCodes=["SIMULATED_FLEET", "NETWORK_QUALIFIED_COHORT", "FIRMWARE_NOT_INSTALLED"],
        summary=("Some deferred devices are now DATA reachable / home-network. Cohort expanded. NetAware did not install firmware." if reassess else "NetAware determined which campaign devices are network-suitable to update now. The enterprise OTA platform still owns firmware installation."),
        dataUsed="Reachability and Roaming Status only. QoD, Location, Number Verification and experimental Connectivity Insights were not required.",
    )
    autonomy = {
        "observe": "ALLOWED",
        "recommend": "ALLOWED",
        "act": "ALLOWED for campaign read, readiness gather, segment, recommend",
        "actWithApproval": ["submit_cohort_to_ota"],
        "notAuthorized": ["install_firmware"],
        "note": "Enterprise OTA owns firmware installation and campaign execution. NetAware returns a network-qualified cohort.",
    }

    demand_rows = []
    for p in providers:
        demand_rows.append({"qualifiedDemand": True, "capability": "device_reachability", "provider": p.get("label"), "region": p.get("region"), "route": p.get("route"), "available": True, "entitled": True, "permitted": True, "needed": True, "fulfilled": True, "blockingGap": None, "invocationCount": p.get("eval"), "representativeVolume": True, "simulated": True})
        roam_ok = bool(p.get("roamingAvailable"))
        demand_rows.append({"qualifiedDemand": True, "capability": "roaming_status", "provider": p.get("label"), "region": p.get("region"), "route": p.get("route"), "available": roam_ok, "entitled": True, "permitted": True, "needed": True, "fulfilled": roam_ok, "blockingGap": None if roam_ok else "Roaming Status not advertised by Network Provider C", "invocationCount": 0 if not roam_ok else max(_n(p, "eval") - _n(p, "unreachable"), 0), "unfulfilledCount": _n(p, "roamingApiGap"), "representativeVolume": True, "simulated": True, "note": None if roam_ok else "Unfulfilled qualified demand is a capability/provider gap. Device UNREACHABLE is not this class."})

    demand_supply = {
        "businessDemandQualified": True,
        "demandFulfilled": True,
        "unfulfilledQualifiedDemand": api_gap > 0,
        "unfulfilledCount": api_gap,
        "unfulfilledCapability": "roaming_status" if api_gap else None,
        "unfulfilledProvider": "Network Provider C" if api_gap else None,
        "apiSuccessfullyReportedUnreachable": True,
        "unreachableIsNotUnfulfilledDemand": True,
        "providerCohorts": demand_rows,
        "note": "Demand/supply seed for later Fulfillment Coverage / Demand Map. Those UIs are not built in Cadence 11.",
        "simulated": True,
        "noRevenue": True,
    }

    ota_visual = {
        "enterprise": "ACME CONNECTED DEVICE OPERATIONS",
        "campaign": "CRITICAL FIRMWARE CAMPAIGN",
        "adjacentApplication": "Quality Inspection remains a separate Acme application (QoD closed-loop).",
        "simulatedFleet": True,
        "wave": variant_id,
        "headline": "Deferred devices moved into ROLL OUT NOW after reassessment." if reassess else "NetAware does not replace the OTA platform. It makes the rollout network-aware.",
        "funnel": [
            {"id": "campaign", "label": "OTA PLATFORM · campaign devices", "count": campaign_n, "owner": "ENTERPRISE"},
            {"id": "eligible", "label": "ENTERPRISE ELIGIBILITY · firmware / model / health", "count": eligible, "owner": "ENTERPRISE"},
            {"id": "discovery", "label": "NETWORK DISCOVERY · providers / routes", "count": eligible, "owner": "NETAWARE"},
            {"id": "readiness", "label": "NETWORK READINESS · reachable / roaming / capability", "count": eval_n, "owner": "NETAWARE"},
            {"id": "now", "label": "ROLL OUT NOW", "count": roll_out, "owner": "NETAWARE", "tone": "ok"},
            {"id": "defer", "label": "DEFER / RETRY", "count": defer, "owner": "NETAWARE", "tone": "warn"},
        ],
        "deferredReasons": [
            {"id": "unreachable", "label": "DEFER — UNREACHABLE", "count": unreachable, "note": "API successfully reported not DATA reachable. Not an API availability failure."},
            {"id": "roaming", "label": "DEFER — ROAMING POLICY", "count": roaming_defer, "note": "CONFIGURED POLICY interprets roaming. Roaming is not automatically bad."},
            {"id": "gap", "label": "UNFULFILLED — PROVIDER/API GAP", "count": api_gap, "note": "Roaming Status unavailable on Network Provider C."},
        ],
        "providers": telco_groups,
        "apiFinder": api_finder.get("providerGroups"),
        "cohorts": {"rollOutNow": roll_out, "deferUnreachable": unreachable, "deferRoamingPolicy": roaming_defer, "unfulfilledApiGap": api_gap},
        "movement": {"fromUnreachable": _n(fleet_r, "newlyReachable") if reassess else 0, "fromRoaming": _n(fleet_r, "noLongerRoaming") if reassess else 0, "added": added if reassess else 0},
        "volume": {"label": "SIMULATED DEMO VOLUME", "oneIntent": intent_id, "reachabilityLive": vol_wave.get("reachabilityLive"), "roamingLive": vol_wave.get("roamingLive"), "reachabilityReused": (volume.get("prepare") or {}).get("reachabilityReused") if not reassess else 0, "note": "ONE BUSINESS INTENT → THOUSANDS OF QUALIFIED NETWORK API INTERACTIONS. No revenue calculated."},
        "close": ["Your OTA platform already knows what needs updating.", "NetAware determines which cellular devices are network-suitable to update now across operators and regions.", "Your OTA platform performs the rollout; NetAware can reassess the deferred fleet for the next wave."],
        "enterpriseValue": "Safer / more targeted connected-device operations.",
        "networkValue": "A single enterprise workflow can generate qualified Network API demand across a large fleet.",
        "didNotInstallFirmware": True,
        "footer": "NETAWARE DID NOT INSTALL FIRMWARE. It determined which devices were network-suitable for the enterprise OTA workflow.",
        "samples": samples,
        "labels": ["SIMULATED FLEET", "SIMULATED ENTERPRISE API", "CONFIGURED POLICY", "SIMULATED OPERATOR RESPONSE"],
        "policy": {"reachability": "DATA reachable → eligible; not DATA reachable → DEFER / RETRY", "roaming": "Network supplies roaming state. CONFIGURED POLICY defers roaming on this campaign. Roaming is not automatically bad."},
    }

    route = {"type": "HYBRID", "from": "NetAware", "display": "ONE ENTERPRISE INTENT → MULTIPLE NETWORK PROVIDERS / ROUTES → ONE NORMALIZED BUSINESS OUTCOME", "note": "Provider A and C are DIRECT. Provider B is AGGREGATED via Aggregator A.", "legs": [{"provider": p.get("label"), "region": p.get("region"), "route": p.get("route"), "via": p.get("via")} for p in providers]}
    active_plan = plan_v2 or plan_v1
    invoked_ids = {i.operationId for i in invocations}
    for step in active_plan.steps:
        if step.operationId == "installFirmware":
            step.state = "NOT_AUTHORIZED"
        elif step.operationId in invoked_ids:
            step.state = "INVOKED"
        elif step.state == "PLANNED" and step.n >= 4:
            step.state = "COMPLETED"

    beats = [
        Beat(1, 0, "ACME DEVICE OPS AGENT", "AGENT_AUTHENTICATED", "Business event received", "Critical firmware 8.4 must roll out to a cellular industrial fleet.", "agent"),
        Beat(2, 400, "NETAWARE AX", "INTENT_RECEIVED", "Intent resolved", "prepare_ota_cohort — which eligible devices are network-suitable now?", "netaware"),
        Beat(3, 800, "CONTEXT / POLICY", "CONTEXT_RESOLVED", "Context resolved", "Enterprise, Connected Device Operations application, purpose and CONFIGURED POLICY from onboarding.", "policy"),
        Beat(4, 1200, "ENTERPRISE OTA", "INVOKED", "listDevices", "SIMULATED ENTERPRISE API — 10,000 campaign devices (SIMULATED FLEET).", "enterprise"),
        Beat(5, 1600, "ENTERPRISE OTA", "INVOKED", "getTwin", "OTA platform already determined 8,400 firmware/model eligible devices.", "enterprise"),
        Beat(6, 2000, "TELCO FINDER", "TELCO_FINDER", "Telco Finder", "Group 10,000 campaign devices by Network Provider A / B / C. Separate from API Finder.", "finder"),
        Beat(7, 2400, "API FINDER", "API_FINDER", "API Finder", "A/B: Reachability yes, Roaming yes. C: Reachability yes, Roaming unavailable.", "finder"),
        Beat(8, 2800, "NETAWARE AX", "NOT_REQUIRED", "QoD / Location / Insights skipped", "They would not change the OTA cohort decision. Connectivity Insights remains experimental.", "netaware"),
        Beat(9, 3200, "NETWORK PROVIDER", "INVOKED", "getReachabilityStatus", "Representative samples + aggregate SIMULATED DEMO VOLUME. Not 10,000 trace rows.", "provider"),
        Beat(10, 3600, "NETWORK PROVIDER", "INVOKED", "getRoamingStatus", "Roaming state supplied by network. CONFIGURED POLICY interprets it. Roaming is not automatically bad.", "provider"),
        Beat(11, 4000, "NETAWARE AX", "COMPLETED", "Segment cohort", f"ROLL OUT NOW {roll_out:,} · DEFER {defer:,} (SIMULATED FLEET).", "netaware"),
    ]
    n, t = 12, 4400
    if reassess:
        beats.append(Beat(n, t, "NETAWARE AX", "REPLAN", "Observe / reassess", f"{_n(fleet_r, 'newlyReachable'):,} previously unreachable and {_n(fleet_r, 'noLongerRoaming'):,} previously roaming devices are now ready.", "netaware"))
        n += 1
        t += 400
    beats.append(Beat(n, t, "ENTERPRISE OTA", "INVOKED", "addDevicesToCampaign", "SIMULATED ENTERPRISE API. Cohort submitted. Firmware not installed.", "enterprise"))
    n += 1
    t += 400
    beats.append(Beat(n, t, "CONTEXT / POLICY", "AUTONOMY", "Autonomy check", "submit_cohort_to_ota is ACT_WITH_APPROVAL. install_firmware is NOT_AUTHORIZED.", "policy"))
    n += 1
    t += 400
    beats.append(Beat(n, t, "ACME DEVICE OPS AGENT", "OUTCOME", "Business outcome returned", f"{outcome.outcome}. Enterprise OTA still owns the rollout.", "agent"))

    invoked_ops = {i.operationId for i in invocations if i.apiKind == "NETWORK"}
    if invoked_ops - {"getReachabilityStatus", "getRoamingStatus"}:
        raise HTTPException(status_code=500, detail="OTA invoked a Network API outside the minimum set")
    if {"createSession", "verifyLocation", "checkNetworkQuality"} & invoked_ops:
        raise HTTPException(status_code=500, detail="OTA forced QoD, Location, or experimental Insights")

    return ExecutionTrace(
        executionId=exec_id,
        traceId=str(corr.get("traceId")),
        correlationId=str(corr.get("correlationId")),
        intentId=intent_id,
        status="COMPLETED",
        request=req_body,
        knownFromConfiguration=known,
        purpose={"id": purpose.get("id"), "label": purpose.get("audienceLabel") or purpose.get("label"), "source": "CONFIGURED APPLICATION / INTENT PROFILE", "dpv": (purpose.get("dpv") or {}).get("id"), "note": "Purpose comes from configuration. Not inferred from arbitrary runtime text."},
        actor={"agent": agent, "application": application, "enterprise": enterprise, "kind": "AUTHORIZED_AGENT"},
        telcoFinder=telco,
        apiFinder=api_finder,
        route=route,
        routes=route.get("legs") or [],
        plan=active_plan,
        planHistory=[plan_v1, plan_v2] if plan_v2 else [plan_v1],
        replan={"occurred": True, "narrative": "Deferred devices rechecked. Some are now reachable / home-network. Cohort expanded. Firmware still not installed by NetAware."} if reassess else None,
        decisions=decisions,
        invocations=invocations,
        evidence=evidence,
        policyEvaluations=policies,
        autonomy=autonomy,
        outcome=outcome,
        economy={"catalogFamiliesAvailable": len(registry.families), "mappedToIntent": len(mapped), "domainInvoked": sum(1 for i in invocations if i.apiKind in {"DOMAIN", "ENTERPRISE"}), "networkInvoked": sum(1 for i in invocations if i.apiKind == "NETWORK"), "invoked": len(invocations), "evidenceReused": reused, "consideredNotRequired": 3, "blockedByPolicy": 0, "simulatedVolume": {"label": "SIMULATED DEMO VOLUME", "reachabilityLive": vol_wave.get("reachabilityLive"), "roamingLive": vol_wave.get("roamingLive"), "noRevenue": True}, "note": "Representative invocations only. Aggregate volume is labelled SIMULATED DEMO VOLUME."},
        beats=beats,
        honesty={"simulated": True, "liveOperators": False, "policyIsConfiguredDemo": True, "simulatedFleet": True, "simulatedEnterpriseApi": True, "simulatedOperatorResponse": True, "networkDoesNotInstallFirmware": True, "noFakeRevenue": True},
        demandSupply=demand_supply,
        otaVisual=ota_visual,
        conditionChange={"observed": True, "from": "DEFER", "to": "ROLL_OUT_NOW", "devices": added} if reassess else None,
    )
