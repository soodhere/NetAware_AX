"""Cadence 14 — Demand Map. Consumes C13 fulfillment. Not a second coverage engine. Not revenue."""
from __future__ import annotations

import json
from typing import Any

from .config import SCHEMAS_DIR
from .fulfillment import public_coverage
from .graph import KnowledgeGraph
from .model import ConfigStore
from .portfolio import row_by_use_case, visible_rows
from .registry import CatalogRegistry

DEMAND_STATES = (
    "POTENTIAL",
    "QUALIFIED",
    "FULFILLED",
    "PARTIALLY_FULFILLED",
    "UNFULFILLED",
    "NOT_REQUIRED",
)

QUALIFIED_STATES = {"QUALIFIED", "FULFILLED", "PARTIALLY_FULFILLED", "UNFULFILLED"}


def demand_schema_path():
    return SCHEMAS_DIR / "demand-record.json"


def demand_doc(store: ConfigStore) -> dict[str, Any]:
    return store.demand_map or {}


def _contextual(store: ConfigStore, intent_id: str, cap_id: str) -> dict[str, Any] | None:
    for row in demand_doc(store).get("contextualDemand") or []:
        if row.get("intentId") == intent_id and row.get("capabilityId") == cap_id:
            return row
    return None


def _portfolio_row(store: ConfigStore, rec: dict[str, Any]) -> dict[str, Any]:
    return row_by_use_case(store, str(rec.get("enterpriseId") or ""), str(rec.get("useCaseId") or "")) or {}


def _in_minimum(rec: dict[str, Any], cap: dict[str, Any]) -> bool:
    cap_id = str(cap.get("id") or "")
    if cap_id in (rec.get("minimumSufficientSet") or []):
        return True
    return cap.get("role") == "REQUIRED"


def _demand_state(rec: dict[str, Any], cap: dict[str, Any], store: ConfigStore) -> str:
    cap_id = str(cap.get("id") or "")
    ctx = _contextual(store, str(rec.get("intentId") or ""), cap_id)
    if ctx and ctx.get("initially") == "NOT_REQUIRED" and not _in_minimum(rec, cap):
        return "NOT_REQUIRED"
    if not _in_minimum(rec, cap) and cap.get("role") in {"OPTIONAL", "CONDITIONAL"}:
        return "NOT_REQUIRED"
    maturity = str(rec.get("maturity") or "")
    fstatus = str(rec.get("fulfillmentStatus") or "")
    if maturity == "EXPLORE" or fstatus == "NOT_CONFIGURED":
        return "POTENTIAL"
    if fstatus in {"FULFILLABLE", "FULFILLABLE_WITH_REDUCED_EVIDENCE"}:
        return "FULFILLED"
    if fstatus == "PARTIALLY_FULFILLABLE":
        if cap.get("fulfillable") == "YES":
            return "FULFILLED"
        return "PARTIALLY_FULFILLED"
    if fstatus in {"BLOCKED", "NOT_AVAILABLE"}:
        return "UNFULFILLED"
    return "POTENTIAL"


def _invocation_note(state: str, rec: dict[str, Any], cap: dict[str, Any]) -> str:
    if rec.get("intentId") == "ensure_baggage_connection" and state == "FULFILLED":
        return "Qualified demand is fulfilled when NetAware can obtain the evidence. A negative DATA-reachability result is still successful fulfillment — not a supply failure."
    if state == "NOT_REQUIRED":
        return "Qualified demand does not necessarily produce an API invocation. This capability is NOT REQUIRED after evaluation."
    if state == "POTENTIAL":
        return "Mapping exists. This is not configured qualified demand and is not an invocation."
    if state == "UNFULFILLED":
        return "Qualified demand exists. No available supply / readiness / governance path, so there is no invocation."
    if rec.get("intentId") == "assess_recovery_continuity":
        return "Evidence reuse can satisfy qualified demand without a new Network API invocation."
    if any(g.get("code") == "CONSENT_MISSING" for g in cap.get("gaps") or []):
        return "Consent/policy can prevent invocation even when the API is available."
    return "Qualified demand is not the same as an API invocation."


