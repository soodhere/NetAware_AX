"""Cadence 13 — derived Fulfillment Coverage. Not a parallel engine. Not revenue."""
from __future__ import annotations

import json
from typing import Any

from .config import SCHEMAS_DIR
from .graph import KnowledgeGraph
from .model import ConfigStore
from .nv_runtime import _evaluate_paths, _operator_readiness
from .portfolio import visible_rows
from .registry import CatalogRegistry
from .runtime import _family_for, _primary_op, _provider_ops, evaluate_capability_policy

STATES = (
    "FULFILLABLE",
    "FULFILLABLE_WITH_REDUCED_EVIDENCE",
    "PARTIALLY_FULFILLABLE",
    "BLOCKED",
    "NOT_AVAILABLE",
    "NOT_CONFIGURED",
    "NOT_APPLICABLE",
)

GAP_CODES = (
    "API_NOT_AVAILABLE",
    "NOT_SUBSCRIBED",
    "NOT_ENTITLED",
    "PURPOSE_NOT_PERMITTED",
    "CONSENT_MISSING",
    "AGREEMENT_GAP",
    "OPERATOR_READINESS",
    "ENTITLEMENT_SERVER_UNAVAILABLE",
    "ACCESS_PATH_UNSUPPORTED",
    "ROUTE_UNAVAILABLE",
    "REGION_NOT_SUPPORTED",
    "CAPABILITY_GAP",
)

EVIDENCE_TO_CAP = {
    "NUMBER_POSSESSION": "number_possession_verification",
    "SIM_CONTINUITY": "sim_continuity",
    "DEVICE_CONTINUITY": "device_continuity",
    "DEVICE_IDENTIFIER": "device_identifier",
    "DEVICE_REACHABILITY": "device_reachability",
    "AGE_ASSERTION": "age_verification",
    "CONNECTIVITY": "connectivity_insights",
    "QOD_SESSION": "quality_on_demand",
    "ROAMING": "roaming_status",
}

PROVIDER_TYPE = {
    "operator": "NETWORK_PROVIDER",
    "aggregator": "AGGREGATOR",
    "specialist": "SPECIALIST",
}

REGION_LABELS = {"CA": "Canada", "DE": "Germany", "SG": "Singapore", "EU": "Europe"}


def coverage_doc(store: ConfigStore) -> dict[str, Any]:
    return store.fulfillment_coverage or {}


def fulfillment_schema_path():
    return SCHEMAS_DIR / "fulfillment-record.json"


def _label(store: ConfigStore, provider_id: str | None) -> str:
    if not provider_id:
        return "—"
    p = store.provider_by_id.get(provider_id) or {}
    return str(p.get("audienceLabel") or p.get("label") or provider_id)


def _provider_type(store: ConfigStore, provider_id: str | None) -> str | None:
    if not provider_id:
        return None
    kind = str((store.provider_by_id.get(provider_id) or {}).get("kind") or "")
    return PROVIDER_TYPE.get(kind, "NETWORK_PROVIDER")


def _region_label(doc: dict[str, Any], region: str) -> str:
    labels = {**REGION_LABELS, **(doc.get("regionLabels") or {})}
    return str(labels.get(region) or region)


def _purpose(store: ConfigStore, row: dict[str, Any], profile: dict[str, Any] | None) -> dict[str, Any]:
    pid = str(row.get("purpose") or (profile or {}).get("purposeId") or "")
    return store.purpose_by_id.get(pid) or {}


def _policy_id(row: dict[str, Any], store: ConfigStore, intent_id: str, enterprise_id: str) -> str:
    if row.get("policy"):
        return str(row["policy"])
    found = next(
        (p for p in store.policies if p.get("intentId") == intent_id and p.get("enterpriseId") == enterprise_id),
        None,
    )
    return str((found or {}).get("id") or "")


def _routes(store: ConfigStore, operation_id: str | None, provider_id: str | None) -> list[dict[str, Any]]:
    if not operation_id or not provider_id:
        return []
    found = [
        r
        for r in store.routes
        if r.get("operationId") == operation_id and r.get("providerId") == provider_id
    ]
    if found:
        return found
    ops = _provider_ops(store, provider_id)
    if operation_id not in ops:
        return []
    kind = str((store.provider_by_id.get(provider_id) or {}).get("kind") or "operator")
    rtype = "AGGREGATED" if kind == "aggregator" else "DIRECT"
    return [
        {
            "id": f"inferred-{provider_id}-{operation_id}",
            "operationId": operation_id,
            "providerId": provider_id,
            "type": rtype,
            "inferred": True,
            "source": "DERIVED",
        }
    ]


def _map_policy_gap(pol: dict[str, Any]) -> str | None:
    result = str(pol.get("result") or "")
    if result == "NOT_SUBSCRIBED":
        return "NOT_SUBSCRIBED"
    if result == "NOT_ENTITLED":
        return "NOT_ENTITLED"
    if result == "PURPOSE_DENIED":
        return "PURPOSE_NOT_PERMITTED"
    if result == "BLOCKED_BY_POLICY":
        if pol.get("consentRequired") and not pol.get("consentAvailable"):
            return "CONSENT_MISSING"
        return "PURPOSE_NOT_PERMITTED"
    return None


