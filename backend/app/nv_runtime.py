"""Cadence 9 — Number Verification path selection.

One executable Intent (`verify_mobile_number`) and one runner.
Three deterministic seeds change access type / operator readiness, not the Intent.
NV1/NV2 are fulfillment paths. phoneNumberVerify / phoneNumberShare are operations.
"""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from .model import ConfigStore
from .graph import KnowledgeGraph
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

WIFI_KINDS = {"WIFI", "WLAN", "VPN"}
NV_VARIANTS = ("cellular-nv1", "wifi-nv2", "wifi-ecs-gap")

SUPPLY_SIDE = [
    {
        "providerId": "simulated-operator-a",
        "label": "Network Provider A",
        "numberVerification": "AVAILABLE",
        "nv1": True,
        "nv2": True,
        "ecs": "AVAILABLE",
        "note": "NV2 ready",
    },
    {
        "providerId": "simulated-operator-b",
        "label": "Network Provider B",
        "numberVerification": "AVAILABLE",
        "nv1": True,
        "nv2": True,
        "ecs": "UNAVAILABLE",
        "note": "NV API available. ECS unavailable.",
    },
    {
        "providerId": "simulated-provider-c",
        "label": "Specialist Provider C",
        "numberVerification": "UNAVAILABLE",
        "nv1": False,
        "nv2": False,
        "ecs": "UNAVAILABLE",
        "note": "Number Verification unavailable",
    },
]


def resolve_nv_variant(request: dict[str, Any], seed: dict[str, Any]) -> str:
    ctx = request.get("context") or {}
    raw = str(ctx.get("nvVariant") or ctx.get("accessProviderScenario") or "").strip()
    if raw in NV_VARIANTS:
        return raw
    access = str(ctx.get("accessType") or "").upper().replace("-", "")
    if access in WIFI_KINDS:
        ecs = str(ctx.get("ecsAvailable") or ctx.get("entitlementServer") or "").upper()
        if ecs in {"UNAVAILABLE", "NO", "FALSE"} or ctx.get("wifiEcsGap"):
            return "wifi-ecs-gap"
        return "wifi-nv2"
    if access == "CELLULAR":
        return "cellular-nv1"
    return str(seed.get("defaultVariant") or "cellular-nv1")


def _operator_readiness(store: ConfigStore, provider_id: str) -> dict[str, Any]:
    for row in (store.operator_readiness or {}).get("operators") or []:
        if row.get("providerId") == provider_id:
            return row
    return {}