def _from_capability(store: ConfigStore, rec: dict[str, Any], cap: dict[str, Any]) -> dict[str, Any]:
    port = _portfolio_row(store, rec)
    state = _demand_state(rec, cap, store)
    cap_id = str(cap.get("id") or "")
    qd = rec.get("qualifiedDemand") or {}
    units = None
    units_label = None
    if qd.get("unfulfilledCount") and qd.get("capabilityId") == cap_id and state in {"UNFULFILLED", "PARTIALLY_FULFILLED"}:
        units = qd.get("unfulfilledCount")
        units_label = f"{units} simulated {qd.get('unit') or 'units'} — SIMULATED QUALIFIED DEMAND, not lost API sales."
    blocking = None
    if state in {"UNFULFILLED", "PARTIALLY_FULFILLED"}:
        for gap in cap.get("gaps") or rec.get("blockingGaps") or []:
            blocking = gap.get("code")
            break
    ctx = _contextual(store, str(rec.get("intentId") or ""), cap_id)
    provenance = list(rec.get("provenance") or []) + [{"fact": f"Demand state {state} for {cap_id}", "source": "DERIVED"}]
    if ctx:
        provenance.append({"fact": ctx.get("note"), "source": ctx.get("source") or "RUNTIME"})
    source = "INTENT PROFILE"
    if rec.get("maturity") == "GUIDED":
        source = "GUIDED SCENARIO"
    if rec.get("maturity") == "EXPLORE":
        source = "CONFIGURED APPLICATION"
    if units:
        source = "SIMULATED FLEET"
    return {
        "demandId": f"{rec.get('id')}::{cap_id}",
        "enterpriseId": rec.get("enterpriseId"),
        "enterpriseLabel": rec.get("enterpriseLabel"),
        "applicationId": rec.get("applicationId"),
        "applicationLabel": rec.get("applicationLabel"),
        "useCaseId": rec.get("useCaseId"),
        "intentId": rec.get("intentId"),
        "intentLabel": rec.get("intentLabel"),
        "businessEvent": port.get("businessProblem") or rec.get("intentLabel"),
        "decisionGap": port.get("decisionGap") or rec.get("intentLabel"),
        "commercialMotion": list(port.get("commercialMotion") or []),
        "industry": rec.get("industry"),
        "industryLabel": rec.get("industryLabel"),
        "region": rec.get("region"),
        "regionLabel": rec.get("regionLabel"),
        "capability": cap_id,
        "capabilityLabel": cap.get("label") or cap_id,
        "requirementType": cap.get("role") or "UNKNOWN",
        "demandState": state,
        "qualified": state in QUALIFIED_STATES,
        "potential": state == "POTENTIAL",
        "invoked": False,
        "invocationNote": _invocation_note(state, rec, cap),
        "fulfillmentStatus": rec.get("fulfillmentStatus"),
        "provider": rec.get("provider"),
        "providerLabel": rec.get("providerLabel"),
        "providerType": rec.get("providerType"),
        "route": rec.get("route"),
        "routeProvider": rec.get("routeProvider"),
        "routeProviderLabel": rec.get("routeProviderLabel"),
        "blockingGap": blocking,
        "affectedUnits": units,
        "affectedUnitsLabel": units_label,
        "source": source,
        "provenance": provenance,
        "coverageRecordId": rec.get("id"),
        "coverageHref": rec.get("coverageHref") or f"/coverage/record/{rec.get('id')}",
        "portfolioHref": rec.get("portfolioHref"),
        "maturity": rec.get("maturity"),
        "accessType": rec.get("accessType"),
        "selectedPath": rec.get("selectedPath"),
        "contextualDemand": ctx,
        "fulfillmentVsOutcome": rec.get("fulfillmentVsOutcome") if cap_id == "device_reachability" else None,
        "familyId": cap.get("familyId"),
        "operationId": cap.get("operationId"),
        "notRevenue": True,
        "configuredDemoPortfolio": True,
    }