def _min_sufficient(store: ConfigStore, profile: dict[str, Any] | None, intent_id: str, candidates: list[dict[str, Any]]) -> list[str]:
    mapped = []
    for ev in (profile or {}).get("minimumEvidence") or []:
        cap = EVIDENCE_TO_CAP.get(str(ev))
        if cap:
            mapped.append(cap)
    required = [str(c["id"]) for c in candidates if c.get("role") == "required"]
    gate = list(dict.fromkeys(mapped or required))
    if intent_id == "prepare_ota_cohort":
        extra = list((store.ota_device_fleet or {}).get("networkAdds", {}).get("required") or [])
        for cap in extra:
            if cap not in gate:
                gate.append(cap)
    return gate


def _role_bucket(cap_id: str, profile: dict[str, Any] | None) -> str:
    optional_ev = {EVIDENCE_TO_CAP.get(str(e)) for e in ((profile or {}).get("optionalEvidence") or [])}
    for row in (profile or {}).get("candidateCapabilities") or []:
        if row.get("id") != cap_id:
            continue
        role = str(row.get("role") or "considered")
        if cap_id in optional_ev and role == "required":
            return "CONDITIONAL"
        if role == "required":
            return "REQUIRED"
        return "OPTIONAL"
    return "OPTIONAL"


def _candidates(profile: dict[str, Any] | None, graph: KnowledgeGraph, intent_id: str) -> list[dict[str, Any]]:
    rows = list((profile or {}).get("candidateCapabilities") or [])
    if rows:
        return [{"id": str(r["id"]), "role": str(r.get("role") or "considered")} for r in rows]
    out = []
    for link in graph.intent_caps.get(intent_id) or []:
        out.append({"id": str(link["capabilityId"]), "role": str(link.get("role") or "considered")})
    return out


def _nv_readiness(
    store: ConfigStore,
    *,
    cap_id: str,
    provider_id: str,
    access_type: str | None,
    ts43: bool,
    sim: bool,
) -> dict[str, Any]:
    empty = {
        "applicable": False,
        "ready": True,
        "selectedPath": None,
        "ecs": None,
        "nv1": None,
        "nv2": None,
        "gap": None,
        "kind": "NOT_APPLICABLE",
    }
    if cap_id != "number_possession_verification" or not access_type:
        return empty
    doc = coverage_doc(store)
    ecs_meta = doc.get("ecs") or {}
    readiness = _operator_readiness(store, provider_id)
    paths = _evaluate_paths(access_type, readiness, {"ts43ClientAvailable": ts43, "simAvailable": sim})
    selected = paths.get("selectedPath")
    ecs = str(paths.get("ecs") or "UNKNOWN")
    gap = None
    ready = bool(selected)
    if access_type.upper() in {"WIFI", "WLAN", "VPN"} and ecs != "AVAILABLE":
        gap = "ENTITLEMENT_SERVER_UNAVAILABLE"
        ready = False
    elif access_type.upper() == "CELLULAR" and not selected:
        gap = "ACCESS_PATH_UNSUPPORTED"
        ready = False
    elif not selected:
        gap = "OPERATOR_READINESS"
        ready = False
    return {
        "applicable": True,
        "ready": ready,
        "selectedPath": selected,
        "ecs": ecs,
        "nv1Supported": paths.get("nv1Supported"),
        "nv2Supported": paths.get("nv2Supported"),
        "nv1": paths.get("nv1"),
        "nv2": paths.get("nv2"),
        "accessType": paths.get("accessType"),
        "gap": gap,
        "kind": "OPERATOR_PREREQUISITE",
        "label": ecs_meta.get("label") or "CONFIGURED OPERATOR READINESS",
        "notACamaraApi": True,
        "netAwareDoesNotControl": True,
        "source": "CONFIGURED_OPERATOR_READINESS",
    }


