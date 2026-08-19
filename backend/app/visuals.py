"""Cadence 17 — visual intelligence over existing C12–C16 truth.

Presentation only. Does not add mappings, scenarios, families, or a second engine.
"""
from __future__ import annotations

from typing import Any

from .demand import public_demand
from .explore_meta import CAPABILITY_LIVE_BEHAVIOR
from .fulfillment import public_coverage
from .graph import KnowledgeGraph
from .model import ConfigStore
from .portfolio import visible_rows
from .registry import CatalogRegistry
from .runtime import _family_for

REGION_LABELS = {"CA": "Canada", "DE": "Germany", "SG": "Singapore", "EU": "Europe"}

GRAMMAR = [
    {"id": "POTENTIAL", "meaning": "could apply from the configured mapping"},
    {"id": "CONFIGURED", "meaning": "onboarding / policy knowledge"},
    {"id": "DISCOVERED", "meaning": "runtime network knowledge"},
    {"id": "SELECTED", "meaning": "chosen capability"},
    {"id": "INVOKED", "meaning": "actual network call"},
    {"id": "REUSED", "meaning": "previous evidence"},
    {"id": "SKIPPED", "meaning": "unnecessary"},
    {"id": "FILTERED", "meaning": "governance prevented selection"},
    {"id": "UNAVAILABLE", "meaning": "supply or prerequisite missing"},
    {"id": "VERIFIED", "meaning": "checked against the objective"},
    {"id": "OUTCOME", "meaning": "business result"},
]


def _role_state(role: str | None) -> str | None:
    if role == "required":
        return "REQUIRED"
    if role == "considered":
        return "CONDITIONAL"
    return None


def _live_state(intent_id: str, cap_id: str) -> str | None:
    for row in CAPABILITY_LIVE_BEHAVIOR.get(cap_id) or []:
        if row.get("intentId") == intent_id:
            return str(row.get("state") or "")
    return None


def _family_state(roles: list[str], live: list[str | None]) -> str | None:
    if not roles:
        return None
    if any(s == "BLOCKED_BY_POLICY" for s in live) and "required" not in roles:
        return "FILTERED"
    if "required" in roles:
        return "REQUIRED"
    if "considered" in roles:
        return "CONDITIONAL"
    return None


def _why(state: str, caps: list[dict[str, Any]]) -> str:
    labels = " · ".join(c["label"] for c in caps)
    if state == "REQUIRED":
        return f"{labels} — required for this Intent. Mapping says this family can apply."
    if state == "CONDITIONAL":
        return f"{labels} — considered. AX may skip, reuse, or invoke depending on context."
    if state == "FILTERED":
        return f"{labels} — mapped as potentially relevant, but existing governance prevents selection."
    return labels


