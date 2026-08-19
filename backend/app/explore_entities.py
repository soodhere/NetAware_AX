"""Rich Explorer entity assemblers — derived from shared config/graph (Cadence 5)."""
from __future__ import annotations

from typing import Any

from .demo import _autonomy_preview, _intent_example, _policy_preview
from .explore_meta import (
    CAPABILITY_DISCOVERY_NOTES,
    CAPABILITY_LIVE_BEHAVIOR,
    DISCOVERY_LINKS,
    DOMAIN_LIVE_DEMOS,
    EVIDENCE_GRADE_LABELS,
    EXECUTABLE_INTENTS,
    FAMILY_DISCOVERY_NOTES,
    OPERATION_LIVE_HINTS,
    POLICY_DISCOVERY_NOTES,
    evidence_grade_label,
    live_link_for_intent,
)
from .graph import KnowledgeGraph
from .presentation import enrich_family_for_ui, enrich_operation_record, network_roles
from .model import ConfigStore
from .registry import CatalogRegistry


def explore_nav() -> list[dict[str, str]]:
    return [
        {"id": "domains", "label": "Domains"},
        {"id": "use-cases", "label": "Use cases"},
        {"id": "intents", "label": "Intents"},
        {"id": "agents", "label": "Agents"},
        {"id": "my-context", "label": "My Context"},
        {"id": "purposes", "label": "Purposes"},
        {"id": "policies", "label": "Policies"},
        {"id": "autonomy", "label": "Autonomy"},
        {"id": "capabilities", "label": "Capabilities"},
        {"id": "catalog", "label": "API Catalog"},
        {"id": "providers", "label": "Providers / Routes"},
    ]


def _enterprise_for_domain(store: ConfigStore, domain_id: str) -> dict[str, Any] | None:
    for ent in store.enterprises:
        if ent.get("domainId") == domain_id:
            return ent
    return None


def _routes_for_operation(store: ConfigStore, operation_id: str) -> list[dict[str, Any]]:
    return [r for r in store.routes if r.get("operationId") == operation_id]


def _providers_for_operation(store: ConfigStore, operation_id: str) -> list[str]:
    ids: list[str] = []
    for block in store.provider_capabilities:
        for op in block.get("operations") or []:
            if op.get("operationId") == operation_id:
                ids.append(str(block.get("providerId")))
    return list(dict.fromkeys(ids))


def enrich_domain(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry, domain_id: str) -> dict[str, Any]:
    body = graph.forward_domain(domain_id)
    domain = body.get("domain") or {}
    ent = _enterprise_for_domain(store, domain_id)
    families: dict[str, dict[str, Any]] = {}
    use_case_rows = []
    for uc_row in body.get("useCases") or []:
        uc = uc_row.get("useCase") or {}
        intent_ids = [((i.get("intent") or {}).get("id")) for i in uc_row.get("intents") or []]
        caps: set[str] = set()
        for iid in intent_ids:
            for link in graph.intent_caps.get(str(iid), []):
                caps.add(str(link["capabilityId"]))
        fam_labels = []
        for cap_id in caps:
            for fam in registry.families:
                if cap_id in (fam.get("capabilities") or []):
                    fam_labels.append(str(fam.get("label")))
                    families[str(fam.get("id"))] = fam
        use_case_rows.append(
            {
                "useCase": uc,
                "intents": uc_row.get("intents"),
                "networkFamilies": sorted(set(fam_labels)),
            }
        )
    return {
        **body,
        "exampleEnterprise": ent,
        "useCaseRows": use_case_rows,
        "networkFamilies": list(families.values()),
        "liveDemo": DOMAIN_LIVE_DEMOS.get(domain_id),
    }