def _evaluate_capability(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    *,
    cap_id: str,
    role: str,
    enterprise_id: str,
    policy_id: str,
    purpose: dict[str, Any],
    provider_id: str | None,
    route_provider_id: str | None,
    access_type: str | None,
    ts43: bool,
    sim: bool,
) -> dict[str, Any]:
    cap = store.capability_by_id.get(cap_id) or {"id": cap_id, "label": cap_id}
    fam = _family_for(registry, cap_id)
    family = str((fam or {}).get("familyGroup") or cap.get("family") or "")
    op_row = _primary_op(graph, cap_id)
    op_id = str((op_row or {}).get("operationId") or "") if op_row else None
    pol = evaluate_capability_policy(
        store,
        enterprise_id=enterprise_id,
        policy_id=policy_id,
        purpose=purpose,
        capability_id=cap_id,
        family=family,
    )
    api_provider = route_provider_id or provider_id
    ops = _provider_ops(store, api_provider) if api_provider else set()
    api_here = bool(op_id and op_id in ops)
    any_ops = any(op_id in _provider_ops(store, p["id"]) for p in store.providers) if op_id else False
    routes = _routes(store, op_id, api_provider)
    route = routes[0] if routes else None
    route_type = str((route or {}).get("type") or "") or None
    nv = _nv_readiness(
        store, cap_id=cap_id, provider_id=str(provider_id or ""), access_type=access_type, ts43=ts43, sim=sim
    )

    relevant = "YES"
    permitted = "YES" if pol.get("result") == "PERMITTED" else "NO"
    available = "YES" if api_here else "NO"
    ready = "YES"
    routable = "YES" if route else "NO"
    gaps: list[dict[str, Any]] = []

    policy_gap = _map_policy_gap(pol)
    if policy_gap:
        permitted = "NO"
        gaps.append({"code": policy_gap, "capabilityId": cap_id, "detail": pol.get("detail")})
    if not api_here:
        gaps.append(
            {
                "code": "API_NOT_AVAILABLE",
                "capabilityId": cap_id,
                "detail": f"{op_id or cap_id} is not advertised on the selected provider/route.",
            }
        )
        ready = "NO"
    if api_here and not route:
        gaps.append(
            {
                "code": "ROUTE_UNAVAILABLE",
                "capabilityId": cap_id,
                "detail": "No configured NetAware route for this operation/provider.",
            }
        )
        routable = "NO"
    if nv.get("applicable"):
        if not nv.get("ready"):
            ready = "NO"
            code = str(nv.get("gap") or "OPERATOR_READINESS")
            gaps.append(
                {
                    "code": code,
                    "capabilityId": cap_id,
                    "detail": "Operator Entitlement Server is a technical prerequisite for NV2. NetAware does not control the operator ECS.",
                }
            )
        else:
            ready = "YES"

    fulfillable = permitted == "YES" and available == "YES" and ready == "YES" and routable == "YES"
    return {
        "id": cap_id,
        "label": cap.get("label") or cap_id,
        "role": role,
        "family": family,
        "familyId": (fam or {}).get("id"),
        "operationId": op_id,
        "relevant": relevant,
        "permitted": permitted,
        "available": available,
        "ready": ready,
        "routable": routable,
        "fulfillable": "YES" if fulfillable else "NO",
        "apiAvailability": "AVAILABLE" if api_here else "UNAVAILABLE",
        "apiAvailableInCatalog": any_ops,
        "route": route_type,
        "routeId": (route or {}).get("id"),
        "policy": pol,
        "operatorReadiness": nv,
        "gaps": gaps,
        "provenance": [
            {"fact": f"Capability {cap_id} role {role}", "source": "INTENT PROFILE"},
            {"fact": f"Policy result {pol.get('result')}", "source": "CONFIGURED POLICY"},
            {"fact": f"Provider operation {op_id} {'present' if api_here else 'absent'}", "source": "SIMULATED PROVIDER DATA"},
            {"fact": "Capability fulfillment", "source": "DERIVED"},
        ],
    }


def _intent_status(
    cap_rows: list[dict[str, Any]], gate: list[str], optional_ids: list[str], region_state: str | None
) -> tuple[str, list[dict[str, Any]]]:
    if region_state:
        return region_state, []
    by_id = {r["id"]: r for r in cap_rows}
    gate_rows = [by_id[i] for i in gate if i in by_id]
    optional_rows = [by_id[i] for i in optional_ids if i in by_id]
    blocking: list[dict[str, Any]] = []
    for row in gate_rows:
        if row.get("fulfillable") != "YES":
            blocking.extend(row.get("gaps") or [])
    optional_gaps = []
    for row in optional_rows:
        if row.get("fulfillable") != "YES":
            optional_gaps.extend(row.get("gaps") or [])
    if not gate_rows:
        return "NOT_CONFIGURED", [
            {"code": "CAPABILITY_GAP", "capabilityId": None, "detail": "No minimum sufficient capability set is configured."}
        ]
    failed = [r for r in gate_rows if r.get("fulfillable") != "YES"]
    passed = [r for r in gate_rows if r.get("fulfillable") == "YES"]
    if not failed:
        if optional_gaps:
            return "FULFILLABLE_WITH_REDUCED_EVIDENCE", []
        return "FULFILLABLE", []
    codes = {g.get("code") for g in blocking}
    if passed and failed and "API_NOT_AVAILABLE" in codes:
        return "PARTIALLY_FULFILLABLE", blocking
    if codes & {"ENTITLEMENT_SERVER_UNAVAILABLE", "OPERATOR_READINESS", "ACCESS_PATH_UNSUPPORTED"}:
        return "BLOCKED", blocking
    if codes & {"CONSENT_MISSING", "PURPOSE_NOT_PERMITTED", "NOT_SUBSCRIBED", "NOT_ENTITLED"}:
        return "BLOCKED", blocking
    if codes & {"API_NOT_AVAILABLE", "ROUTE_UNAVAILABLE"}:
        return "NOT_AVAILABLE", blocking
    return "BLOCKED", blocking


def _funnel(cap_rows: list[dict[str, Any]], status: str) -> dict[str, Any]:
    n = len(cap_rows)
    relevant = sum(1 for r in cap_rows if r.get("relevant") == "YES")
    permitted = sum(1 for r in cap_rows if r.get("permitted") == "YES")
    available = sum(1 for r in cap_rows if r.get("available") == "YES")
    ready = sum(1 for r in cap_rows if r.get("ready") == "YES" and r.get("available") == "YES")
    routable = sum(1 for r in cap_rows if r.get("routable") == "YES" and r.get("ready") == "YES" and r.get("available") == "YES")
    return {
        "candidate": n,
        "relevant": relevant,
        "permitted": permitted,
        "available": available,
        "operatorReady": ready,
        "routable": routable,
        "intentStatus": status,
        "note": "Counts are derived from configured capability evaluation. Not fabricated.",
        "source": "DERIVED",
    }