def _enablement(demands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    nv_b = next(
        (
            d
            for d in demands
            if d.get("coverageRecordId") == "nv-wifi-provider-b" and d.get("capability") == "number_possession_verification"
        ),
        None,
    )
    if nv_b:
        out.append(
            {
                "id": "enable-ecs-provider-b",
                "gap": "ENTITLEMENT_SERVER_UNAVAILABLE",
                "label": "Entitlement Server readiness",
                "providerId": "simulated-operator-b",
                "providerLabel": "Network Provider B",
                "prevents": "NV2 fulfillment blocked over Wi-Fi",
                "affectedIntent": "verify_mobile_number",
                "affectedApplication": nv_b.get("applicationLabel"),
                "affectedMotion": "IDENTITY_AND_TRUST",
                "ifEnabled": {
                    "from": "UNFULFILLED",
                    "to": "FULFILLED",
                    "note": "Exposing the API is not always enough. The fulfillment path must also be operationally ready.",
                },
                "kind": "FULFILLMENT IMPACT",
                "notRevenue": True,
            }
        )
    ota_c = next(
        (d for d in demands if d.get("coverageRecordId") == "ota-provider-c" and d.get("capability") == "roaming_status"),
        None,
    )
    if ota_c:
        out.append(
            {
                "id": "enable-roaming-provider-c",
                "gap": "CAPABILITY_GAP",
                "label": "Enable Roaming Status for Network Provider C",
                "providerId": "simulated-provider-c",
                "providerLabel": ota_c.get("providerLabel"),
                "prevents": "OTA campaign cannot fully qualify the roaming-required cohort",
                "affectedIntent": "prepare_ota_cohort",
                "affectedApplication": ota_c.get("applicationLabel"),
                "affectedMotion": "DEVICE_AND_FLEET_OPERATIONS",
                "affectedUnits": ota_c.get("affectedUnits"),
                "affectedUnitsLabel": ota_c.get("affectedUnitsLabel"),
                "ifEnabled": {
                    "from": "PARTIALLY_FULFILLABLE",
                    "to": "FULFILLABLE",
                    "note": "500-device simulated cohort gap removed. Fulfillment impact, not revenue impact.",
                },
                "kind": "FULFILLMENT IMPACT",
                "notRevenue": True,
            }
        )
    return out


def _operator_enablement(coverage: dict[str, Any], demands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for provider in coverage.get("providers") or []:
        hits = [d for d in demands if d.get("provider") == provider.get("id") or d.get("routeProvider") == provider.get("id")]
        ready = sorted({d.get("capabilityLabel") for d in hits if d.get("demandState") == "FULFILLED" and d.get("capabilityLabel")})
        gaps = []
        seen = set()
        for d in hits:
            key = (d.get("blockingGap"), d.get("capability"))
            if d.get("demandState") in {"UNFULFILLED", "PARTIALLY_FULFILLED"} and d.get("blockingGap") and key not in seen:
                seen.add(key)
                gaps.append(
                    {
                        "gap": d.get("blockingGap"),
                        "capability": d.get("capabilityLabel"),
                        "intentId": d.get("intentId"),
                        "unlocks": "Additional configured demand would become fulfillable.",
                    }
                )
        out.append(
            {
                "id": provider.get("id"),
                "label": provider.get("label"),
                "providerType": provider.get("providerType"),
                "currentlyReady": ready,
                "gaps": gaps,
                "fulfillsIntents": len({d.get("intentId") for d in hits if d.get("demandState") == "FULFILLED"}),
                "fulfillsApplications": len({d.get("applicationId") for d in hits if d.get("demandState") == "FULFILLED"}),
                "fulfillsIndustries": len({d.get("industry") for d in hits if d.get("demandState") == "FULFILLED" and d.get("industry")}),
                "note": "CONFIGURED DEMO PORTFOLIO. Not actual commercial customer counts.",
                "doesNotOwnApis": provider.get("doesNotOwnApis"),
                "aggregatorNote": provider.get("aggregatorNote"),
                "regions": sorted({d.get("region") for d in hits if d.get("region")}),
                "wording": "AVAILABLE VIA / ROUTED THROUGH / NORMALIZED THROUGH" if provider.get("doesNotOwnApis") else "DIRECT",
            }
        )
    return out


def _capability_leverage(demands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_cap: dict[str, dict[str, Any]] = {}
    for d in demands:
        cid = str(d.get("capability"))
        bucket = by_cap.setdefault(
            cid,
            {
                "id": cid,
                "label": d.get("capabilityLabel"),
                "familyId": d.get("familyId"),
                "operationId": d.get("operationId"),
                "intents": [],
                "applications": [],
                "enterprises": [],
                "industries": [],
                "regions": [],
                "providers": [],
            },
        )
        intent = {
            "id": d.get("intentId"),
            "label": d.get("intentLabel"),
            "maturity": d.get("maturity"),
            "demandState": d.get("demandState"),
            "enterpriseLabel": d.get("enterpriseLabel"),
            "applicationLabel": d.get("applicationLabel"),
            "demandId": d.get("demandId"),
        }
        if intent not in bucket["intents"]:
            bucket["intents"].append(intent)
        app = {"id": d.get("applicationId"), "label": d.get("applicationLabel"), "maturity": d.get("maturity")}
        if app not in bucket["applications"]:
            bucket["applications"].append(app)
        ent = {"id": d.get("enterpriseId"), "label": d.get("enterpriseLabel")}
        if ent not in bucket["enterprises"]:
            bucket["enterprises"].append(ent)
        ind = {"id": d.get("industry"), "label": d.get("industryLabel")}
        if ind not in bucket["industries"]:
            bucket["industries"].append(ind)
        if d.get("region") and d.get("region") not in bucket["regions"]:
            bucket["regions"].append(d.get("region"))
        pl = d.get("routeProviderLabel") or d.get("providerLabel")
        if pl and pl not in bucket["providers"]:
            bucket["providers"].append(pl)
    return [
        {
            **bucket,
            "industriesReached": len({i.get("id") for i in bucket["industries"] if i.get("id")}),
            "applicationsReached": len({a.get("id") for a in bucket["applications"] if a.get("id")}),
            "intentsReached": len({i.get("id") for i in bucket["intents"] if i.get("id")}),
            "note": "ONE NETWORK CAPABILITY CAN SERVE MULTIPLE ENTERPRISE APPLICATIONS. No dollar value.",
        }
        for bucket in by_cap.values()
    ]


def public_demand(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry) -> dict[str, Any]:
    coverage = public_coverage(store, graph, registry)
    demands: list[dict[str, Any]] = []
    for rec in coverage.get("records") or []:
        caps = rec.get("capabilities") or []
        if not caps:
            port = _portfolio_row(store, rec)
            for cap_id in port.get("capabilities") or []:
                cap_row = store.capability_by_id.get(str(cap_id)) or {"id": cap_id, "label": cap_id}
                demands.append(
                    _from_capability(
                        store,
                        rec,
                        {
                            "id": cap_row.get("id") or cap_id,
                            "label": cap_row.get("label") or cap_id,
                            "role": "REQUIRED",
                            "gaps": [],
                            "fulfillable": "NO",
                        },
                    )
                )
            continue
        for cap in caps:
            demands.append(_from_capability(store, rec, cap))
    doc = demand_doc(store)
    motions = (store.sales_portfolio or {}).get("motions") or []
    industries = (store.sales_portfolio or {}).get("industries") or []

    def n(state: str) -> int:
        return sum(1 for d in demands if d.get("demandState") == state)

    summary = {
        "visibleUseCases": len(visible_rows(store)),
        "configuredApplications": len({d.get("applicationId") for d in demands if d.get("applicationId")}),
        "qualifiedCapabilityDemands": sum(1 for d in demands if d.get("qualified")),
        "fulfilledDemands": n("FULFILLED"),
        "partialDemands": n("PARTIALLY_FULFILLED"),
        "unfulfilledDemands": n("UNFULFILLED"),
        "potentialDemands": n("POTENTIAL"),
        "notRequired": n("NOT_REQUIRED"),
        "regions": len({d.get("region") for d in demands if d.get("region")}),
        "providers": len({d.get("provider") for d in demands if d.get("provider")}),
        "aggregatedRoutes": sum(1 for d in demands if d.get("route") == "AGGREGATED"),
        "note": "Counts are derived from configured demo data. Not hardcoded marketing numbers. Not customer counts.",
        "source": "DERIVED",
        "coverageSummary": coverage.get("summary"),
    }
    families = []
    for fam in registry.families:
        fid = str(fam.get("id"))
        related = [d for d in demands if d.get("familyId") == fid]
        families.append(
            {
                "id": fid,
                "label": fam.get("label"),
                "intents": sorted({d.get("intentId") for d in related if d.get("intentId")}),
                "applications": sorted({d.get("applicationLabel") for d in related if d.get("applicationLabel")}),
                "industries": sorted({d.get("industryLabel") for d in related if d.get("industryLabel")}),
            }
        )
    return {
        "headline": "Demand Map",
        "question": "Where is network API demand?",
        "notRevenue": True,
        "notTam": True,
        "notForecast": True,
        "consumesCoverage": True,
        "honesty": str(doc.get("honesty") or "").strip(),
        "configuredDemoCoverage": True,
        "states": list(DEMAND_STATES),
        "whyNetAware": doc.get("whyNetAware") or {},
        "demoStory": doc.get("demoStory") or [],
        "language": doc.get("language") or {},
        "notInvocationReasons": doc.get("notInvocationReasons") or [],
        "summary": summary,
        "records": demands,
        "enablement": _enablement(demands),
        "operators": _operator_enablement(coverage, demands),
        "capabilityLeverage": _capability_leverage(demands),
        "familyLeverage": families,
        "motions": [{**m, "count": sum(1 for d in demands if m.get("id") in (d.get("commercialMotion") or []))} for m in motions],
        "industries": [
            {
                **ind,
                "applications": sorted({d.get("applicationLabel") for d in demands if d.get("industry") == ind.get("id") and d.get("applicationLabel")}),
                "intents": sorted({d.get("intentId") for d in demands if d.get("industry") == ind.get("id")}),
            }
            for ind in industries
        ],
        "regions": [
            {
                "id": rid,
                "label": label,
                "note": "CONFIGURED DEMO COVERAGE. Not actual market-wide country statistics.",
            }
            for rid, label in (("CA", "Canada"), ("DE", "Germany"), ("SG", "Singapore"))
        ],
        "source": "DERIVED",
        "coverageHref": "/coverage",
    }


def demand_for(payload: dict[str, Any], **filters: str) -> dict[str, Any]:
    records = payload.get("records") or []
    for key, val in filters.items():
        if not val:
            continue
        records = [r for r in records if str(r.get(key) or "") == val]
    return {**payload, "records": records}


def validate_demand_schema(record: dict[str, Any]) -> None:
    schema = json.loads(demand_schema_path().read_text(encoding="utf-8"))
    for key in schema.get("required") or []:
        if key not in record:
            raise ValueError(f"Demand record missing {key}")
    if record.get("demandState") not in schema["properties"]["demandState"]["enum"]:
        raise ValueError(f"Invalid demandState {record.get('demandState')}")
    for banned in ("revenue", "price", "ARR", "tam", "opportunityScore"):
        if banned in record:
            raise ValueError("Commercial forecast fields are not allowed on demand records")

