"""Cadence 12 — shared GUIDED scenario interpreter.

Configuration-driven. Deterministic. No LLM. No MCP. No custom runner
per enterprise. Does not replace LIVE runners. Does not import the
Cadence 10 interpreter spike into execute_intent.
"""
from __future__ import annotations

from typing import Any

import yaml
from fastapi import HTTPException

from .config import GUIDED_DIR
from .graph import KnowledgeGraph
from .model import ConfigStore
from .registry import CatalogRegistry
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

_SCENARIOS: dict[str, dict[str, Any]] | None = None


def _load_scenarios() -> dict[str, dict[str, Any]]:
    global _SCENARIOS
    if _SCENARIOS is not None:
        return _SCENARIOS
    path = GUIDED_DIR / "scenarios.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[str, dict[str, Any]] = {}
    for row in data.get("scenarios") or []:
        intent_id = str(row.get("intentId") or "")
        if not intent_id:
            continue
        if intent_id in out:
            raise ValueError(f"Duplicate guided scenario intent: {intent_id}")
        out[intent_id] = row
    _SCENARIOS = out
    return out


GUIDED_INTENTS: set[str] = set()


def _init_guided_intents() -> None:
    GUIDED_INTENTS.update(_load_scenarios().keys())


_init_guided_intents()


def guided_scenario(intent_id: str) -> dict[str, Any] | None:
    return _load_scenarios().get(intent_id)


def _action_to_state(action: str) -> str:
    if action == "CALL":
        return "SELECTED"
    if action == "SKIP":
        return "NOT_REQUIRED"
    if action == "REUSE":
        return "EVIDENCE_REUSED"
    return "BLOCKED_BY_POLICY"