def _why_panel(
    status: str,
    cap_rows: list[dict[str, Any]],
    blocking: list[dict[str, Any]],
    selected_path: str | None,
    hf_note: dict[str, Any] | None,
    qd: dict[str, Any] | None,
) -> dict[str, Any]:
    steps = []
    for row in cap_rows:
        nv = row.get("operatorReadiness") or {}
        steps.append(
            {
                "capability": row.get("label"),
                "capabilityId": row.get("id"),
                "role": row.get("role"),
                "relevant": row.get("relevant"),
                "permitted": row.get("permitted"),
                "available": row.get("available"),
                "ready": row.get("ready"),
                "routable": row.get("routable"),
                "fulfillable": row.get("fulfillable"),
                "api": row.get("apiAvailability"),
                "operationId": row.get("operationId"),
                "route": row.get("route"),
                "nv1": "SUPPORTED" if nv.get("nv1Supported") else ("NOT_APPLICABLE" if not nv.get("applicable") else "NOT_SUPPORTED"),
                "nv2": "SUPPORTED" if nv.get("nv2Supported") else ("NOT_APPLICABLE" if not nv.get("applicable") else "NOT_SUPPORTED"),
                "entitlementServer": nv.get("ecs") if nv.get("applicable") else "NOT_APPLICABLE",
                "entitlementServerKind": "OPERATOR_PREREQUISITE" if nv.get("applicable") else None,
                "gaps": row.get("gaps") or [],
            }
        )
    return {
        "status": status,
        "chain": [
            "ENTERPRISE",
            "APPLICATION",
            "INTENT",
            "REQUIRED / OPTIONAL CAPABILITIES",
            "GOVERNANCE ELIGIBILITY",
            "REGION",
            "NETWORK / OPERATOR",
            "API AVAILABILITY",
            "OPERATOR READINESS / PREREQUISITES",
            "PROVIDER / ROUTE",
            "FULFILLMENT",
        ],
        "distinctions": {
            "relevant": "Is this capability in the Intent Profile candidate set?",
            "permitted": "Do subscription, entitlement, purpose, consent and policy allow it?",
            "available": "Does the selected provider advertise the API operation?",
            "ready": "Are operator technical prerequisites configured ready (for example ECS for NV2)?",
            "routable": "Is a NetAware DIRECT / AGGREGATED / HYBRID route configured?",
            "fulfillable": "Can the minimum sufficient set be satisfied?",
        },
        "capabilities": steps,
        "selectedPath": selected_path,
        "blockingGap": blocking[0] if blocking else None,
        "fulfillmentVsOutcome": hf_note,
        "qualifiedDemand": qd,
        "note": "Do not collapse all failures into unavailable. UNKNOWN/NOT_CONFIGURED is not BLOCKED.",
    }