def public_map(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry) -> dict[str, Any]:
    rows = visible_rows(store)
    families = [
        {"id": str(fam.get("id")), "label": fam.get("label"), "group": fam.get("familyGroup")}
        for fam in registry.families
    ]
    family_ids = [f["id"] for f in families]
    use_cases = []
    cells: list[dict[str, Any]] = []
    reverse_fam: dict[str, list[dict[str, Any]]] = {fid: [] for fid in family_ids}
    reverse_cap: dict[str, list[dict[str, Any]]] = {}
    enterprises: dict[str, dict[str, Any]] = {}

    for row in rows:
        intent_id = str(row.get("intentId") or "")
        links = list(graph.intent_caps.get(intent_id) or [])
        cap_nodes = []
        family_roles: dict[str, list[str]] = {}
        family_caps: dict[str, list[dict[str, Any]]] = {}
        family_live: dict[str, list[str | None]] = {}
        for link in links:
            cap_id = str(link.get("capabilityId") or "")
            cap = store.capability_by_id.get(cap_id) or {"id": cap_id, "label": cap_id}
            fam = _family_for(registry, cap_id)
            fam_id = str((fam or {}).get("id") or "")
            role = str(link.get("role") or "")
            live = _live_state(intent_id, cap_id)
            node = {
                "id": cap_id,
                "label": cap.get("label") or cap_id,
                "role": role,
                "state": _role_state(role),
                "live": live,
                "familyId": fam_id or None,
                "familyLabel": (fam or {}).get("label"),
            }
            cap_nodes.append(node)
            reverse_cap.setdefault(cap_id, []).append(
                {
                    "useCaseId": row.get("useCaseId"),
                    "useCaseLabel": (store.use_case_by_id.get(str(row.get("useCaseId") or "")) or {}).get("label"),
                    "intentId": intent_id,
                    "enterpriseId": row.get("enterpriseId"),
                    "enterpriseLabel": (store.enterprise_by_id.get(str(row.get("enterpriseId") or "")) or {}).get("label"),
                    "industry": row.get("industry"),
                    "maturity": row.get("scenarioMaturity"),
                    "role": role,
                    "note": "CONFIGURED DEMO USE CASE. Not market demand.",
                }
            )
            if fam_id:
                family_roles.setdefault(fam_id, []).append(role)
                family_caps.setdefault(fam_id, []).append(node)
                family_live.setdefault(fam_id, []).append(live)

        apis = []
        for fam_id, roles in family_roles.items():
            state = _family_state(roles, family_live.get(fam_id) or [])
            if not state:
                continue
            fam_meta = next((f for f in families if f["id"] == fam_id), {"id": fam_id, "label": fam_id})
            why = _why(state, family_caps[fam_id])
            cell = {
                "useCaseId": row.get("useCaseId"),
                "intentId": intent_id,
                "familyId": fam_id,
                "familyLabel": fam_meta.get("label"),
                "state": state,
                "why": why,
                "capabilities": family_caps[fam_id],
                "source": "MAPPINGS + EXISTING LIVE BEHAVIOR",
            }
            cells.append(cell)
            apis.append({"id": fam_id, "label": fam_meta.get("label"), "state": state, "why": why})
            reverse_fam[fam_id].append(
                {
                    "useCaseId": row.get("useCaseId"),
                    "useCaseLabel": (store.use_case_by_id.get(str(row.get("useCaseId") or "")) or {}).get("label"),
                    "intentId": intent_id,
                    "intentLabel": (store.intent_by_id.get(intent_id) or {}).get("label"),
                    "enterpriseId": row.get("enterpriseId"),
                    "enterpriseLabel": (store.enterprise_by_id.get(str(row.get("enterpriseId") or "")) or {}).get("label"),
                    "applicationId": row.get("applicationId"),
                    "applicationLabel": (store.application_by_id.get(str(row.get("applicationId") or "")) or {}).get("label"),
                    "industry": row.get("industry"),
                    "maturity": row.get("scenarioMaturity"),
                    "motion": row.get("commercialMotion"),
                    "state": state,
                    "why": why,
                    "note": "CONFIGURED DEMO USE CASE. Not a customer or TAM claim.",
                }
            )

        uc = store.use_case_by_id.get(str(row.get("useCaseId") or "")) or {}
        intent = store.intent_by_id.get(intent_id) or {}
        ent = store.enterprise_by_id.get(str(row.get("enterpriseId") or "")) or {}
        app = store.application_by_id.get(str(row.get("applicationId") or "")) or {}
        industry_meta = next((i for i in ((store.sales_portfolio or {}).get("industries") or []) if i.get("id") == row.get("industry")), None) or {}
        forward = {
            "id": row.get("id"),
            "industry": row.get("industry"),
            "industryLabel": industry_meta.get("label") or row.get("industry"),
            "enterpriseId": row.get("enterpriseId"),
            "enterpriseLabel": ent.get("label"),
            "applicationId": row.get("applicationId"),
            "applicationLabel": app.get("label"),
            "useCaseId": row.get("useCaseId"),
            "useCaseLabel": uc.get("label"),
            "intentId": intent_id,
            "intentLabel": intent.get("label"),
            "decisionGap": row.get("decisionGap"),
            "businessProblem": row.get("businessProblem"),
            "networkContribution": row.get("networkContribution"),
            "maturity": row.get("scenarioMaturity"),
            "complexity": row.get("scenarioComplexity"),
            "motion": row.get("commercialMotion") or [],
            "chain": [
                row.get("industry"),
                ent.get("label"),
                app.get("label"),
                uc.get("label"),
                intent.get("label") or intent_id,
                "NETWORK DECISION GAP",
                *[c["label"] for c in cap_nodes],
                *[a["label"] for a in apis],
            ],
            "capabilities": cap_nodes,
            "families": apis,
            "href": f"/map/use-case/{row.get('useCaseId')}",
            "demoHref": f"/demo/{row.get('enterpriseId')}/{row.get('useCaseId')}",
        }
        use_cases.append(forward)
        ent_id = str(row.get("enterpriseId") or "")
        bucket = enterprises.setdefault(
            ent_id,
            {
                "id": ent_id,
                "label": ent.get("label"),
                "industry": row.get("industry"),
                "applications": {},
                "sharedCapabilities": {},
            },
        )
        app_id = str(row.get("applicationId") or "")
        app_bucket = bucket["applications"].setdefault(
            app_id,
            {"id": app_id, "label": app.get("label"), "useCases": []},
        )
        app_bucket["useCases"].append(
            {
                "useCaseId": row.get("useCaseId"),
                "useCaseLabel": uc.get("label"),
                "intentId": intent_id,
                "intentLabel": intent.get("label"),
                "decisionGap": row.get("decisionGap"),
                "capabilities": cap_nodes,
                "families": apis,
                "maturity": row.get("scenarioMaturity"),
            }
        )
        for cap in cap_nodes:
            bucket["sharedCapabilities"].setdefault(cap["id"], {"id": cap["id"], "label": cap["label"], "intents": []})
            bucket["sharedCapabilities"][cap["id"]]["intents"].append(intent_id)

    coverage = public_coverage(store, graph, registry)
    demand = public_demand(store, graph, registry)
    heatmap = _heatmap(coverage)
    topology = _topology(coverage, store)
    gaps = demand.get("enablement") or []

    return {
        "headline": "Use Case ↔ Network API Map",
        "question": "Which Network APIs relate to which configured demo use cases — and what does AX determine beyond a static spreadsheet?",
        "presentationOnly": True,
        "doesNotAlterRuntime": True,
        "doesNotAlterCoverage": True,
        "doesNotAlterDemand": True,
        "notIndependentMappingDb": True,
        "consumesPortfolio": True,
        "consumesMappings": True,
        "consumesCoverage": True,
        "consumesDemand": True,
        "honesty": "PRODUCT / DEMO MAPPINGS. Configured demo coverage. Not market-wide applicability. Not live operator inventory.",
        "productStatement": "A static mapping tells you what could apply. NetAware AX determines what should apply, what is permitted, what is available, what is fulfillable, and what should be called now.",
        "grammar": GRAMMAR,
        "families": families,
        "useCases": use_cases,
        "matrix": {
            "rows": [
                {
                    "useCaseId": u["useCaseId"],
                    "label": u["useCaseLabel"],
                    "enterprise": u["enterpriseLabel"],
                    "industry": u["industry"],
                    "motion": u["motion"],
                    "maturity": u["maturity"],
                    "applicationId": u["applicationId"],
                }
                for u in use_cases
            ],
            "columns": families,
            "cells": cells,
            "states": ["REQUIRED", "CONDITIONAL", "FILTERED"],
            "emptyMeans": "NOT RELEVANT — no configured mapping. Not invented.",
            "note": "Not a wall of checkmarks. Empty cells are not relevant. FILTERED uses existing live governance behavior, not a new mapping.",
        },
        "reverseFamilies": [
            {
                "id": fam["id"],
                "label": fam["label"],
                "useCases": reverse_fam.get(fam["id"]) or [],
                "question": "WHERE CAN I ENABLE THIS CAPABILITY?",
                "note": "Configured demo use cases. Not actual customers.",
            }
            for fam in families
        ],
        "reverseCapabilities": [
            {
                "id": cap_id,
                "label": (store.capability_by_id.get(cap_id) or {}).get("label") or cap_id,
                "familyId": str((_family_for(registry, cap_id) or {}).get("id") or ""),
                "useCases": hits,
            }
            for cap_id, hits in reverse_cap.items()
        ],
        "enterprises": [
            {
                **{k: v for k, v in ent.items() if k != "applications" and k != "sharedCapabilities"},
                "applications": list(ent["applications"].values()),
                "sharedCapabilities": list(ent["sharedCapabilities"].values()),
                "leverage": "ONE ENTERPRISE. MULTIPLE APPLICATIONS. MULTIPLE INTENTS. REUSABLE NETWORK CAPABILITIES.",
            }
            for ent in enterprises.values()
        ],
        "staticToAx": {
            "static": ["USE CASE", "INTENT", "POTENTIALLY RELEVANT CAPABILITIES"],
            "ax": ["GOVERNANCE", "RUNTIME FEASIBILITY", "FULFILLMENT", "SELECTED NETWORK APIs"],
            "line": "Static mapping says what could apply. AX operationalizes what should apply now.",
            "notDisparagingSpreadsheets": True,
        },
        "finderDistinction": {
            "telcoFinder": "Which network/operator applies?",
            "apiFinder": "Which relevant Network APIs are available through which providers?",
            "fulfillment": "Can the Intent actually be satisfied given governance, readiness, required capabilities and route?",
        },
        "topology": topology,
        "heatmap": heatmap,
        "supplyGaps": gaps,
        "dxAx": {
            "dx": [
                "Application developer",
                "discover APIs",
                "choose API",
                "understand operator differences",
                "implement flow",
                "handle availability",
                "invoke API",
            ],
            "ax": [
                "Application / authorized agent",
                "express Intent",
                "NetAware discovers capabilities",
                "governs",
                "resolves operator / provider",
                "selects fulfillment",
                "CALL / REUSE / SKIP / FILTER",
                "business outcome",
            ],
            "footer": "AX BUILDS ON NETWORK API DX. IT DOES NOT REPLACE IT.",
        },
        "agentic": {
            "chain": [
                "APPLICATION / AUTHORIZED AGENT",
                "INTENT",
                "CONTEXT",
                "PLAN",
                "DISCOVER",
                "GOVERN",
                "SELECT TOOLS",
                "ACT / REUSE / SKIP",
                "OBSERVE",
                "REPLAN IF NEEDED",
                "VERIFY",
                "OUTCOME",
            ],
            "proofs": [
                "Rocket Bank: selective evidence",
                "NV: runtime fulfillment path selection",
                "High Flight: network evidence + bounded enterprise action",
                "Acme Inspection: closed-loop action + verification",
                "CityCare: governed minimization",
                "OTA: fleet-level orchestration",
            ],
            "note": "Deterministic configured behavior. No LLM theater. No MCP/A2A.",
        },
        "configuredVsRuntime": {
            "configured": [
                "ENTERPRISE",
                "APPLICATION",
                "AGENT",
                "ALLOWED INTENTS",
                "PURPOSE",
                "REGIONS",
                "SUBSCRIPTIONS",
                "ENTITLEMENTS",
                "POLICY",
                "AGREEMENTS / DPA",
                "CONSENT REQUIREMENTS",
                "AUTONOMY",
            ],
            "runtime": [
                "SUBJECT",
                "ACCESS CONTEXT",
                "OPERATOR",
                "API AVAILABILITY",
                "PROVIDER / ROUTE",
                "EVIDENCE",
                "USEFULNESS",
            ],
        },
        "provenanceBadges": [
            "ONBOARDING",
            "CONFIGURATION",
            "INTENT PROFILE",
            "POLICY",
            "RUNTIME",
            "OPERATOR READINESS",
            "SIMULATED PROVIDER DATA",
            "SIMULATED ENTERPRISE DATA",
            "DERIVED",
        ],
        "closeVisual": {
            "left": {
                "title": "ENTERPRISE DEMAND",
                "items": ["Industries", "Applications", "Business events", "Intents", "Decision gaps"],
            },
            "center": {
                "title": "NETAWARE AX",
                "items": ["Intent understanding", "Capability discovery", "Governance", "Fulfillment", "Orchestration", "Verification"],
            },
            "right": {
                "title": "NETWORK SUPPLY",
                "items": ["Operators", "Aggregators", "Regions", "Network capabilities", "CAMARA APIs"],
            },
            "outcome": "BUSINESS OUTCOMES",
            "line": "NETAWARE CONNECTS ENTERPRISE DEMAND TO NETWORK SUPPLY.",
        },
        "counts": {
            "useCases": len(use_cases),
            "industries": len({u["industry"] for u in use_cases}),
            "families": len(families),
            "cells": len(cells),
        },
        "filters": {
            "industries": (store.sales_portfolio or {}).get("industries") or [],
            "motions": (store.sales_portfolio or {}).get("motions") or [],
            "maturities": ["LIVE", "GUIDED", "EXPLORE"],
        },
        "coverageSource": "C13",
        "demandSource": "C14",
    }


