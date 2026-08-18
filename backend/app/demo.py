"""Cadence 1 read-only demo and explore assemblers. No execution."""
from __future__ import annotations

from typing import Any

from .graph import KnowledgeGraph
from .presentation import capability_network_role, enrich_family_for_ui, network_roles, value_clarity_for
from .model import ConfigStore
from .registry import CatalogRegistry

AUTONOMY_ORDER = ["OBSERVE", "RECOMMEND", "ACT_WITH_APPROVAL", "ACT", "NOT_AUTHORIZED"]


def _family_for_capability(registry: CatalogRegistry, capability_id: str) -> dict[str, Any] | None:
    for fam in registry.families:
        if capability_id in (fam.get("capabilities") or []):
            return fam
    return None


def _compact_family(fam: dict[str, Any]) -> dict[str, Any]:
    enriched = enrich_family_for_ui(fam)
    specs = fam.get("technicalSpecs") or []
    maturities = list(dict.fromkeys(str(s.get("specMaturity")) for s in specs if s.get("specMaturity")))
    return {
        "id": enriched.get("id"),
        "label": enriched.get("label"),
        "businessStatus": enriched.get("businessStatus"),
        "netawareBusinessStatus": enriched.get("netawareBusinessStatus"),
        "familyGroup": enriched.get("familyGroup"),
        "specMaturity": maturities,
        "camaraApiVersion": enriched.get("camaraApiVersion"),
        "apiVersionMaturity": enriched.get("apiVersionMaturity"),
        "camaraProjectLifecycle": enriched.get("camaraProjectLifecycle"),
        "honesty": enriched.get("honesty"),
        "distinction": enriched.get("distinction"),
        "note": enriched.get("note"),
    }


def enterprise_card(store: ConfigStore, enterprise_id: str) -> dict[str, Any] | None:
    ent = store.enterprise_by_id.get(enterprise_id)
    if not ent:
        return None
    apps = [a for a in store.applications if a.get("enterpriseId") == enterprise_id]
    agents = [a for a in store.agents if a.get("enterpriseId") == enterprise_id]
    domain = store.domain_by_id.get(str(ent.get("domainId") or ""))
    return {
        "enterprise": ent,
        "domain": domain,
        "applications": apps,
        "agents": agents,
    }


def featured_row(store: ConfigStore, row: dict[str, Any]) -> dict[str, Any]:
    card = enterprise_card(store, str(row["enterpriseId"])) or {}
    use_cases = [store.use_case_by_id[uid] for uid in row.get("useCaseIds") or [] if uid in store.use_case_by_id]
    related = [store.use_case_by_id[uid] for uid in row.get("relatedUseCaseIds") or [] if uid in store.use_case_by_id]
    return {
        **card,
        "storyId": row.get("storyId") or row.get("heroUseCaseId"),
        "domainAudienceLabel": row.get("domainAudienceLabel"),
        "heroUseCaseId": row.get("heroUseCaseId"),
        "heroCard": row.get("heroCard") or {},
        "valueClarity": row.get("valueClarity") or {},
        "secondaryDemo": row.get("secondaryDemo"),
        "presentationOrder": row.get("presentationOrder"),
        "useCases": use_cases,
        "relatedUseCases": related,
        "existingSystems": row.get("existingSystems") or [],
    }


def _intent_example(store: ConfigStore, intent_id: str) -> dict[str, Any]:
    examples = (store.demo or {}).get("intentExamples") or {}
    row = examples.get(intent_id) or {}
    intent = store.intent_by_id.get(intent_id) or {}
    request = row.get("request") or {"intent": intent_id, "subject": {}, "context": {}}
    return {
        "id": intent_id,
        "label": intent.get("label"),
        "plain": row.get("plain") or intent.get("label"),
        "request": request,
        "explainer": "Intent is the outcome the application or agent wants — without specifying which Network APIs should be called.",
    }


def _policy_preview(store: ConfigStore, enterprise_id: str, intent_id: str) -> dict[str, Any]:
    policy = next(
        (
            p
            for p in store.policies
            if p.get("enterpriseId") == enterprise_id and p.get("intentId") == intent_id
        ),
        None,
    )
    agreement = next((a for a in store.agreements if a.get("enterpriseId") == enterprise_id), None)
    purpose = None
    if policy and policy.get("purposeId") in store.purpose_by_id:
        purpose = store.purpose_by_id[str(policy["purposeId"])]
    consents = []
    if policy:
        for rule in store.consent_rules:
            if rule.get("policyId") == policy.get("id"):
                cap = store.capability_by_id.get(str(rule.get("capabilityId") or ""))
                consents.append(
                    {
                        "capabilityId": rule.get("capabilityId"),
                        "capability": (cap or {}).get("label"),
                        "required": rule.get("required"),
                        "available": rule.get("available"),
                        "note": rule.get("note"),
                    }
                )
    return {
        "label": (policy or {}).get("label") or "Configured demo policy",
        "source": "CONFIGURED DEMO POLICY",
        "purpose": (purpose or {}).get("audienceLabel") or (purpose or {}).get("label") or "Configured",
        "purposeId": (purpose or {}).get("id"),
        "consent": "Required for selected capabilities where configured" if consents else "Configured",
        "consentRules": consents,
        "agreement": (agreement or {}).get("label") or "Configured",
        "dataResidency": (agreement or {}).get("dataResidency") or "Configured",
        "subscriptions": "Configured",
    }