def _build_record(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    *,
    row: dict[str, Any],
    slice_id: str,
    region: str,
    provider_id: str | None,
    route_provider_id: str | None,
    route_type_hint: str | None,
    access_type: str | None,
    ts43: bool,
    sim: bool,
    showcase: str | None,
    region_state: str | None,
    qualified_demand: dict[str, Any] | None,
    serving_label: str | None = None,
) -> dict[str, Any]:
    doc = coverage_doc(store)
    intent_id = str(row.get("intentId") or "")
    enterprise_id = str(row.get("enterpriseId") or "")
    application_id = str(row.get("applicationId") or "")
    profile = store.intent_profile_by_id.get(intent_id)
    purpose = _purpose(store, row, profile)
    policy_id = _policy_id(row, store, intent_id, enterprise_id)
    candidates = _candidates(profile, graph, intent_id)
    gate = _min_sufficient(store, profile, intent_id, candidates)
    cap_rows = []
    if not region_state:
        for cand in candidates:
            cap_rows.append(
                _evaluate_capability(
                    store,
                    graph,
                    registry,
                    cap_id=str(cand["id"]),
                    role=_role_bucket(str(cand["id"]), profile),
                    enterprise_id=enterprise_id,
                    policy_id=policy_id,
                    purpose=purpose,
                    provider_id=provider_id,
                    route_provider_id=route_provider_id,
                    access_type=access_type,
                    ts43=ts43,
                    sim=sim,
                )
            )
    optional_evidence_caps = [
        EVIDENCE_TO_CAP.get(str(e))
        for e in ((profile or {}).get("optionalEvidence") or [])
        if EVIDENCE_TO_CAP.get(str(e)) and EVIDENCE_TO_CAP.get(str(e)) not in gate
    ]
    status, blocking = _intent_status(cap_rows, gate, [c for c in optional_evidence_caps if c], region_state)
    hf = doc.get("highFlightDistinction") or {}
    hf_note = None
    if intent_id == hf.get("intentId") and status in {"FULFILLABLE", "FULFILLABLE_WITH_REDUCED_EVIDENCE"}:
        hf_note = {**hf, "source": "DERIVED"}
        status = "FULFILLABLE"

    route_types = list(
        dict.fromkeys([c.get("route") for c in cap_rows if c.get("route")] + ([route_type_hint] if route_type_hint else []))
    )
    route = route_type_hint or (route_types[0] if len(route_types) == 1 else ("HYBRID" if route_types else None))
    api_states = {c.get("apiAvailability") for c in cap_rows}
    api_availability = "MIXED" if len(api_states) > 1 else next(iter(api_states), "UNKNOWN")
    if region_state == "NOT_CONFIGURED":
        api_availability = "NOT_CONFIGURED"
        status = "NOT_CONFIGURED"
        blocking = []
    elif region_state == "NOT_AVAILABLE":
        api_availability = "UNAVAILABLE"
        status = "NOT_AVAILABLE"
        hint = None
        for item in row.get("regions") or []:
            if str(item.get("id")) == region:
                hint = item.get("blockingGap")
        blocking = [
            {
                "code": "REGION_NOT_SUPPORTED",
                "capabilityId": None,
                "detail": str(hint or "Capability not offered in this region."),
            }
        ]

    readiness_label = "READY"
    if any((c.get("operatorReadiness") or {}).get("applicable") and not (c.get("operatorReadiness") or {}).get("ready") for c in cap_rows):
        readiness_label = "NOT_READY"
    elif status == "NOT_CONFIGURED":
        readiness_label = "NOT_CONFIGURED"
    elif status == "PARTIALLY_FULFILLABLE":
        readiness_label = "PARTIAL"
    elif status in {"BLOCKED", "NOT_AVAILABLE"}:
        readiness_label = "NOT_READY"

    selected_path = None
    for c in cap_rows:
        nv = c.get("operatorReadiness") or {}
        if nv.get("selectedPath"):
            selected_path = nv["selectedPath"]

    ent = store.enterprise_by_id.get(enterprise_id) or {}
    app = store.application_by_id.get(application_id) or {}
    intent = store.intent_by_id.get(intent_id) or {}
    domain = store.domain_by_id.get(str(ent.get("domainId") or "")) or {}

    provenance = [
        {"fact": f"Portfolio scenario {row.get('id')}", "source": "ONBOARDING"},
        {"fact": f"Intent {intent_id} requires {', '.join(gate) or 'configured minimum'}", "source": "INTENT PROFILE"},
        {"fact": f"Purpose {(purpose or {}).get('id')}", "source": "CONFIGURED POLICY"},
        {"fact": f"Provider {_label(store, route_provider_id or provider_id)}", "source": "SIMULATED PROVIDER DATA"},
        {"fact": f"Fulfillment {status}", "source": "DERIVED"},
    ]
    if access_type:
        provenance.append({"fact": f"Access type {access_type} from runtime/client context", "source": "RUNTIME"})
        provenance.append({"fact": "NV path / ECS readiness", "source": "CONFIGURED_OPERATOR_READINESS"})

    qd = None
    if row.get("qualifiedDemand"):
        qd = {
            "exists": True,
            "notRevenue": True,
            "meaning": "A legitimate enterprise Intent requires a network capability.",
            "source": "CONFIGURATION",
        }
    if qualified_demand:
        qd = {**(qd or {}), **qualified_demand, "notRevenue": True}
        if status == "PARTIALLY_FULFILLABLE" and qualified_demand.get("gapClass"):
            blocking = list(blocking) + [
                {
                    "code": str(qualified_demand.get("gapClass")),
                    "capabilityId": qualified_demand.get("capabilityId"),
                    "detail": qualified_demand.get("note") or "Capability gap on this provider.",
                    "affectedCohort": qualified_demand.get("unfulfilledCount"),
                    "impact": "Some qualified fleet demand cannot be fulfilled.",
                }
            ]

    return {
        "id": slice_id,
        "enterpriseId": enterprise_id,
        "enterpriseLabel": ent.get("label"),
        "applicationId": application_id,
        "applicationLabel": app.get("label"),
        "intentId": intent_id,
        "intentLabel": intent.get("label"),
        "useCaseId": row.get("useCaseId"),
        "industry": row.get("industry"),
        "industryLabel": domain.get("label") or row.get("industry"),
        "maturity": row.get("scenarioMaturity"),
        "region": region,
        "regionLabel": _region_label(doc, region),
        "subjectType": "MSISDN" if intent_id == "verify_mobile_number" else "DEVICE",
        "accessType": access_type,
        "requiredCapabilities": [c["id"] for c in cap_rows if c.get("role") == "REQUIRED"],
        "optionalCapabilities": [c["id"] for c in cap_rows if c.get("role") == "OPTIONAL"],
        "conditionalCapabilities": [c["id"] for c in cap_rows if c.get("role") == "CONDITIONAL"],
        "minimumSufficientSet": gate,
        "capabilities": cap_rows,
        "provider": provider_id,
        "providerLabel": serving_label or _label(store, provider_id),
        "providerType": _provider_type(store, provider_id),
        "routeProvider": route_provider_id or provider_id,
        "routeProviderLabel": _label(store, route_provider_id or provider_id),
        "route": route,
        "apiAvailability": api_availability,
        "operatorReadiness": readiness_label,
        "subscription": (cap_rows[0]["policy"].get("subscription") if cap_rows else None),
        "entitlement": (cap_rows[0]["policy"].get("entitlement") if cap_rows else None),
        "purpose": (purpose or {}).get("id"),
        "purposeLabel": (purpose or {}).get("label"),
        "consent": "MISSING"
        if any(g.get("code") == "CONSENT_MISSING" for c in cap_rows for g in c.get("gaps") or [])
        else "NOT_REQUIRED_OR_AVAILABLE",
        "agreement": (cap_rows[0]["policy"].get("agreement") if cap_rows else None),
        "fulfillmentStatus": status,
        "blockingGaps": blocking,
        "selectedPath": selected_path,
        "applicationDoesNotSelectPath": intent_id == "verify_mobile_number",
        "showcase": showcase,
        "funnel": _funnel(cap_rows, status),
        "fulfillmentVsOutcome": hf_note,
        "qualifiedDemand": qd,
        "provenance": provenance,
        "why": _why_panel(status, cap_rows, blocking, selected_path, hf_note, qd),
        "coverageHref": f"/coverage/record/{slice_id}",
        "portfolioHref": f"/demo/{enterprise_id}/{row.get('useCaseId')}",
        "notSla": True,
        "notRevenue": True,
    }