def _heatmap(coverage: dict[str, Any]) -> dict[str, Any]:
    records = coverage.get("records") or []
    providers = []
    seen_p: set[str] = set()
    intents = []
    seen_i: set[str] = set()
    cells = []
    for rec in records:
        pid = str(rec.get("provider") or "")
        iid = str(rec.get("intentId") or "")
        if pid and pid not in seen_p:
            seen_p.add(pid)
            providers.append({"id": pid, "label": rec.get("providerLabel") or pid, "kind": rec.get("providerType")})
        if iid and iid not in seen_i:
            seen_i.add(iid)
            intents.append(
                {
                    "id": iid,
                    "label": rec.get("intentLabel") or iid,
                    "application": rec.get("applicationLabel"),
                    "enterprise": rec.get("enterpriseLabel"),
                }
            )
        gaps = rec.get("blockingGaps") or []
        gap0 = gaps[0] if gaps else {}
        cells.append(
            {
                "intentId": iid,
                "providerId": pid,
                "region": rec.get("region"),
                "regionLabel": rec.get("regionLabel") or REGION_LABELS.get(str(rec.get("region") or ""), rec.get("region")),
                "status": rec.get("fulfillmentStatus"),
                "recordId": rec.get("id"),
                "accessType": rec.get("accessType"),
                "selectedPath": rec.get("selectedPath"),
                "route": rec.get("route"),
                "why": gap0.get("detail") or gap0.get("code") or rec.get("fulfillmentStatus"),
                "blockingGap": gap0.get("code"),
                "nvApi": rec.get("apiAvailability"),
                "operatorReadiness": rec.get("operatorReadiness"),
            }
        )
    return {
        "question": "Can this Intent be fulfilled through this provider / region?",
        "intents": intents,
        "providers": providers,
        "cells": cells,
        "states": coverage.get("states") or [],
        "source": "C13",
        "note": "Click a cell for the shortest causal why. Same fulfillment records as Coverage.",
    }