def enrich_use_case(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry, use_case_id: str) -> dict[str, Any]:
    body = graph.forward_use_case(use_case_id)
    uc = body.get("useCase") or {}
    intents = body.get("intents") or []
    primary = (intents[0] or {}).get("intent") or {}
    intent_id = str(primary.get("id") or "")
    ent = next((e for e in store.enterprises if e.get("domainId") == uc.get("domainId")), None)
    agent = next((a for a in store.agents if a.get("enterpriseId") == (ent or {}).get("id")), None)
    caps = []
    families: set[str] = set()
    for block in (intents[0] or {}).get("capabilities") or []:
        cap = block.get("capability") or {}
        caps.append(
            {
                **cap,
                "role": block.get("role"),
                "evidenceGrade": evidence_grade_label(block.get("evidence")),
            }
        )
        for fam in registry.families:
            if cap.get("id") in (fam.get("capabilities") or []):
                families.add(str(fam.get("label")))
    return {
        **body,
        "businessProblem": uc.get("networkComplement"),
        "existingSystems": uc.get("existingSystems") or [],
        "existingApis": uc.get("existingApis") or [],
        "purpose": store.purpose_by_id.get(str(primary.get("defaultPurposeId") or "")),
        "capabilitiesSummary": caps,
        "networkFamilies": sorted(families),
        "policyPreview": _policy_preview(store, str((ent or {}).get("id") or ""), intent_id) if ent and intent_id else {},
        "autonomyPreview": _autonomy_preview(store, str((agent or {}).get("id") or ""), intent_id) if agent and intent_id else {},
        "liveDemo": live_link_for_intent(intent_id),
        "intentVsUseCase": "Use case is the business job. Intent is the runtime outcome request.",
    }


def enrich_intent(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry, intent_id: str) -> dict[str, Any]:
    body = graph.forward_intent(intent_id)
    intent = body.get("intent") or {}
    purpose = store.purpose_by_id.get(str(intent.get("defaultPurposeId") or ""))
    agents = [a for a in store.agents if intent_id in (a.get("allowedIntents") or [])]
    policies = [p for p in store.policies if p.get("intentId") == intent_id]
    autonomy = []
    for agent in agents:
        autonomy.append({"agent": agent, "rules": _autonomy_preview(store, str(agent.get("id")), intent_id)})
    caps = []
    for block in body.get("capabilities") or []:
        cap = block.get("capability") or {}
        cap_id = str(cap.get("id"))
        caps.append(
            {
                **block,
                "evidenceGrade": evidence_grade_label(block.get("evidence")),
                "liveBehavior": CAPABILITY_LIVE_BEHAVIOR.get(cap_id, []),
            }
        )
    example = _intent_example(store, intent_id)
    ent = None
    if agents:
        ent = store.enterprise_by_id.get(str(agents[0].get("enterpriseId") or ""))
    known = {
        "source": "FROM ONBOARDING / CONFIGURATION",
        "note": "NetAware reuses configured knowledge. The application sends a small runtime request.",
    }
    if ent:
        app = store.application_by_id.get(str(agents[0].get("actsOnBehalfOf") or ""))
        known["rows"] = [
            {"label": "Enterprise", "value": ent.get("label")},
            {"label": "Application", "value": (app or {}).get("label")},
            {"label": "Purpose", "value": (purpose or {}).get("audienceLabel") or (purpose or {}).get("label")},
            {"label": "Policy", "value": (policies[0] or {}).get("label") if policies else "Configured"},
        ]
    return {
        **body,
        "purpose": purpose,
        "purposeSource": "CONFIGURED APPLICATION / INTENT PROFILE",
        "agents": agents,
        "policies": policies,
        "autonomy": autonomy,
        "capabilities": caps,
        "runtimeRequest": example.get("request"),
        "runtimeRequestNote": example.get("explainer"),
        "knownFromConfiguration": known,
        "executable": intent_id in EXECUTABLE_INTENTS,
        "liveDemo": live_link_for_intent(intent_id),
        "discoveryLink": DISCOVERY_LINKS.get(intent_id),
        "explorerOnly": bool(intent.get("explorerOnly")) and intent_id not in EXECUTABLE_INTENTS,
    }


def enrich_capability(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry, capability_id: str) -> dict[str, Any]:
    body = graph.reverse_capability(capability_id)
    cap = body.get("capability") or {}
    live = CAPABILITY_LIVE_BEHAVIOR.get(capability_id, [])
    intent_links = []
    for i in body.get("intents") or []:
        iid = str(i.get("id"))
        intent_links.append({"intent": i, "liveDemo": live_link_for_intent(iid), "liveBehavior": live})
    routes = []
    for op in body.get("operations") or []:
        op_id = str(op.get("operationId"))
        routes.extend(_routes_for_operation(store, op_id))
    return {
        **body,
        "liveBehavior": live,
        "discoveryNote": CAPABILITY_DISCOVERY_NOTES.get(capability_id),
        "intentLinks": intent_links,
        "routes": routes,
        "policyNote": "Policy outcomes vary by enterprise purpose and consent configuration.",
    }