def _autonomy_preview(store: ConfigStore, agent_id: str, intent_id: str) -> dict[str, Any]:
    rules = [
        r
        for r in store.autonomy_rules
        if r.get("agentId") == agent_id and r.get("intentId") == intent_id
    ]
    by_level: dict[str, list[str]] = {k: [] for k in AUTONOMY_ORDER}
    for rule in rules:
        by_level.setdefault(str(rule.get("level")), []).append(str(rule.get("action")))
    summary = {
        "observe": "Allowed" if by_level.get("ACT") or by_level.get("OBSERVE") else "Not configured",
        "recommend": "Allowed" if by_level.get("RECOMMEND") else "Not configured for this intent",
        "actWithApproval": (
            "Allowed for selected actions" if by_level.get("ACT_WITH_APPROVAL") else "Not configured for this intent"
        ),
        "act": "Restricted by configured intent/action policy",
    }
    if by_level.get("NOT_AUTHORIZED"):
        summary["notAuthorized"] = by_level["NOT_AUTHORIZED"]
    return {
        "label": "Configured by intent/action. Not a production identity architecture.",
        "summary": summary,
        "rules": rules,
    }


def _known_from_config(
    store: ConfigStore,
    featured: dict[str, Any],
    enterprise: dict[str, Any],
    application: dict[str, Any] | None,
    domain: dict[str, Any] | None,
    purpose: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "source": "FROM ONBOARDING / CONFIGURATION",
        "note": "You do not send this on every request. NetAware already has it from onboarding.",
        "rows": [
            {"label": "Enterprise", "value": enterprise.get("label")},
            {"label": "Application", "value": (application or {}).get("label") or "Configured"},
            {"label": "Environment", "value": featured.get("environment") or "Production"},
            {"label": "Domain", "value": featured.get("domainAudienceLabel") or (domain or {}).get("label")},
            {"label": "Purpose", "value": (purpose or {}).get("audienceLabel") or (purpose or {}).get("label") or "Configured"},
            {"label": "Region", "value": featured.get("regionDisplay") or "Configured"},
            {"label": "Network API subscriptions", "value": featured.get("subscriptionsDisplay") or "Configured"},
            {"label": "Provider relationships", "value": featured.get("providersDisplay") or "Configured"},
            {"label": "Security", "value": featured.get("securityDisplay") or "Configured"},
        ],
    }