def _topology(coverage: dict[str, Any], store: ConfigStore) -> dict[str, Any]:
    records = coverage.get("records") or []
    examples = []
    for rec in records:
        region = rec.get("region")
        if region not in {"CA", "DE", "SG"}:
            continue
        route = rec.get("route")
        if route not in {"DIRECT", "AGGREGATED"}:
            continue
        aggregated = route == "AGGREGATED" or rec.get("providerType") == "AGGREGATOR"
        examples.append(
            {
                "intentId": rec.get("intentId"),
                "intentLabel": rec.get("intentLabel"),
                "enterprise": rec.get("enterpriseLabel"),
                "region": region,
                "regionLabel": rec.get("regionLabel") or REGION_LABELS.get(str(region), region),
                "route": route,
                "provider": rec.get("providerLabel"),
                "via": rec.get("routeProviderLabel") if aggregated else None,
                "status": rec.get("fulfillmentStatus"),
                "language": "ROUTED THROUGH" if aggregated else "DIRECT",
                "doesNotOwnApis": aggregated,
            }
        )
        if len(examples) >= 12:
            break
    return {
        "question": "How does this Intent reach network supply?",
        "direct": "Enterprise → NetAware → Network Provider",
        "aggregated": "Enterprise → NetAware → Aggregator A → Network Provider",
        "hybrid": "One Intent can use different routes by region/provider.",
        "regions": ["Canada", "Germany", "Singapore"],
        "examples": examples,
        "note": "Aggregator A does not own operator APIs. Routed through / normalized through / available via.",
        "source": "C13 configured demo coverage",
    }