def enrich_catalog_api(store: ConfigStore, graph: KnowledgeGraph, registry: CatalogRegistry, api_id: str) -> dict[str, Any]:
    body = graph.reverse_api(api_id)
    ops = []
    for op in body.get("operations") or []:
        op_id = str(op.get("operation_id"))
        ops.append(
            enrich_operation_record(
                {
                    **op,
                    "liveHint": OPERATION_LIVE_HINTS.get(op_id),
                    "routes": _routes_for_operation(store, op_id),
                }
            )
        )
    live_refs = []
    for intent in body.get("intents") or []:
        link = live_link_for_intent(str(intent.get("id")))
        if link:
            live_refs.append(link)
    api = body.get("api") or {}
    if api:
        body["api"] = enrich_family_for_ui(api)
    enriched_specs = [enrich_operation_record(v) for v in body.get("catalogVariants") or []]
    return {
        **body,
        "operations": ops,
        "catalogVariants": enriched_specs if enriched_specs else body.get("catalogVariants"),
        "liveReferences": live_refs,
        "discoveryNote": FAMILY_DISCOVERY_NOTES.get(api_id),
        "networkRoles": network_roles(),
        "netawareBusinessStatus": (body.get("api") or {}).get("netawareBusinessStatus"),
        "camaraApiVersion": (body.get("api") or {}).get("camaraApiVersion"),
        "apiVersionMaturity": (body.get("api") or {}).get("apiVersionMaturity"),
        "camaraProjectLifecycle": (body.get("api") or {}).get("camaraProjectLifecycle"),
        "fulfillment": {
            "whereAvailable": "WHERE IS THIS AVAILABLE?",
            "whichIntents": "WHICH INTENTS DEPEND ON IT?",
            "href": f"/coverage/family/{api_id}",
            "demandHref": f"/demand/family/{api_id}",
            "seeDemand": "SEE DEMAND",
            "whatDoesThisEnable": "WHAT DOES THIS ENABLE?",
            "capabilityHrefs": [
                {"id": (c.get("id") if isinstance(c, dict) else c), "href": f"/coverage/capabilities/{c.get('id') if isinstance(c, dict) else c}"}
                for c in (body.get("capabilities") or [])
            ],
        },
    }


def enrich_operation(store: ConfigStore, graph: KnowledgeGraph, operation_id: str) -> dict[str, Any]:
    body = graph.reverse_operation(operation_id)
    variants = [
        enrich_operation_record({**variant, "operation_id": operation_id})
        for variant in body.get("catalogVariants") or []
    ]
    if variants:
        body["catalogVariants"] = variants
        lead = variants[0]
        body["camaraApiVersion"] = lead.get("camaraApiVersion")
        body["apiVersionMaturity"] = lead.get("apiVersionMaturity")
        body["camaraProjectLifecycle"] = lead.get("camaraProjectLifecycle")
        body["netawareBusinessStatus"] = lead.get("business_status")
    body["liveHint"] = OPERATION_LIVE_HINTS.get(operation_id)
    body["routes"] = _routes_for_operation(store, operation_id)
    provider_ids = _providers_for_operation(store, operation_id)
    body["providers"] = [store.provider_by_id.get(pid) for pid in provider_ids if store.provider_by_id.get(pid)]
    return body


def list_agents(store: ConfigStore) -> list[dict[str, Any]]:
    rows = []
    for agent in store.agents:
        app = store.application_by_id.get(str(agent.get("actsOnBehalfOf") or ""))
        ent = store.enterprise_by_id.get(str(agent.get("enterpriseId") or ""))
        rows.append({"agent": agent, "application": app, "enterprise": ent})
    return rows