def _evaluate_paths(
    access_type: str,
    readiness: dict[str, Any],
    prereqs: dict[str, Any],
) -> dict[str, Any]:
    access = "WIFI" if access_type.upper().replace("-", "") in {"WIFI", "WLAN", "VPN"} else "CELLULAR"
    nv1_supported = bool(readiness.get("nv1Supported"))
    nv2_supported = bool(readiness.get("nv2Supported"))
    ecs = str((readiness.get("entitlementServer") or {}).get("available") or "UNKNOWN")
    ts43 = bool(prereqs.get("ts43ClientAvailable"))
    sim = bool(prereqs.get("simAvailable"))

    nv1: dict[str, Any] = {
        "id": "NV1_NETWORK_BASED",
        "label": "Network-based Number Verification",
        "productLabel": "NV1",
        "operatorSupport": nv1_supported,
    }
    if access == "WIFI":
        nv1.update(
            {
                "result": "FILTERED",
                "reasonCode": "ACCESS_TYPE_INCOMPATIBLE",
                "humanReason": "NV1 needs cellular access so the operator can identify the subscription from the network. Wi-Fi cannot silently use NV1.",
            }
        )
    elif nv1_supported:
        nv1.update({"result": "CANDIDATE", "reasonCode": None, "humanReason": "Cellular access and operator NV1 support."})
    else:
        nv1.update(
            {
                "result": "FILTERED",
                "reasonCode": "OPERATOR_NOT_SUPPORTED",
                "humanReason": "This operator does not support the NV1 network-based path.",
            }
        )

    nv2: dict[str, Any] = {
        "id": "NV2_OPERATOR_TOKEN",
        "label": "Operator-token Number Verification",
        "productLabel": "NV2",
        "operatorSupport": nv2_supported,
    }
    if not nv2_supported:
        nv2.update(
            {
                "result": "FILTERED",
                "reasonCode": "OPERATOR_NOT_SUPPORTED",
                "humanReason": "This operator does not support the NV2 operator-token path.",
            }
        )
    elif access == "WIFI" and ecs != "AVAILABLE":
        nv2.update(
            {
                "result": "FILTERED",
                "reasonCode": "ENTITLEMENT_SERVER_UNAVAILABLE",
                "humanReason": "NV2 is in the operator product profile, but the Entitlement Server is unavailable. No fake NV1 over Wi-Fi. No SMS OTP fallback.",
            }
        )
    elif access == "WIFI" and (not ts43 or not sim):
        nv2.update(
            {
                "result": "FILTERED",
                "reasonCode": "TECHNICAL_PREREQUISITE_MISSING",
                "humanReason": "TS.43 client or SIM prerequisite is missing for the operator-token path.",
            }
        )
    elif access == "CELLULAR":
        nv2.update(
            {
                "result": "NOT_REQUIRED",
                "reasonCode": "NOT_REQUIRED",
                "humanReason": "NV2 may be available, but NV1 is the simplest feasible path on cellular.",
            }
        )
    else:
        nv2.update(
            {
                "result": "CANDIDATE",
                "reasonCode": None,
                "humanReason": "Wi-Fi access, NV2 supported, Entitlement Server available, TS.43/SIM present.",
            }
        )

    selected = None
    if nv1.get("result") == "CANDIDATE":
        selected = "NV1_NETWORK_BASED"
        nv1["result"] = "SELECTED"
        nv1["reasonCode"] = "SELECTED"
        nv1["humanReason"] = "Simplest feasible path: cellular + NV1."
    elif nv2.get("result") == "CANDIDATE":
        selected = "NV2_OPERATOR_TOKEN"
        nv2["result"] = "SELECTED"
        nv2["reasonCode"] = "SELECTED"
        nv2["humanReason"] = "NV1 filtered on Wi-Fi. NV2 operator-token path is ready."

    return {
        "accessType": access,
        "nv1": nv1,
        "nv2": nv2,
        "selectedPath": selected,
        "ecs": ecs,
        "ts43ClientAvailable": ts43,
        "simAvailable": sim,
        "nv1Supported": nv1_supported,
        "nv2Supported": nv2_supported,
    }