def briefing(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    enterprise_id: str,
    use_case_id: str,
) -> dict[str, Any] | None:
    featured_rows = [row for row in (store.demo or {}).get("featuredEnterprises") or [] if row.get("enterpriseId") == enterprise_id]
    featured = next(
        (
            row
            for row in featured_rows
            if use_case_id == row.get("heroUseCaseId") or use_case_id in (row.get("useCaseIds") or [])
        ),
        featured_rows[0] if featured_rows else None,
    )
    if not featured:
        return None
    use_case = store.use_case_by_id.get(use_case_id)
    if not use_case:
        return None
    allowed = set(featured.get("useCaseIds") or []) | {featured.get("heroUseCaseId")}
    if use_case_id not in allowed and use_case_id not in (featured.get("relatedUseCaseIds") or []):
        # Still allow any use case in the enterprise domain for explorer-linked demo.
        ent = store.enterprise_by_id.get(enterprise_id) or {}
        if use_case.get("domainId") != ent.get("domainId"):
            return None

    forward = graph.forward_use_case(use_case_id)
    intent_wrap = (forward.get("intents") or [None])[0] or {}
    intent = intent_wrap.get("intent") or {}
    intent_id = str(intent.get("id") or "")
    enterprise = store.enterprise_by_id[enterprise_id]
    policy = next(
        (p for p in store.policies if p.get("intentId") == intent_id and p.get("enterpriseId") == enterprise_id),
        None,
    )
    application = store.application_by_id.get(str((policy or {}).get("applicationId") or "")) or next(
        (a for a in store.applications if a.get("enterpriseId") == enterprise_id), None
    )
    agent = store.agent_by_id.get(str((policy or {}).get("agentId") or "")) or next(
        (a for a in store.agents if a.get("enterpriseId") == enterprise_id), None
    )
    domain = store.domain_by_id.get(str(enterprise.get("domainId") or ""))
    purpose = store.purpose_by_id.get(str(intent.get("defaultPurposeId") or ""))

    caps: list[dict[str, Any]] = []
    families: list[dict[str, Any]] = []
    seen_fam: set[str] = set()
    for cap_block in intent_wrap.get("capabilities") or []:
        cap = cap_block.get("capability") or {}
        cap_id = str(cap.get("id") or "")
        fam = _family_for_capability(registry, cap_id)
        ops = []
        for op in cap_block.get("operations") or []:
            rec = op.get("catalog") or {}
            ops.append(
                {
                    "operationId": op.get("operationId"),
                    "source": op.get("source"),
                    "evidence": op.get("evidence"),
                    "businessStatus": rec.get("business_status"),
                    "specMaturity": rec.get("spec_maturity"),
                    "family": rec.get("family"),
                    "productLabel": rec.get("product_label"),
                }
            )
        caps.append(
            {
                "id": cap_id,
                "label": cap.get("label"),
                "role": cap_block.get("role"),
                "networkRole": capability_network_role(cap_id),
                "evidence": cap_block.get("evidence"),
                "relevance": "POTENTIALLY_RELEVANT",
                "invoked": None,
                "invokedNote": "Not invoked. Cadence 1 has no runtime selection.",
                "familyId": (fam or {}).get("id"),
                "familyLabel": (fam or {}).get("label"),
                "operations": ops,
            }
        )
        if fam and fam["id"] not in seen_fam:
            seen_fam.add(str(fam["id"]))
            families.append(_compact_family(fam))

    existing_systems = use_case.get("existingSystems") or featured.get("existingSystems") or []
    existing_apis = use_case.get("existingApis") or []
    hero_runnable = {
        ("rocket-bank", "high-value-payment-protection"),
        ("rocket-bank", "passwordless-mobile-sign-in"),
        ("high-flight-airlines", "baggage-connection"),
        ("acme-manufacturing", "critical-inspection-camera"),
        ("citycare-health", "pharmacy-age-gate"),
    }
    secondary_runnable = {
        ("rocket-bank", "account-recovery-anomaly"),
    }
    is_runnable = (enterprise_id, use_case_id) in hero_runnable
    is_secondary = (enterprise_id, use_case_id) in secondary_runnable

    return {
        "configurationOnly": not is_runnable and not is_secondary,
        "executionEngine": is_runnable or is_secondary,
        "runtimeNotExecuted": not is_runnable and not is_secondary,
        "runnable": is_runnable,
        "secondaryDemo": is_secondary,
        "secondaryNote": (featured.get("secondaryDemo") or {}).get("note") if is_secondary else None,
        "enterprise": enterprise,
        "domain": domain,
        "domainAudienceLabel": featured.get("domainAudienceLabel") or (domain or {}).get("label"),
        "useCase": use_case,
        "existingSystems": existing_systems,
        "existingApis": existing_apis,
        "complementNote": use_case.get("networkComplement")
        or "Network capabilities complement existing systems. They do not replace them.",
        "intent": _intent_example(store, intent_id) if intent_id else {},
        "capabilities": caps,
        "catalogFamilies": families,
        "application": application,
        "agent": {
            **(agent or {}),
            "kind": "AUTHORIZED_AGENT",
            "actsForLabel": (application or {}).get("label"),
            "identityNote": "Authorized agent. Production identity and delegation are not locked.",
        },
        "knownFromOnboarding": _known_from_config(store, featured, enterprise, application, domain, purpose),
        "runtimeRequest": {
            "source": "RUNTIME REQUEST",
            "note": "The application sends a small outcome request. Configured context is not repeated.",
            "body": (_intent_example(store, intent_id).get("request") if intent_id else {}),
        },
        "policyPreview": _policy_preview(store, enterprise_id, intent_id) if intent_id else {},
        "autonomyPreview": _autonomy_preview(store, str((agent or {}).get("id") or ""), intent_id) if agent else {},
        "chain": {
            "domain": featured.get("domainAudienceLabel") or (domain or {}).get("label"),
            "domainId": (domain or {}).get("id"),
            "useCase": use_case.get("label"),
            "useCaseId": use_case_id,
            "intent": intent.get("label"),
            "intentId": intent_id,
            "capabilities": [{"id": c["id"], "label": c["label"], "role": c["role"]} for c in caps],
            "catalogFamilies": families,
        },
        "relevance": {
            "potentiallyRelevant": True,
            "actuallyInvoked": is_runnable or is_secondary,
            "note": (
                "Live run selects minimum sufficient capabilities under configured policy."
                if is_runnable or is_secondary
                else "Potentially relevant from configuration. Not invoked in this briefing."
            ),
        },
        "networkValueFraming": (store.demo or {}).get("networkValueFraming") or {},
        "networkRoles": network_roles(),
        "valueClarity": value_clarity_for(featured, use_case_id),
    }


def demo_index(store: ConfigStore) -> dict[str, Any]:
    product = (store.demo or {}).get("product") or {}
    featured_src = list((store.demo or {}).get("featuredEnterprises") or [])
    featured_src.sort(key=lambda row: int(row["presentationOrder"]) if row.get("presentationOrder") is not None else 99)
    featured = [featured_row(store, row) for row in featured_src]
    return {
        "product": product,
        "networkValueFraming": (store.demo or {}).get("networkValueFraming") or {},
        "networkRoles": network_roles(),
        "honesty": (store.demo or {}).get("honesty") or {},
        "featured": featured,
        "executionEngine": False,
    }


from .explore_entities import explore_summary


def explore_index(store: ConfigStore, registry: CatalogRegistry) -> dict[str, Any]:
    return explore_summary(store, registry)