def agent_detail(store: ConfigStore, agent_id: str) -> dict[str, Any] | None:
    agent = store.agent_by_id.get(agent_id)
    if not agent:
        return None
    app = store.application_by_id.get(str(agent.get("actsOnBehalfOf") or ""))
    ent = store.enterprise_by_id.get(str(agent.get("enterpriseId") or ""))
    intents = [store.intent_by_id.get(i) for i in agent.get("allowedIntents") or [] if i in store.intent_by_id]
    policies = [p for p in store.policies if p.get("agentId") == agent_id]
    autonomy = [r for r in store.autonomy_rules if r.get("agentId") == agent_id]
    subs = [s for s in store.subscriptions if s.get("enterpriseId") == ent.get("id")] if ent else []
    return {
        "agent": agent,
        "application": app,
        "enterprise": ent,
        "identityModel": "SIMULATED FOR PROTOTYPE",
        "identityNote": "Production auth/delegation is intentionally unresolved.",
        "allowedIntents": intents,
        "policies": policies,
        "autonomyRules": autonomy,
        "subscriptions": subs,
        "liveIntents": [live_link_for_intent(str(i.get("id"))) for i in intents if i and live_link_for_intent(str(i.get("id")))],
    }


def list_purposes(store: ConfigStore) -> list[dict[str, Any]]:
    return store.purposes


def purpose_detail(store: ConfigStore, purpose_id: str) -> dict[str, Any] | None:
    purpose = store.purpose_by_id.get(purpose_id)
    if not purpose:
        return None
    intents = [i for i in store.intents if i.get("defaultPurposeId") == purpose_id]
    policies = [p for p in store.policies if p.get("purposeId") == purpose_id]
    agreements = [a for a in store.agreements if purpose_id in (a.get("permittedPurposes") or [])]
    return {
        "purpose": purpose,
        "intents": intents,
        "policies": policies,
        "agreements": agreements,
        "permittedFamilies": purpose.get("permittedCapabilityFamilies") or [],
        "legalNote": "CONFIGURED DEMO POLICY — not a universal legal requirement.",
    }


def list_policies(store: ConfigStore) -> list[dict[str, Any]]:
    return store.policies


def policy_detail(store: ConfigStore, policy_id: str) -> dict[str, Any] | None:
    policy = store.policy_by_id.get(policy_id)
    if not policy:
        return None
    rules = [r for r in store.policy_rules if r.get("policyId") == policy_id]
    consents = [c for c in store.consent_rules if c.get("policyId") == policy_id]
    autonomy = [
        r
        for r in store.autonomy_rules
        if r.get("agentId") == policy.get("agentId") and r.get("intentId") == policy.get("intentId")
    ]
    live = live_link_for_intent(str(policy.get("intentId") or ""))
    exercised = []
    if policy_id == "rocket-bank-trust-policy":
        exercised = ["Location consent → BLOCKED in Rocket Bank", "Trust evidence → reused in recovery"]
    elif policy_id == "high-flight-baggage-policy":
        exercised = ["Location consent → BLOCKED; replan to ground ops"]
    elif policy_id == "citycare-pharmacy-policy":
        exercised = ["KYC Match → BLOCKED; Age Verification selected"]
    return {
        "policy": policy,
        "rules": rules,
        "consentRules": consents,
        "autonomyRules": autonomy,
        "liveScenario": live,
        "discoveryNote": POLICY_DISCOVERY_NOTES.get(policy_id),
        "exercisedEffects": exercised,
        "source": "CONFIGURED DEMO POLICY",
    }


def autonomy_index(store: ConfigStore) -> dict[str, Any]:
    levels = ["OBSERVE", "RECOMMEND", "ACT_WITH_APPROVAL", "ACT", "NOT_AUTHORIZED"]
    examples = [
        {
            "enterprise": "Rocket Bank",
            "intentId": "assess_network_trust",
            "rows": [
                ("Gather evidence", "ACT"),
                ("Recommend STEP_UP", "RECOMMEND"),
                ("Decline payment", "NOT_AUTHORIZED"),
            ],
        },
        {
            "enterprise": "High Flight",
            "intentId": "ensure_baggage_connection",
            "rows": [
                ("Observe / assess", "ACT"),
                ("Expedite transfer", "ACT_WITH_APPROVAL"),
                ("Change flight plan", "NOT_AUTHORIZED"),
            ],
        },
        {
            "enterprise": "Acme",
            "intentId": "maintain_inspection_experience",
            "rows": [("Observe", "ACT"), ("QoD session", "ACT"), ("MES routing", "NOT_AUTHORIZED")],
        },
        {
            "enterprise": "CityCare",
            "intentId": "verify_pharmacy_age_gate",
            "rows": [
                ("Age assertion", "ACT"),
                ("Return eligibility", "ACT"),
                ("Dispense/refuse", "NOT_AUTHORIZED"),
            ],
        },
    ]
    return {
        "model": levels,
        "tagline": "Autonomous within a defined envelope.",
        "examples": examples,
        "rules": store.autonomy_rules,
    }