def run_verify_mobile_number(
    store: ConfigStore,
    graph: KnowledgeGraph,
    registry: CatalogRegistry,
    request: dict[str, Any],
) -> ExecutionTrace:
    from .runtime import (
        _family_for,
        _op_meta,
        _primary_op,
        _provider_ops,
        evaluate_capability_policy,
        load_scenario,
    )

    intent_id = str(request.get("intent") or "verify_mobile_number")
    seed = load_scenario(intent_id).get("scenario") or {}
    variant_id = resolve_nv_variant(request, seed)
    variant = (seed.get("variants") or {}).get(variant_id)
    if not variant:
        raise HTTPException(status_code=400, detail=f"Unknown NV variant: {variant_id}")

    agent_id = str(request.get("agentId") or seed.get("agentId"))
    agent = store.agent_by_id.get(agent_id)
    if not agent:
        raise HTTPException(status_code=403, detail="Unknown agent")
    if intent_id not in (agent.get("allowedIntents") or []):
        raise HTTPException(status_code=403, detail="Agent is not authorized for this intent")

    application = store.application_by_id.get(str(agent.get("actsOnBehalfOf") or seed.get("applicationId") or ""))
    enterprise = store.enterprise_by_id.get(str(agent.get("enterpriseId") or ""))
    if not application or not enterprise:
        raise HTTPException(status_code=403, detail="Agent application/enterprise not resolved")

    intent = store.intent_by_id.get(intent_id) or {}
    uc_id = graph.intent_use_case.get(intent_id)
    use_case = store.use_case_by_id.get(uc_id or "")
    policy = next((p for p in store.policies if p.get("id") == seed.get("policyId")), None)
    if not policy:
        raise HTTPException(status_code=500, detail="Scenario policy missing")
    purpose = store.purpose_by_id.get(str(policy.get("purposeId") or intent.get("defaultPurposeId") or ""))
    if not purpose:
        raise HTTPException(status_code=500, detail="Purpose not resolved from configuration")

    corr = variant.get("correlation") or {}
    access_type = str(variant.get("accessType") or "CELLULAR")
    provider_id = str(variant.get("selectedProviderId"))
    provider_label = str(variant.get("providerAudienceLabel") or "Network Provider A")
    readiness = _operator_readiness(store, provider_id)
    prereqs = variant.get("technicalPrerequisites") or {}
    paths = _evaluate_paths(access_type, readiness, prereqs)
    selected_path = paths["selectedPath"]
    claimed = bool((request.get("context") or {}).get("claimedMsisdn", True))
    selected_operation = "phoneNumberVerify" if selected_path and claimed else None
    share_state = "NOT_REQUIRED"
    share_why = "Claimed MSISDN is present. CAMARA operation is phoneNumberVerify. phoneNumberShare is not NV2."

    req_body = {
        "intent": intent_id,
        "subject": (request.get("subject") or seed.get("request", {}).get("subject")),
        "context": {
            **(seed.get("request", {}).get("context") or {}),
            **(request.get("context") or {}),
            "nvVariant": variant_id,
            "accessType": access_type,
            "accessTypeSource": "RUNTIME_CLIENT_CONTEXT",
            "claimedMsisdn": claimed,
            "businessEvent": "CUSTOMER_SIGNING_IN",
        },
    }

    advertised = _provider_ops(store, provider_id)
    nv_available = "phoneNumberVerify" in advertised
    cap_id = "number_possession_verification"
    fam = _family_for(registry, cap_id)
    op_row = _primary_op(graph, cap_id)
    meta = _op_meta(registry, str(op_row["operationId"]), str(op_row["source"])) if op_row else {}
    pol = evaluate_capability_policy(
        store,
        enterprise_id=str(enterprise["id"]),
        policy_id=str(policy["id"]),
        purpose=purpose,
        capability_id=cap_id,
        family=str((fam or {}).get("familyGroup") or "IDENTITY_AND_TRUST"),
    )

    telco = dict(variant.get("telcoFinder") or {})
    telco["accessTypeNote"] = "Access type is SIMULATED ACCESS CONTEXT. Telco Finder does not determine Wi-Fi vs cellular."
    api_finder = {
        "network": provider_label,
        "note": "API Finder answers whether this provider offers Number Verification. It does not decide NV1 vs NV2 or ECS readiness.",
        "results": [
            {
                "capabilityId": cap_id,
                "operationId": "phoneNumberVerify",
                "available": nv_available,
                "providerId": provider_id,
                "providerLabel": provider_label,
            },
            {
                "capabilityId": cap_id,
                "operationId": "phoneNumberShare",
                "available": "phoneNumberShare" in advertised,
                "providerId": provider_id,
                "providerLabel": provider_label,
                "note": "Available is not selected. Claimed MSISDN uses verify, not share.",
            },
        ],
    }

    route_type = "DIRECT"
    blocking_gap = None
    if not selected_path and paths["nv2"].get("reasonCode") == "ENTITLEMENT_SERVER_UNAVAILABLE":
        blocking_gap = "Entitlement Server unavailable"
    elif not selected_path:
        blocking_gap = paths["nv2"].get("humanReason") or paths["nv1"].get("humanReason") or "No feasible Number Verification path"

    fulfilled = bool(selected_path and selected_operation)
    invocations: list[Invocation] = []
    evidence: list[Evidence] = []
    if fulfilled and op_row:
        sim = (variant.get("simulatedResponses") or {}).get(selected_operation) or {}
        invocations.append(
            Invocation(
                id=f"inv-{selected_operation}",
                operationId=selected_operation,
                source=str(op_row["source"]),
                familyId=str((fam or {}).get("id") or meta.get("api_id") or "number-verification"),
                familyLabel=str((fam or {}).get("label") or "Number Verification"),
                specMaturity=str(meta.get("spec_maturity") or ""),
                businessStatus=str(meta.get("business_status") or ""),
                method=str(meta.get("method") or "POST"),
                providerId=provider_id,
                providerLabel=provider_label,
                routeType=route_type,
                correlationId=str(corr.get("correlationId")),
                latencyMs=int(sim.get("latencyMs") or 40),
                httpStatus=int(sim.get("httpStatus") or 200),
                raw=sim.get("raw") or {"devicePhoneNumberVerified": True},
                simulated=True,
            )
        )
        ev = sim.get("evidence") or {"type": "NUMBER_POSSESSION", "status": "verified"}
        evidence.append(
            Evidence(
                id=f"ev-{selected_operation}",
                operationId=selected_operation,
                type=str(ev.get("type") or "NUMBER_POSSESSION"),
                status=str(ev.get("status") or "verified"),
                payload={k: v for k, v in ev.items() if k not in {"type"}},
                purposeId=str(purpose["id"]),
            )
        )

    cap_state = "INVOKED" if fulfilled else "UNAVAILABLE"
    cap_why = (
        f"Number Verification selected via {selected_path}. Operation {selected_operation} because a claimed MSISDN is present."
        if fulfilled
        else f"Number Verification is eligible and the API is available, but no feasible path remains. {blocking_gap}."
    )
    decisions = [
        Decision(
            id="dec-number_possession_verification",
            capabilityId=cap_id,
            familyId=(fam or {}).get("id"),
            operationId=selected_operation or "phoneNumberVerify",
            label="Number possession verification",
            relevant=True,
            availability="YES" if nv_available else "NO",
            policyResult=pol["result"],
            state=cap_state,
            why=cap_why,
            stage="SELECT",
            reasonCode="SELECTED" if fulfilled else (paths["nv2"].get("reasonCode") or paths["nv1"].get("reasonCode") or "OPERATOR_NOT_SUPPORTED"),
            pathId=selected_path,
        ),
    ]

    policies = [
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
            "Intent verify_mobile_number is in the agent's allowedIntents. The application did not request NV1, NV2, TS.43, ECS, or a CAMARA operationId.",
        ),
        PolicyEvaluation(
            "pol-actor-purpose",
            "ACTOR_INTENT",
            "purpose",
            "RESOLVED_FROM_CONFIGURATION",
            "CONFIGURED POLICY",
            f"Purpose {(purpose.get('audienceLabel') or purpose.get('label'))} resolved from application/intent policy.",
        ),
        PolicyEvaluation(
            "pol-cap-number_possession_verification",
            "CAPABILITY_API",
            cap_id,
            pol["result"],
            "CONFIGURED POLICY",
            pol["detail"],
        ),
        PolicyEvaluation(
            "pol-path-nv1",
            "RUNTIME_FEASIBILITY",
            "NV1_NETWORK_BASED",
            paths["nv1"]["result"],
            "CONFIGURED OPERATOR READINESS",
            paths["nv1"]["humanReason"],
        ),
        PolicyEvaluation(
            "pol-path-nv2",
            "RUNTIME_FEASIBILITY",
            "NV2_OPERATOR_TOKEN",
            paths["nv2"]["result"],
            "CONFIGURED OPERATOR READINESS",
            paths["nv2"]["humanReason"],
        ),
    ]

    plan = Plan(
        id=f"plan-rb-nv-{variant_id}",
        intentId=intent_id,
        executionId=str(corr.get("executionId")),
        label="Number Verification path selection",
        note="Path (how the subscriber is bound) is selected independently of operation (verify vs share).",
        steps=[
            PlanStep(1, "Receive verify_mobile_number Intent", None, None, state="COMPLETED"),
            PlanStep(2, f"Read access type from runtime context ({access_type})", None, None, state="COMPLETED"),
            PlanStep(3, f"Telco Finder → {provider_label}", None, None, state="COMPLETED"),
            PlanStep(4, "API Finder → Number Verification availability", cap_id, "phoneNumberVerify", state="COMPLETED"),
            PlanStep(5, "Evaluate NV1 network-based path", None, None, state=paths["nv1"]["result"]),
            PlanStep(6, "Evaluate NV2 operator-token path", None, None, state=paths["nv2"]["result"]),
            PlanStep(
                7,
                "Select CAMARA operation from claim shape",
                cap_id,
                selected_operation,
                state="COMPLETED" if selected_operation else "UNAVAILABLE",
            ),
            PlanStep(8, "Return number verification outcome", None, None, state="COMPLETED"),
        ],
    )

    if fulfilled:
        outcome = Outcome(
            outcome="VERIFIED",
            confidence=0.92,
            recommendedAction="CONTINUE_SIGN_IN",
            decisionOwner="Rocket Bank IAM",
            reasonCodes=["NUMBER_POSSESSION_VERIFIED", selected_path or ""],
            summary="Claimed mobile number verified by the selected Number Verification path. Rocket Bank owns the application session.",
            networkTrust="verified",
            verification="PASSED",
        )
        commercial = None
        demand_class = "FULFILLED_QUALIFIED_DEMAND"
    else:
        outcome = Outcome(
            outcome="CAPABILITY_UNAVAILABLE",
            confidence=0.9,
            recommendedAction="USE_ENTERPRISE_IAM_ALTERNATE",
            decisionOwner="Rocket Bank IAM",
            reasonCodes=[paths["nv2"].get("reasonCode") or "OPERATOR_NOT_SUPPORTED"],
            summary=(
                "Qualified Number Verification demand could not be fulfilled. "
                "NV1 is incompatible with Wi-Fi. NV2 requires an Entitlement Server that is unavailable. "
                "NetAware does not invent SMS OTP or a fake NV1 path. The enterprise owns any alternate IAM path."
            ),
            limitingFactor=blocking_gap or "Entitlement Server unavailable",
        )
        commercial = (
            "This application demand could not be fulfilled through the required "
            "Wi-Fi Number Verification path."
        )
        demand_class = "UNFULFILLED_QUALIFIED_DEMAND"

    path_selection = {
        "accessType": access_type,
        "accessTypeSource": "RUNTIME_CLIENT_CONTEXT",
        "accessTypeHonesty": "SIMULATED ACCESS CONTEXT",
        "telcoFinder": {
            "providerId": provider_id,
            "provider": provider_label,
            "role": "Which operator / network profile applies?",
            "doesNotDetermineAccessType": True,
        },
        "apiFinder": {
            "numberVerificationAvailable": nv_available,
            "role": "Does this provider offer Number Verification?",
            "distinctFrom": ["NV1/NV2 path support", "ECS readiness"],
        },
        "operatorReadiness": {
            "source": "CONFIGURED_OPERATOR_READINESS",
            "nv1Supported": paths["nv1Supported"],
            "nv2Supported": paths["nv2Supported"],
            "entitlementServer": ecs_state(paths["ecs"]),
            "honesty": "CONFIGURED OPERATOR READINESS",
        },
        "technicalPrerequisites": {
            "ts43ClientAvailable": paths["ts43ClientAvailable"],
            "simAvailable": paths["simAvailable"],
            "tokenPathState": prereqs.get("tokenPathState"),
            "honesty": "SIMULATED / CONCEPTUAL PATH",
        },
        "paths": [paths["nv1"], paths["nv2"]],
        "selectedPath": selected_path,
        "selectedOperation": selected_operation,
        "operations": [
            {
                "operationId": "phoneNumberVerify",
                "job": "claimed_msisdn_match",
                "result": "SELECTED" if selected_operation == "phoneNumberVerify" else "SKIPPED",
                "reasonCode": "SELECTED" if selected_operation == "phoneNumberVerify" else None,
                "humanReason": "Claimed MSISDN is present — verify, not share.",
            },
            {
                "operationId": "phoneNumberShare",
                "job": "return_network_bound_msisdn",
                "result": "SKIPPED",
                "reasonCode": "NOT_REQUIRED",
                "humanReason": share_why,
            },
        ],
        "claimShape": "claimed_msisdn" if claimed else "network_bound_msisdn_needed",
        "operationNote": "Path is how the subscriber is authenticated/bound. Operation is what Number Verification is asked to do.",
        "forbidden": [
            "Fake NV1 over Wi-Fi",
            "SMS OTP as an AX Number Verification fallback",
            "NV1 = phoneNumberVerify",
            "NV2 = phoneNumberShare",
        ],
        "tokenFlowConceptual": (
            [
                {"id": "DEVICE", "label": "Device"},
                {"id": "TS43", "label": "TS.43 / Entitlement Server"},
                {"id": "TOKEN", "label": "Operator token"},
                {"id": "AUTH", "label": "Authorization"},
                {"id": "NV", "label": "Number Verification"},
            ]
            if selected_path == "NV2_OPERATOR_TOKEN" or variant_id != "cellular-nv1"
            else None
        ),
        "supplySide": SUPPLY_SIDE,
        "variantId": variant_id,
        "variantLabel": variant.get("label"),
    }

    network_opportunity = {
        "title": "See network opportunity",
        "businessDemand": "Number Verification",
        "businessDemandQualified": True,
        "qualified": True,
        "provider": provider_label,
        "providerId": provider_id,
        "route": route_type,
        "capability": cap_id,
        "numberVerificationApi": "AVAILABLE" if nv_available else "UNAVAILABLE",
        "fulfilled": fulfilled,
        "demandFulfilled": fulfilled,
        "path": selected_path,
        "networkApiInvocations": len(invocations),
        "networkApiConsumption": (
            f"{len(invocations)} Number Verification invocation" if fulfilled else "0 Number Verification invocations"
        ),
        "blockingReadinessGap": blocking_gap,
        "demandClass": demand_class,
        "commercialMessage": commercial,
        "noRevenue": True,
        "enterpriseValue": (
            "My application asked to verify a number. I did not code separate cellular and Wi-Fi "
            "Network API flows. NetAware selected the feasible network path."
        ),
        "operatorValue": (
            "My Network API may be commercially available, but infrastructure readiness determines "
            "whether actual demand can be served."
        ),
        "close": {
            "application": "One Intent. No NV1/NV2 integration logic.",
            "network": "Operator readiness determines whether demand can be fulfilled.",
            "ax": "NetAware AX connects business demand to the Network API path that can actually serve it.",
        },
    }

    nv_visual = _visual(variant_id, access_type, paths, selected_path, fulfilled)

    known = {
        "source": "FROM ONBOARDING / CONFIGURATION",
        "note": "You do not send this on every request. NetAware already has it from onboarding.",
        "rows": [
            {"label": "Enterprise", "value": enterprise.get("label")},
            {"label": "Application", "value": application.get("label")},
            {"label": "Use case", "value": "Digital Identity / IAM — passwordless mobile sign-in"},
            {"label": "Adjacent use case", "value": "Payments Risk still uses assess_network_trust"},
            {"label": "Purpose", "value": purpose.get("audienceLabel") or purpose.get("label")},
            {"label": "Region", "value": "CA"},
            {"label": "Subscription", "value": "IDENTITY_AND_TRUST (enterprise)"},
            {"label": "Entitlement", "value": "Digital Identity / IAM application"},
        ],
    }

    autonomy = {
        "observe": "ALLOWED",
        "recommend": "ALLOWED",
        "act": "ALLOWED for Number Verification invocation",
        "notAuthorized": ["issue_application_session"],
        "note": "Enterprise IAM owns the application session. NetAware returns verification outcome only.",
    }

    beats = _beats(
        agent=agent,
        application=application,
        access_type=access_type,
        provider_label=provider_label,
        paths=paths,
        selected_path=selected_path,
        selected_operation=selected_operation,
        fulfilled=fulfilled,
        blocking_gap=blocking_gap,
    )

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
            "mappedToIntent": 1,
            "selected": 1 if fulfilled else 0,
            "invoked": len(invocations),
            "evidenceReused": 0,
            "consideredNotRequired": 1,
            "notRequiredUnmapped": 0,
            "blockedByPolicy": 0,
        },
        beats=beats,
        honesty={
            "simulated": True,
            "liveOperators": False,
            "policyIsConfiguredDemo": True,
            "dataMinimization": True,
            "accessType": "SIMULATED ACCESS CONTEXT",
            "operatorReadiness": "CONFIGURED OPERATOR READINESS",
            "operatorResponse": "SIMULATED OPERATOR RESPONSE",
            "ecsNotCamaraApi": True,
            "ecsNotInApiCatalog": True,
            "noSmsOtpFallback": True,
            "noFakeNv1OnWifi": True,
            "telcoFinderDoesNotDetermineAccessType": True,
            "apiFinderDistinctFromEcs": True,
            "pathDistinctFromOperation": True,
            "tokenFlow": "SIMULATED / CONCEPTUAL PATH",
        },
        pathSelection=path_selection,
        networkOpportunity=network_opportunity,
        nvVisual=nv_visual,
        demandSupply={
            "businessDemandQualified": True,
            "demandFulfilled": fulfilled,
            "provider": provider_label,
            "route": route_type,
            "capability": cap_id,
            "path": selected_path,
            "blockingReadinessGap": blocking_gap,
            "networkApiInvocations": len(invocations),
        },
    )


