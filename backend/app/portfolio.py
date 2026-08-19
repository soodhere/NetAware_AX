"""Cadence 12 sales portfolio index. Not Demand Map. Not SalesScenarioProfile."""
from __future__ import annotations

from typing import Any

from .model import ConfigStore
from .registry import CatalogRegistry


MATURITY = {"LIVE", "GUIDED", "EXPLORE"}
COMPLEXITY = {"BASIC", "COMPOSED", "ADVANCED_AGENTIC"}


def load_portfolio(store: ConfigStore) -> dict[str, Any]:
    return store.sales_portfolio or {}


def visible_rows(store: ConfigStore) -> list[dict[str, Any]]:
    return [row for row in (load_portfolio(store).get("visible") or []) if row.get("visible") is not False]


def row_by_use_case(store: ConfigStore, enterprise_id: str, use_case_id: str) -> dict[str, Any] | None:
    for row in visible_rows(store):
        if row.get("enterpriseId") == enterprise_id and row.get("useCaseId") == use_case_id:
            return row
    return None


def _enrich_row(store: ConfigStore, row: dict[str, Any]) -> dict[str, Any]:
    ent = store.enterprise_by_id.get(str(row.get("enterpriseId") or "")) or {}
    app = store.application_by_id.get(str(row.get("applicationId") or "")) or {}
    uc = store.use_case_by_id.get(str(row.get("useCaseId") or "")) or {}
    intent = store.intent_by_id.get(str(row.get("intentId") or "")) or {}
    domain = store.domain_by_id.get(str(ent.get("domainId") or uc.get("domainId") or "")) or {}
    maturity = str(row.get("scenarioMaturity") or "EXPLORE")
    return {
        **row,
        "enterprise": {"id": ent.get("id"), "label": ent.get("label")},
        "application": {"id": app.get("id"), "label": app.get("label")},
        "useCase": {"id": uc.get("id"), "label": uc.get("label")},
        "intent": {"id": intent.get("id"), "label": intent.get("label")},
        "industryLabel": (domain.get("label") or row.get("industry")),
        "runnable": maturity in {"LIVE", "GUIDED"},
        "exploreOnly": maturity == "EXPLORE",
        "coverageHref": f"/coverage/enterprise/{row.get('enterpriseId')}/use-case/{row.get('useCaseId')}",
        "demandHref": f"/demand/enterprise/{row.get('enterpriseId')}",
    }


def public_portfolio(store: ConfigStore, registry: CatalogRegistry | None = None) -> dict[str, Any]:
    doc = load_portfolio(store)
    rows = [_enrich_row(store, row) for row in visible_rows(store)]
    by_industry: dict[str, list[dict[str, Any]]] = {}
    by_motion: dict[str, list[dict[str, Any]]] = {}
    reverse: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_industry.setdefault(str(row.get("industry")), []).append(row)
        for motion in row.get("commercialMotion") or []:
            by_motion.setdefault(str(motion), []).append(row)
        for cap in row.get("capabilities") or []:
            reverse.setdefault(str(cap), []).append(
                {
                    "useCaseId": row.get("useCaseId"),
                    "intentId": row.get("intentId"),
                    "enterprise": (row.get("enterprise") or {}).get("label"),
                    "application": (row.get("application") or {}).get("label"),
                    "maturity": row.get("scenarioMaturity"),
                    "industry": row.get("industry"),
                }
            )
    families = len(registry.families) if registry else 13
    return {
        "headline": "Sales portfolio",
        "note": "LIVE executes. GUIDED is configuration-driven. EXPLORE is mapped opportunity — not fake execution.",
        "scenarios": rows,
        "count": len(rows),
        "motions": doc.get("motions") or [],
        "industries": doc.get("industries") or [],
        "byIndustry": by_industry,
        "byMotion": by_motion,
        "whereCouldISellThis": reverse,
        "leverage": {
            **(doc.get("leverage") or {}),
            "catalogFamilies": families,
        },
        "rejected": doc.get("rejected") or [],
    }


def industry_view(store: ConfigStore, industry_id: str) -> dict[str, Any] | None:
    doc = load_portfolio(store)
    meta = next((i for i in (doc.get("industries") or []) if i.get("id") == industry_id), None)
    rows = [_enrich_row(store, row) for row in visible_rows(store) if row.get("industry") == industry_id]
    if not meta and not rows:
        return None
    apps = []
    seen = set()
    for row in rows:
        app_id = row.get("applicationId")
        if app_id in seen:
            continue
        seen.add(app_id)
        apps.append(row.get("application"))
    return {
        "industry": meta or {"id": industry_id},
        "applications": apps,
        "useCases": [
            {
                "useCase": row.get("useCase"),
                "application": row.get("application"),
                "enterprise": row.get("enterprise"),
                "businessProblem": row.get("businessProblem"),
                "decisionGap": row.get("decisionGap"),
                "networkContribution": row.get("networkContribution"),
                "capabilities": row.get("capabilities"),
                "maturity": row.get("scenarioMaturity"),
                "complexity": row.get("scenarioComplexity"),
                "runnable": row.get("runnable"),
            }
            for row in rows
        ],
    }


def motion_view(store: ConfigStore, motion_id: str) -> dict[str, Any] | None:
    doc = load_portfolio(store)
    meta = next((m for m in (doc.get("motions") or []) if m.get("id") == motion_id), None)
    rows = [
        _enrich_row(store, row)
        for row in visible_rows(store)
        if motion_id in (row.get("commercialMotion") or [])
    ]
    if not meta and not rows:
        return None
    return {
        "motion": meta or {"id": motion_id},
        "scenarios": rows,
    }


def reverse_capability(store: ConfigStore, capability_id: str) -> dict[str, Any]:
    rows = [
        _enrich_row(store, row)
        for row in visible_rows(store)
        if capability_id in (row.get("capabilities") or [])
    ]
    cap = store.capability_by_id.get(capability_id) or {"id": capability_id}
    return {
        "headline": "Where could I sell this?",
        "capability": {"id": cap.get("id"), "label": cap.get("label")},
        "scenarios": rows,
        "note": "Preparation for later coverage exploration. Not a Demand Map.",
    }