def list_providers(store: ConfigStore) -> list[dict[str, Any]]:
    return store.providers


def provider_detail(store: ConfigStore, provider_id: str) -> dict[str, Any] | None:
    provider = store.provider_by_id.get(provider_id)
    if not provider:
        return None
    ops = []
    for block in store.provider_capabilities:
        if block.get("providerId") != provider_id:
            continue
        ops.extend(block.get("operations") or [])
    routes = [r for r in store.routes if r.get("providerId") == provider_id]
    return {
        "provider": provider,
        "operations": ops,
        "routes": routes,
        "coverageHref": f"/coverage/provider/{provider_id}",
        "demandHref": f"/demand/provider/{provider_id}",
        "providerType": "AGGREGATOR" if provider.get("kind") == "aggregator" else "NETWORK_PROVIDER",
    }


def list_routes(store: ConfigStore) -> list[dict[str, Any]]:
    enriched = []
    for route in store.routes:
        pid = route.get("providerId")
        provider = store.provider_by_id.get(str(pid)) if pid else None
        enriched.append({**route, "provider": provider})
    return enriched


def my_context(store: ConfigStore, enterprise_id: str) -> dict[str, Any] | None:
    ent = store.enterprise_by_id.get(enterprise_id)
    if not ent:
        return None
    featured = next(
        (row for row in (store.demo or {}).get("featuredEnterprises") or [] if row.get("enterpriseId") == enterprise_id),
        None,
    )
    apps = [a for a in store.applications if a.get("enterpriseId") == enterprise_id]
    agents = [a for a in store.agents if a.get("enterpriseId") == enterprise_id]
    subs = [s for s in store.subscriptions if s.get("enterpriseId") == enterprise_id]
    ents = [e for e in store.entitlements if any(a.get("id") == e.get("agentId") for a in agents)]
    agreements = [a for a in store.agreements if a.get("enterpriseId") == enterprise_id]
    policies = [p for p in store.policies if p.get("enterpriseId") == enterprise_id]
    purposes = list(
        {
            str(p.get("purposeId")): store.purpose_by_id.get(str(p.get("purposeId")))
            for p in policies
            if p.get("purposeId") in store.purpose_by_id
        }.values()
    )
    example_intent = None
    for agent in agents:
        for iid in agent.get("allowedIntents") or []:
            if iid in EXECUTABLE_INTENTS:
                example_intent = _intent_example(store, iid)
                break
    routes = [r for r in store.routes if r.get("enterpriseId") in {enterprise_id, None}]
    return {
        "enterprise": ent,
        "featured": featured,
        "applications": apps,
        "agents": agents,
        "purposes": purposes,
        "subscriptions": subs,
        "entitlements": ents,
        "agreements": agreements,
        "policies": policies,
        "consentRules": [c for c in store.consent_rules if c.get("policyId") in {p.get("id") for p in policies}],
        "routes": routes,
        "knownFromConfiguration": {
            "source": "WHAT NETAWARE ALREADY KNOWS",
            "note": "From onboarding. Not resent on every runtime call.",
        },
        "runtimeRequestExample": example_intent.get("request") if example_intent else {},
        "runtimeRequestSource": "WHAT THE APPLICATION SENDS AT RUNTIME",
    }


def explore_summary(store: ConfigStore, registry: CatalogRegistry) -> dict[str, Any]:
    return {
        "catalog": "AX_ACTIVE_CATALOG",
        "businessFamilies": len(registry.families),
        "technicalSpecs": registry.technical_spec_count(),
        "operations": len(registry.operations),
        "domains": len(store.domains),
        "useCases": len(store.use_cases),
        "intents": len(store.intents),
        "capabilities": len(store.capabilities),
        "agents": len(store.agents),
        "purposes": len(store.purposes),
        "policies": len(store.policies),
        "providers": len(store.providers),
        "routes": len(store.routes),
        "evidenceGrades": EVIDENCE_GRADE_LABELS,
        "executableIntents": sorted(EXECUTABLE_INTENTS),
        "nav": explore_nav(),
        "note": "13 current-focus families → capabilities → many intents → many domains. Configuration graph, not a runtime trace.",
    }