def run_guided_intent(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    request: dict[str, Any],
) -> ExecutionTrace:
    from .runtime import (
        _append_network_invocation,
        _family_for,
        _op_meta,
        _primary_op,
        evaluate_capability_policy,
    )

    intent_id = str(request.get("intent") or "")
    cfg = guided_scenario(intent_id)
    if not cfg:
        raise HTTPException(status_code=409, detail=f"Intent not executable: {intent_id}")

    agent_id = str(request.get("agentId") or cfg.get("agentId"))
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
    uc_id = str(cfg.get("useCaseId") or graph.intent_use_case.get(intent_id) or "")
    use_case = store.use_case_by_id.get(uc_id)
    domain = store.domain_by_id.get(str((use_case or {}).get("domainId") or enterprise.get("domainId") or ""))
    policy = next((p for p in store.policies if p.get("id") == cfg.get("policyId")), None)
    if not policy:
        raise HTTPException(status_code=500, detail="Scenario policy missing")
    purpose = store.purpose_by_id.get(str(policy.get("purposeId") or cfg.get("purposeId") or intent.get("defaultPurposeId") or ""))
    if not purpose:
        raise HTTPException(status_code=500, detail="Purpose not resolved from configuration")

    corr = cfg.get("correlation") or {}
    req_body = {
        "intent": intent_id,
        "subject": (request.get("subject") or (cfg.get("request") or {}).get("subject")),
        "context": (request.get("context") or (cfg.get("request") or {}).get("context")),
    }
    ctx = req_body.get("context") or {}
    variant_id = str(ctx.get("guidedVariant") or cfg.get("defaultVariant") or "")
    variants = cfg.get("variants") or {}
    variant = variants.get(variant_id) or next(iter(variants.values()), {}) or {}

    telco = cfg.get("telcoFinder") or {}
    provider_label = str((telco.get("result") or {}).get("network") or "Network Provider A")
    mapped = list(graph.intent_caps.get(intent_id) or [])
    configured_caps = {str(row.get("capabilityId")): row for row in cfg.get("candidateCapabilities") or []}
    network_routes = cfg.get("networkRoutes") or {}
    sim_block = (variant.get("evidence") or {}) if isinstance(variant, dict) else {}

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

    plan_steps = [
        PlanStep(1, "Receive business event / Intent", None, None, state="COMPLETED"),
        PlanStep(2, "Resolve configured / onboarded context", None, None, state="COMPLETED"),
    ]
    n = 3
    for cap_id, row in configured_caps.items():
        plan_steps.append(
            PlanStep(n, f"{row.get('action')} {cap_id}", cap_id, None, "NETWORK", state="PLANNED")
        )
        n += 1
    plan_steps.append(PlanStep(n, "Return business outcome", None, None, state="COMPLETED"))
    plan = Plan(
        id=f"plan-guided-{intent_id}",
        intentId=intent_id,
        executionId=str(corr.get("executionId") or f"ax-guided-{intent_id}"),
        version=1,
        label="Guided configuration plan",
        note="Deterministic interpreter. Configuration drives CALL / SKIP / FILTER. Not a custom runner.",
        steps=plan_steps,
    )

    for op in cfg.get("domainOperations") or []:
        op_id = str(op.get("operationId") or "enterpriseOperation")
        invocations.append(
            Invocation(
                id=f"inv-ent-{op_id}",
                operationId=op_id,
                source="SIMULATED ENTERPRISE API",
                familyId="enterprise",
                familyLabel="SIMULATED ENTERPRISE API",
                specMaturity="",
                businessStatus="",
                method="POST",
                providerId="",
                providerLabel=str(op.get("owner") or "Enterprise system"),
                routeType="EXISTING_ENTERPRISE_INTEGRATION",
                correlationId=str(corr.get("correlationId") or ""),
                latencyMs=12,
                httpStatus=200,
                raw={"simulated": True, "kind": "SIMULATED_ENTERPRISE_API"},
                apiKind=str(op.get("apiKind") or "DOMAIN"),
                simulated=True,
                owner=str(op.get("owner") or ""),
                routeDisplay="Enterprise application (already have)",
            )
        )

    finder_ops: list[dict[str, Any]] = []
    step_by_cap = {s.capabilityId: s for s in plan.steps if s.capabilityId}

    for link in mapped:
        cap_id = str(link["capabilityId"])
        cap = store.capability_by_id.get(cap_id) or {"id": cap_id}
        fam = _family_for(registry, cap_id)
        ops_for_cap = list(graph.cap_ops.get(cap_id) or [])
        preferred = set(network_routes) | set(sim_block)
        op_row = next((row for row in ops_for_cap if str(row.get("operationId")) in preferred), None)
        if not op_row:
            op_row = _primary_op(graph, cap_id)
        meta = _op_meta(registry, str(op_row["operationId"]), str(op_row["source"])) if op_row else {}
        pol = evaluate_capability_policy(
            store,
            enterprise_id=str(enterprise["id"]),
            policy_id=str(policy["id"]),
            purpose=purpose,
            capability_id=cap_id,
            family=str(cap.get("family") or (fam or {}).get("familyGroup")),
        )
        cfg_row = configured_caps.get(cap_id) or {"action": "SKIP", "reason": "Not configured for this guided scenario."}
        action = str(cfg_row.get("action") or "SKIP")
        if action == "CALL" and pol.get("result") not in {"PERMITTED", "YES"}:
            action = "FILTER"
        state = _action_to_state(action)
        op_id = str((op_row or {}).get("operationId") or "")
        why = str(cfg_row.get("reason") or pol.get("detail") or "")
        policies.append(
            PolicyEvaluation(
                f"pol-{cap_id}",
                "CAPABILITY_API",
                cap_id,
                pol.get("result") or action,
                "CONFIGURED POLICY",
                why,
            )
        )
        decisions.append(
            Decision(
                id=f"dec-{cap_id}",
                capabilityId=cap_id,
                familyId=(fam or {}).get("id"),
                operationId=op_id or None,
                label=cap.get("label") or cap_id,
                relevant=True,
                availability="YES" if op_row else "NO",
                policyResult=str(pol.get("result") or "PERMITTED"),
                state=state,
                why=why,
                stage="CAPABILITY_API",
            )
        )
        if op_row:
            finder_ops.append(
                {
                    "capabilityId": cap_id,
                    "capability": cap.get("label"),
                    "operationId": op_id,
                    "family": (fam or {}).get("label"),
                    "available": True,
                    "provider": provider_label,
                    "action": action,
                }
            )
        if action == "CALL" and op_row:
            sim = sim_block.get(op_id) or {}
            _append_network_invocation(
                invocations=invocations,
                evidence=evidence,
                route_records=[],
                op_id=op_id,
                inv_id=f"inv-{op_id}",
                meta=meta,
                fam=fam or {},
                route_cfg=network_routes.get(op_id) or {},
                corr_id=str(corr.get("correlationId") or ""),
                sim=sim,
                op_row=op_row,
                purpose_id=str(purpose["id"]),
            )
        if cap_id in step_by_cap:
            step_by_cap[cap_id].state = "INVOKED" if action == "CALL" else state
            step_by_cap[cap_id].operationId = op_id or None

    out_seed = variant.get("outcome") or {}
    outcome = Outcome(
        outcome=str(out_seed.get("outcome") or "CONTINUE"),
        confidence=float(out_seed.get("confidence") or 0.9),
        recommendedAction=str(out_seed.get("recommendedAction") or ""),
        decisionOwner=str(out_seed.get("decisionOwner") or enterprise.get("label") or "ENTERPRISE"),
        reasonCodes=list(out_seed.get("reasonCodes") or []),
        summary=str(out_seed.get("summary") or cfg.get("close") or ""),
    )

    autonomy = dict(cfg.get("autonomy") or {})
    autonomy.setdefault("source", "CONFIGURED POLICY")
    if "NOT_AUTHORIZED" in {str(v) for v in autonomy.values()}:
        denied = [k for k, v in autonomy.items() if v == "NOT_AUTHORIZED"]
        for action_id in denied:
            policies.append(
                PolicyEvaluation(
                    f"pol-auto-{action_id}",
                    "AUTONOMY_ACTION",
                    action_id,
                    "NOT_AUTHORIZED",
                    "CONFIGURED POLICY",
                    f"Agent is not authorized to {action_id.replace('_', ' ')}.",
                )
            )

    selected_route = None
    for inv in invocations:
        if (inv.apiKind or "NETWORK") == "NETWORK":
            selected_route = {
                "type": inv.routeType,
                "display": inv.routeDisplay or f"NetAware → {inv.providerLabel}",
                "aggregatorLabel": inv.aggregatorLabel,
                "note": "Guided interpreter uses configured DIRECT or AGGREGATED routes.",
            }
            break
    if not selected_route:
        selected_route = {"type": "DIRECT", "display": f"NetAware → {provider_label}", "note": "Configured."}

    t = 0
    beats = [
        Beat(1, t, "ENTERPRISE AGENT", "BUSINESS_EVENT", "Business event", str(cfg.get("businessEvent") or intent.get("label")), "agent"),
        Beat(2, t := t + 400, "NETAWARE AX", "INTENT_RECEIVED", "Intent", intent_id, "netaware"),
        Beat(3, t := t + 400, "CONTEXT / POLICY", "CONFIGURED_CONTEXT", "Configured / onboarded context", f"{enterprise.get('label')} · {application.get('label')}", "policy"),
        Beat(4, t := t + 400, "NETAWARE AX", "CANDIDATE_GENERATION", "Candidate generation", f"{len(configured_caps)} configured capabilities", "netaware"),
        Beat(5, t := t + 400, "CONTEXT / POLICY", "POLICY", "Policy / entitlement / purpose", str(purpose.get("audienceLabel") or purpose.get("label")), "policy"),
        Beat(6, t := t + 400, "API CATALOG / FINDERS", "TELCO_FINDER", "Telco Finder", provider_label if telco else "Not required", "finder"),
        Beat(7, t := t + 400, "API CATALOG / FINDERS", "API_FINDER", "API Finder", f"{len(finder_ops)} catalog operations", "finder"),
        Beat(8, t := t + 400, "NETWORK PROVIDER", "PROVIDER_ROUTE", "Provider / route", str(selected_route.get("display")), "provider"),
    ]
    nbeat = 9
    for dec in decisions:
        if dec.state == "SELECTED":
            beats.append(Beat(nbeat, t := t + 400, "NETWORK PROVIDER", "INVOKED", str(dec.operationId or dec.capabilityId), dec.why, "provider"))
            nbeat += 1
    beats.append(Beat(nbeat, t + 400, "ENTERPRISE AGENT", "OUTCOME", outcome.outcome, outcome.summary, "agent"))

    visual = dict(cfg.get("visual") or {})
    visual.update(
        {
            "maturity": "GUIDED",
            "complexity": cfg.get("complexity"),
            "axBehavior": cfg.get("axBehavior"),
            "variantId": variant_id,
            "decisionGap": cfg.get("decisionGap"),
            "networkContribution": cfg.get("networkContribution"),
            "interpreter": "SHARED_GUIDED_INTERPRETER",
            "noCustomRunner": True,
        }
    )

    blocked = sum(1 for d in decisions if d.state == "BLOCKED_BY_POLICY")
    skipped = sum(1 for d in decisions if d.state == "NOT_REQUIRED")
    invoked_net = [i for i in invocations if (i.apiKind or "NETWORK") == "NETWORK"]

    return ExecutionTrace(
        executionId=str(corr.get("executionId") or f"ax-guided-{intent_id}"),
        traceId=str(corr.get("traceId") or f"ax-guided-{intent_id}-trace"),
        correlationId=str(corr.get("correlationId") or intent_id),
        intentId=intent_id,
        status="COMPLETED",
        request=req_body,
        knownFromConfiguration={
            "source": "FROM ONBOARDING / CONFIGURATION",
            "note": "CONFIGURED / ONBOARDED CONTEXT. Not a runtime request payload. TMF931 labels are used only where mapped.",
            "rows": [
                {"label": "Enterprise", "value": enterprise.get("label"), "tmf931": "Party / related party (mapped)"},
                {"label": "Application", "value": application.get("label"), "tmf931": "Product / application (mapped)"},
                {"label": "Authorized Agent", "value": agent.get("label"), "tmf931": "AX extension — not TMF931-standard"},
                {"label": "Domain", "value": (domain or {}).get("label")},
                {"label": "Use case", "value": (use_case or {}).get("label")},
                {"label": "Allowed intents", "value": ", ".join(agent.get("allowedIntents") or [])},
                {"label": "Purpose", "value": purpose.get("audienceLabel") or purpose.get("label")},
                {"label": "DPV", "value": ((purpose.get("dpv") or {}).get("id") if not (purpose.get("dpv") or {}).get("needsReview") else "NEEDS_REVIEW")},
                {"label": "Region", "value": cfg.get("region") or "Configured"},
                {"label": "Policy", "value": policy.get("label")},
                {"label": "Agreement / DPA", "value": policy.get("agreementId")},
                {"label": "Autonomy", "value": autonomy.get("note") or "Configured"},
            ],
        },
        purpose={
            "id": purpose.get("id"),
            "label": purpose.get("audienceLabel") or purpose.get("label"),
            "dpv": (purpose.get("dpv") or {}).get("id"),
            "dpvNeedsReview": bool((purpose.get("dpv") or {}).get("needsReview")),
            "source": "CONFIGURED APPLICATION / INTENT PROFILE",
            "note": "Business View uses the human-readable purpose. DPV is Technical View only when validated.",
        },
        actor={"agent": agent, "application": application, "enterprise": enterprise, "kind": "AUTHORIZED_AGENT"},
        telcoFinder=telco,
        apiFinder={
            "neededBecause": "API Finder resolves catalog availability. Guided configuration decides CALL / SKIP / FILTER.",
            "network": provider_label,
            "results": finder_ops,
            "simulated": True,
        },
        route=selected_route,
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
            "invoked": len(invoked_net),
            "blockedByPolicy": blocked,
            "consideredNotRequired": skipped,
            "note": "Guided interpreter. Catalog availability ≠ permission ≠ need.",
        },
        beats=beats,
        honesty={
            "simulated": True,
            "liveOperators": False,
            "policyIsConfiguredDemo": True,
            "dataMinimization": True,
            "guidedInterpreter": True,
            "noCustomRunner": True,
        },
        guidedVisual=visual,
    )