def _providers_for_region(row: dict[str, Any], region: dict[str, Any]) -> list[tuple[str | None, str | None, str | None]]:
    rtype = region.get("route")
    ids = list(row.get("providers") or [])
    if rtype == "AGGREGATED":
        agg = "simulated-aggregator-b"
        serving = ids[0] if ids and ids[0] != agg else None
        return [(serving or agg, agg, "AGGREGATED")]
    if rtype == "HYBRID":
        return [(pid, pid, "HYBRID") for pid in ids] or [(None, None, "HYBRID")]
    return [(pid, pid, rtype or "DIRECT") for pid in ids] or [(None, None, rtype)]


def _slices(store: ConfigStore) -> list[dict[str, Any]]:
    doc = coverage_doc(store)
    skip = set(doc.get("skipAutoPortfolioIds") or [])
    out: list[dict[str, Any]] = []
    by_id = {row.get("id"): row for row in visible_rows(store)}

    for row in visible_rows(store):
        if row.get("id") in skip:
            continue
        maturity = str(row.get("scenarioMaturity") or "")
        for region in row.get("regions") or [{"id": "CA"}]:
            rid = str(region.get("id") or "CA")
            availability = str(region.get("availability") or "")
            if maturity == "EXPLORE" or not (row.get("providers") or []) or availability == "OPPORTUNITY":
                out.append(
                    {
                        "id": f"{row.get('id')}-{rid}-unconfigured",
                        "row": row,
                        "region": rid,
                        "providerId": None,
                        "routeProviderId": None,
                        "routeType": None,
                        "regionState": "NOT_CONFIGURED",
                    }
                )
                continue
            if availability == "UNAVAILABLE":
                out.append(
                    {
                        "id": f"{row.get('id')}-{rid}-unavailable",
                        "row": row,
                        "region": rid,
                        "providerId": None,
                        "routeProviderId": None,
                        "routeType": None,
                        "regionState": "NOT_AVAILABLE",
                    }
                )
                continue
            for provider_id, route_pid, rtype in _providers_for_region(row, region):
                out.append(
                    {
                        "id": f"{row.get('id')}-{rid}-{provider_id or 'none'}",
                        "row": row,
                        "region": rid,
                        "providerId": provider_id,
                        "routeProviderId": route_pid,
                        "routeType": rtype,
                        "regionState": None,
                    }
                )

    for spec in doc.get("nvSlices") or []:
        row = by_id.get(spec.get("portfolioId"))
        if not row:
            continue
        out.append(
            {
                "id": spec["id"],
                "row": row,
                "region": spec.get("region") or "CA",
                "providerId": spec.get("providerId"),
                "routeProviderId": spec.get("providerId"),
                "routeType": spec.get("routeType") or "DIRECT",
                "accessType": spec.get("accessType"),
                "ts43": bool(spec.get("ts43ClientAvailable", True)),
                "sim": bool(spec.get("simAvailable", True)),
                "showcase": spec.get("showcase"),
            }
        )

    for spec in doc.get("otaSlices") or []:
        row = by_id.get(spec.get("portfolioId"))
        if not row:
            continue
        out.append(
            {
                "id": spec["id"],
                "row": row,
                "region": spec.get("region") or "EU",
                "providerId": spec.get("providerId"),
                "routeProviderId": spec.get("routeProviderId") or spec.get("providerId"),
                "routeType": spec.get("routeType"),
                "qualifiedDemand": spec.get("qualifiedDemand"),
                "servingLabel": spec.get("servingLabel"),
            }
        )
    return out


def evaluate_records(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry) -> list[dict[str, Any]]:
    records = []
    for spec in _slices(store):
        records.append(
            _build_record(
                store,
                graph,
                registry,
                row=spec["row"],
                slice_id=str(spec["id"]),
                region=str(spec["region"]),
                provider_id=spec.get("providerId"),
                route_provider_id=spec.get("routeProviderId"),
                route_type_hint=spec.get("routeType"),
                access_type=spec.get("accessType"),
                ts43=bool(spec.get("ts43", True)),
                sim=bool(spec.get("sim", True)),
                showcase=spec.get("showcase"),
                region_state=spec.get("regionState"),
                qualified_demand=spec.get("qualifiedDemand"),
                serving_label=spec.get("servingLabel"),
            )
        )
    return records


def _summary(records: list[dict[str, Any]], store: ConfigStore) -> dict[str, Any]:
    visible = visible_rows(store)
    configured_ids = {r.get("useCaseId") for r in records if r.get("fulfillmentStatus") != "NOT_CONFIGURED"}
    visible_configured = [v for v in visible if v.get("useCaseId") in configured_ids]
    statuses = [r.get("fulfillmentStatus") for r in records]

    def n(status: str) -> int:
        return sum(1 for s in statuses if s == status)

    return {
        "salesVisibleUseCases": len(visible),
        "configuredFulfillmentCoverage": len(visible_configured),
        "records": len(records),
        "fullyFulfillable": n("FULFILLABLE") + n("FULFILLABLE_WITH_REDUCED_EVIDENCE"),
        "partial": n("PARTIALLY_FULFILLABLE"),
        "blocked": n("BLOCKED"),
        "notAvailable": n("NOT_AVAILABLE"),
        "unknown": n("NOT_CONFIGURED"),
        "note": "Counts are derived from configuration. Not hardcoded.",
        "source": "DERIVED",
    }