def ecs_state(value: str) -> dict[str, Any]:
    return {
        "available": value,
        "source": "CONFIGURED_OPERATOR_READINESS",
        "notACamaraApi": True,
        "notDiscoveredViaStandardizedApi": True,
    }


def _visual(variant_id: str, access_type: str, paths: dict[str, Any], selected_path: str | None, fulfilled: bool) -> dict[str, Any]:
    nv1 = paths["nv1"]
    nv2 = paths["nv2"]
    if variant_id == "cellular-nv1":
        headline = "SAME INTENT. NETAWARE SELECTS THE SIMPLEST FEASIBLE PATH."
        steps = [
            {"id": "access", "label": "CELLULAR", "state": "ok"},
            {"id": "identity", "label": "NETWORK-BASED IDENTITY", "state": "ok"},
            {"id": "nv1", "label": "NV1", "state": "ok"},
            {"id": "out", "label": "NUMBER VERIFIED", "state": "ok"},
        ]
    elif variant_id == "wifi-nv2":
        headline = "SAME APPLICATION. SAME INTENT. DIFFERENT FULFILLMENT. NO APPLICATION INTEGRATION CHANGE."
        steps = [
            {"id": "access", "label": "WI-FI", "state": "ok"},
            {"id": "nv1", "label": "NV1", "state": "filtered", "detail": "ACCESS_TYPE_INCOMPATIBLE"},
            {"id": "nv2", "label": "NV2 CANDIDATE", "state": "ok"},
            {"id": "ecs", "label": "ENTITLEMENT SERVER", "state": "ok"},
            {"id": "token", "label": "OPERATOR TOKEN PATH", "state": "ok"},
            {"id": "out", "label": "NUMBER VERIFIED", "state": "ok"},
        ]
    else:
        headline = "QUALIFIED DEMAND. OPERATOR READINESS BLOCKS FULFILLMENT."
        steps = [
            {"id": "access", "label": "WI-FI", "state": "ok"},
            {"id": "nv1", "label": "NV1", "state": "filtered", "detail": "ACCESS_TYPE_INCOMPATIBLE"},
            {"id": "nv2", "label": "NV2 CANDIDATE", "state": "warn"},
            {"id": "ecs", "label": "ENTITLEMENT SERVER", "state": "break", "detail": "UNAVAILABLE"},
            {"id": "out", "label": "CAPABILITY UNAVAILABLE", "state": "break"},
        ]
    return {
        "intentId": "verify_mobile_number",
        "intentLabel": "Verify this mobile number",
        "businessEvent": "CUSTOMER SIGNING IN",
        "headline": headline,
        "variantId": variant_id,
        "accessType": access_type,
        "steps": steps,
        "nv1": nv1,
        "nv2": nv2,
        "selectedPath": selected_path,
        "fulfilled": fulfilled,
        "comparison": {
            "cellular": ["Intent", "NV1 ✓", "Verify"],
            "wifiReady": ["Intent", "NV1 ✕", "NV2 ✓", "ECS ✓", "Verify"],
            "wifiEcsGap": ["Intent", "NV1 ✕", "NV2 candidate", "ECS ✕", "Cannot fulfill"],
        },
    }


def _beats(
    *,
    agent: dict[str, Any],
    application: dict[str, Any],
    access_type: str,
    provider_label: str,
    paths: dict[str, Any],
    selected_path: str | None,
    selected_operation: str | None,
    fulfilled: bool,
    blocking_gap: str | None,
) -> list[Beat]:
    beats = [
        Beat(1, 0, "ROCKET BANK / AGENT", "BUSINESS_EVENT", "Customer signing in", f"{application.get('label')} sends a business event — not an NV1/NV2 request.", "agent"),
        Beat(2, 350, "NETAWARE AX", "INTENT_RECEIVED", "Intent received", "verify_mobile_number — verify this mobile number.", "netaware"),
        Beat(3, 700, "CONTEXT / POLICY", "ACCESS_CONTEXT", "Simulated access context", f"{access_type}. Runtime client context. Telco Finder does not detect access type.", "policy"),
        Beat(4, 1050, "CATALOG / FINDERS", "TELCO_FINDER", "Telco Finder", f"MSISDN → {provider_label}. Which operator applies?", "finder"),
        Beat(5, 1400, "CATALOG / FINDERS", "API_FINDER", "API Finder", f"Does {provider_label} offer Number Verification? Distinct from NV path support and ECS readiness.", "finder"),
        Beat(6, 1800, "NETWORK PROVIDER", "NV1_PATH", "NV1 path", paths["nv1"]["humanReason"], "provider"),
        Beat(7, 2200, "NETWORK PROVIDER", "NV2_PATH", "NV2 path", paths["nv2"]["humanReason"], "provider"),
        Beat(8, 2600, "CONTEXT / POLICY", "OPERATOR_READINESS", "Operator readiness", "CONFIGURED OPERATOR READINESS — ECS is not a CAMARA catalog API.", "policy"),
        Beat(9, 3000, "NETAWARE AX", "OPERATION", "Operation from claim shape", "Claimed MSISDN → phoneNumberVerify. Share is not NV2.", "netaware"),
    ]
    if fulfilled:
        beats.append(Beat(10, 3400, "NETWORK PROVIDER", "INVOKED", selected_operation or "phoneNumberVerify", "SIMULATED OPERATOR RESPONSE.", "provider"))
        beats.append(Beat(11, 3800, "ROCKET BANK / AGENT", "OUTCOME", "NUMBER VERIFIED", f"Fulfilled via {selected_path}.", "agent"))
    else:
        beats.append(Beat(10, 3400, "NETAWARE AX", "UNAVAILABLE", "Cannot fulfill", f"{blocking_gap}. No fake NV1. No SMS OTP.", "netaware"))
        beats.append(Beat(11, 3800, "ROCKET BANK / AGENT", "OUTCOME", "CAPABILITY UNAVAILABLE", "Enterprise owns any alternate IAM path.", "agent"))
    return beats