def _rank(status: str | None) -> int:
    order = {
        "BLOCKED": 0,
        "NOT_AVAILABLE": 1,
        "PARTIALLY_FULFILLABLE": 2,
        "FULFILLABLE_WITH_REDUCED_EVIDENCE": 3,
        "FULFILLABLE": 4,
        "NOT_CONFIGURED": 5,
        "NOT_APPLICABLE": 6,
    }
    return order.get(str(status or ""), 9)


def _matrix(records: list[dict[str, Any]], store: ConfigStore) -> list[dict[str, Any]]:
    doc = coverage_doc(store)
    regions = list(doc.get("canonicalMatrixRegions") or ["CA", "DE", "SG"])
    apps: dict[tuple[str, str], dict[str, Any]] = {}
    for rec in records:
        key = (str(rec.get("enterpriseId")), str(rec.get("applicationId")))
        apps.setdefault(
            key,
            {
                "enterpriseId": rec.get("enterpriseId"),
                "enterpriseLabel": rec.get("enterpriseLabel"),
                "applicationId": rec.get("applicationId"),
                "applicationLabel": rec.get("applicationLabel"),
                "intents": {},
            },
        )
        intent_id = str(rec.get("intentId"))
        intent = apps[key]["intents"].setdefault(
            intent_id,
            {"intentId": intent_id, "intentLabel": rec.get("intentLabel"), "useCaseId": rec.get("useCaseId"), "cells": {}},
        )
        cell_key = str(rec.get("region"))
        prev = intent["cells"].get(cell_key)
        if not prev or _rank(rec.get("fulfillmentStatus")) < _rank(prev.get("fulfillmentStatus")):
            intent["cells"][cell_key] = {
                "region": rec.get("region"),
                "fulfillmentStatus": rec.get("fulfillmentStatus"),
                "recordId": rec.get("id"),
                "providerLabel": rec.get("providerLabel"),
                "route": rec.get("route"),
            }
    out = []
    for app in apps.values():
        intents = []
        for intent in app["intents"].values():
            cells = []
            for region in regions:
                cell = intent["cells"].get(region)
                if cell:
                    cells.append(cell)
                else:
                    cells.append(
                        {
                            "region": region,
                            "fulfillmentStatus": "NOT_CONFIGURED",
                            "recordId": None,
                            "note": "Operator availability is not configured for this region. Not BLOCKED.",
                        }
                    )
            intents.append({**intent, "cells": cells})
        out.append({**app, "intents": intents, "regions": regions})
    return out


def _supply(records: list[dict[str, Any]], store: ConfigStore) -> list[dict[str, Any]]:
    out = []
    for provider in store.providers:
        pid = str(provider.get("id"))
        hits = [r for r in records if r.get("provider") == pid or r.get("routeProvider") == pid]
        ops = sorted(_provider_ops(store, pid))
        enabled_intents = []
        seen = set()
        for rec in hits:
            intent_id = rec.get("intentId")
            key = (intent_id, rec.get("applicationId"), rec.get("region"))
            if key in seen or rec.get("fulfillmentStatus") == "NOT_CONFIGURED":
                continue
            seen.add(key)
            enabled_intents.append(
                {
                    "intentId": intent_id,
                    "intentLabel": rec.get("intentLabel"),
                    "applicationId": rec.get("applicationId"),
                    "applicationLabel": rec.get("applicationLabel"),
                    "enterpriseLabel": rec.get("enterpriseLabel"),
                    "industry": rec.get("industry"),
                    "industryLabel": rec.get("industryLabel"),
                    "fulfillmentStatus": rec.get("fulfillmentStatus"),
                    "region": rec.get("region"),
                    "recordId": rec.get("id"),
                }
            )
        out.append(
            {
                "id": pid,
                "label": provider.get("audienceLabel") or provider.get("label"),
                "kind": provider.get("kind"),
                "providerType": _provider_type(store, pid),
                "operations": ops,
                "records": [r.get("id") for r in hits],
                "intentsEnabled": enabled_intents,
                "industries": sorted({i.get("industry") for i in enabled_intents if i.get("industry")}),
                "doesNotOwnApis": provider.get("kind") == "aggregator",
                "aggregatorNote": (
                    "Aggregator A normalizes and routes. It does not own the operator APIs it routes to."
                    if provider.get("kind") == "aggregator"
                    else None
                ),
                "coverageGaps": [
                    {
                        "code": g.get("code"),
                        "intentId": rec.get("intentId"),
                        "region": rec.get("region"),
                        "detail": g.get("detail"),
                    }
                    for rec in hits
                    for g in rec.get("blockingGaps") or []
                ],
            }
        )
    return out


def _capability_index(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_cap: dict[str, dict[str, Any]] = {}
    for rec in records:
        for cap in rec.get("capabilities") or []:
            cid = str(cap.get("id"))
            bucket = by_cap.setdefault(
                cid,
                {
                    "id": cid,
                    "label": cap.get("label"),
                    "familyId": cap.get("familyId"),
                    "operationId": cap.get("operationId"),
                    "providers": [],
                    "intents": [],
                    "routes": [],
                },
            )
            bucket["providers"].append(
                {
                    "providerId": rec.get("routeProvider") or rec.get("provider"),
                    "providerLabel": rec.get("routeProviderLabel") or rec.get("providerLabel"),
                    "region": rec.get("region"),
                    "regionLabel": rec.get("regionLabel"),
                    "route": cap.get("route") or rec.get("route"),
                    "available": cap.get("available"),
                    "ready": cap.get("ready"),
                    "fulfillable": cap.get("fulfillable"),
                    "recordId": rec.get("id"),
                }
            )
            intent = {
                "intentId": rec.get("intentId"),
                "intentLabel": rec.get("intentLabel"),
                "enterpriseLabel": rec.get("enterpriseLabel"),
                "applicationLabel": rec.get("applicationLabel"),
                "maturity": rec.get("maturity"),
                "useCaseId": rec.get("useCaseId"),
                "enterpriseId": rec.get("enterpriseId"),
            }
            if intent not in bucket["intents"]:
                bucket["intents"].append(intent)
            if cap.get("route"):
                route = {
                    "route": cap.get("route"),
                    "routeId": cap.get("routeId"),
                    "providerLabel": rec.get("routeProviderLabel"),
                }
                if route not in bucket["routes"]:
                    bucket["routes"].append(route)
    return list(by_cap.values())


def public_coverage(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry) -> dict[str, Any]:
    doc = coverage_doc(store)
    records = evaluate_records(store, graph, registry)
    return {
        "headline": "Fulfillment Coverage",
        "question": "Can NetAware actually fulfill this Intent in this region, for this application, through the available operator / aggregator supply?",
        "notDemandMap": True,
        "notRevenue": True,
        "honesty": str(doc.get("honesty") or "").strip(),
        "states": list(doc.get("states") or STATES),
        "gapClasses": list(doc.get("gapClasses") or GAP_CODES),
        "distinctions": doc.get("distinctions")
        or {
            "telcoFinder": "Which network/operator applies to this subject?",
            "apiFinder": "Which candidate Network API operations are available through which providers?",
            "fulfillmentCoverage": "Given the Intent, governance, required capabilities, operator readiness and routes, can the business need actually be fulfilled?",
        },
        "chain": [
            "DEMAND · Enterprise / Application / Intent",
            "REQUIREMENTS · Capabilities / governance",
            "SUPPLY · Region / operator / aggregator / API",
            "READINESS · Prerequisites / route",
            "FULFILLMENT",
        ],
        "summary": _summary(records, store),
        "records": records,
        "matrix": _matrix(records, store),
        "providers": _supply(records, store),
        "capabilities": _capability_index(records),
        "industries": [
            {
                "id": ind.get("id"),
                "label": ind.get("label"),
                "useCases": [r.get("id") for r in visible_rows(store) if r.get("industry") == ind.get("id")],
                "configuredRegions": sorted(
                    {
                        rec.get("region")
                        for rec in records
                        if rec.get("industry") == ind.get("id") and rec.get("fulfillmentStatus") != "NOT_CONFIGURED"
                    }
                ),
                "coverage": [
                    {
                        "intentId": rec.get("intentId"),
                        "region": rec.get("region"),
                        "status": rec.get("fulfillmentStatus"),
                        "recordId": rec.get("id"),
                    }
                    for rec in records
                    if rec.get("industry") == ind.get("id")
                ],
            }
            for ind in ((store.sales_portfolio or {}).get("industries") or [])
        ],
        "ecs": doc.get("ecs")
        or {"kind": "OPERATOR_PREREQUISITE", "label": "CONFIGURED OPERATOR READINESS", "notACamaraApi": True},
        "source": "DERIVED",
    }


def record_by_id(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry, record_id: str) -> dict[str, Any] | None:
    for rec in evaluate_records(store, graph, registry):
        if rec.get("id") == record_id:
            return rec
    return None


def coverage_for_enterprise(payload: dict[str, Any], enterprise_id: str) -> dict[str, Any]:
    records = [r for r in payload.get("records") or [] if r.get("enterpriseId") == enterprise_id]
    return {
        **payload,
        "records": records,
        "matrix": [m for m in payload.get("matrix") or [] if m.get("enterpriseId") == enterprise_id],
    }


def coverage_for_intent(payload: dict[str, Any], intent_id: str) -> dict[str, Any]:
    records = [r for r in payload.get("records") or [] if r.get("intentId") == intent_id]
    return {**payload, "records": records}


def coverage_for_provider(payload: dict[str, Any], provider_id: str) -> dict[str, Any]:
    providers = [p for p in payload.get("providers") or [] if p.get("id") == provider_id]
    records = [
        r for r in payload.get("records") or [] if r.get("provider") == provider_id or r.get("routeProvider") == provider_id
    ]
    return {**payload, "providers": providers, "records": records}


def coverage_for_capability(payload: dict[str, Any], capability_id: str) -> dict[str, Any]:
    caps = [c for c in payload.get("capabilities") or [] if c.get("id") == capability_id]
    records = [
        r
        for r in payload.get("records") or []
        if capability_id
        in (r.get("requiredCapabilities") or []) + (r.get("optionalCapabilities") or []) + (r.get("conditionalCapabilities") or [])
    ]
    return {**payload, "capabilities": caps, "records": records, "routeExplorer": caps[0] if caps else None}


def validate_record_schema(record: dict[str, Any]) -> None:
    schema = json.loads(fulfillment_schema_path().read_text(encoding="utf-8"))
    required = schema.get("required") or []
    for key in required:
        if key not in record:
            raise ValueError(f"Fulfillment record missing {key}")
    allowed = schema["properties"]["fulfillmentStatus"]["enum"]
    if record.get("fulfillmentStatus") not in allowed:
        raise ValueError(f"Invalid fulfillmentStatus {record.get('fulfillmentStatus')}")
    if "revenue" in record or "opportunityScore" in record or "tam" in record:
        raise ValueError("Commercial fields are not allowed on fulfillment records")


