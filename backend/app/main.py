"""NetAware AX Cadence 6 — hosted single-service API + SPA."""
from __future__ import annotations

import base64
import logging
import secrets
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from .config import (
    ALLOWED_ORIGINS,
    APP_VERSION,
    BUILD_ID,
    CADENCE,
    CADENCE_PATCH,
    ENVIRONMENT,
    FRONTEND_DIST,
    LOG_LEVEL,
    MODEL_CADENCE,
    PRODUCT_BEHAVIOR_FROZEN,
    UI_CADENCE,
    demo_basic_credentials,
    serve_frontend,
)
from .demo import briefing, demo_index, enterprise_card, featured_row
from .evidence_store import list_store
from .explore_entities import (
    agent_detail,
    autonomy_index,
    enrich_capability,
    enrich_catalog_api,
    enrich_domain,
    enrich_intent,
    enrich_operation,
    enrich_use_case,
    explore_summary,
    list_agents,
    list_policies,
    list_providers,
    list_purposes,
    list_routes,
    my_context,
    policy_detail,
    provider_detail,
    purpose_detail,
)
from .graph import KnowledgeGraph
from .model import ConfigStore
from .registry import load_pin, load_registry
from .runtime import EXECUTABLE_INTENTS, execute_intent, get_execution, reset_executions

store = ConfigStore()
registry = load_registry()
graph = KnowledgeGraph(store, registry)
pin = load_pin()

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("netaware.ax")

app = FastAPI(
    title="NetAware AX",
    version=APP_VERSION,
    description="Cadence 6: presentation-ready demo freeze — clarity, pacing, traceability.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


def _unauthorized() -> Response:
    return Response(
        content='{"ok":false,"error":"Authentication required"}',
        status_code=401,
        headers={
            "Content-Type": "application/json",
            "WWW-Authenticate": 'Basic realm="NetAware AX Prototype"',
        },
    )


@app.middleware("http")
async def demo_access(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path == "/health":
        return await call_next(request)
    basic = demo_basic_credentials()
    if not basic:
        return await call_next(request)
    header = request.headers.get("authorization") or ""
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "basic" or not token:
        return _unauthorized()
    try:
        decoded = base64.b64decode(token.strip()).decode("utf-8")
        user, _, password = decoded.partition(":")
    except Exception:
        return _unauthorized()
    expected_user, expected_password = basic
    if not (
        secrets.compare_digest(user, expected_user) and secrets.compare_digest(password, expected_password)
    ):
        return _unauthorized()
    return await call_next(request)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "product": "NetAware AX",
        "environment": ENVIRONMENT,
        "cadence": CADENCE,
        "cadencePatch": CADENCE_PATCH,
        "modelCadence": MODEL_CADENCE,
        "uiCadence": UI_CADENCE,
        "version": APP_VERSION,
        "build": BUILD_ID,
        "productBehaviorFrozen": PRODUCT_BEHAVIOR_FROZEN,
        "serveFrontend": serve_frontend(),
        "basicAuthConfigured": demo_basic_credentials() is not None,
        "registryLoaded": True,
        "catalog": {
            "id": "AX_ACTIVE_CATALOG",
            "businessFamilies": len(registry.families),
            "technicalSpecs": registry.technical_spec_count(),
            "operations": len(registry.operations),
            "uniqueOperationIds": len({op.operation_id for op in registry.operations}),
            "maturityIsMetadata": True,
            "fullPinRetainedForReference": True,
            "fullPinNotExposed": True,
        },
        "executionEngine": True,
        "demoUi": True,
        "explorerProductSurface": True,
        "evidenceReuse": True,
        "executableIntents": sorted(EXECUTABLE_INTENTS),
        "pin": {
            "acquisitionDate": (pin.get("pin") or {}).get("acquisition_date"),
            "independentCopy": (pin.get("pin") or {}).get("independent_copy"),
        },
    }


@app.get("/catalog")
def catalog() -> dict[str, Any]:
    return registry.to_public()


@app.get("/catalog/apis")
def catalog_apis() -> dict[str, Any]:
    return {
        "catalog": "AX_ACTIVE_CATALOG",
        "apis": [enrich_catalog_api(store, graph, registry, str(api["id"])) for api in registry.apis],
    }


@app.get("/catalog/apis/{api_id}")
def catalog_api(api_id: str) -> dict[str, Any]:
    body = enrich_catalog_api(store, graph, registry, api_id)
    if not body.get("api"):
        raise HTTPException(status_code=404, detail=f"Unknown active API: {api_id}")
    return body


@app.get("/catalog/{operation_id}")
def catalog_operation(operation_id: str) -> dict[str, Any]:
    reverse = enrich_operation(store, graph, operation_id)
    if not reverse.get("catalogVariants"):
        raise HTTPException(status_code=404, detail=f"Unknown active operationId: {operation_id}")
    return reverse


@app.get("/domains")
def domains() -> dict[str, Any]:
    return {"domains": store.domains}


@app.get("/domains/{domain_id}")
def domain_detail(domain_id: str) -> dict[str, Any]:
    if domain_id not in store.domain_by_id:
        raise HTTPException(status_code=404, detail=f"Unknown domain: {domain_id}")
    return enrich_domain(store, graph, registry, domain_id)


@app.get("/intents")
def intents() -> dict[str, Any]:
    return {"intents": store.intents}


@app.get("/intents/{intent_id}")
def intent_detail(intent_id: str) -> dict[str, Any]:
    if intent_id not in store.intent_by_id:
        raise HTTPException(status_code=404, detail=f"Unknown intent: {intent_id}")
    return enrich_intent(store, graph, registry, intent_id)


@app.get("/capabilities")
def capabilities() -> dict[str, Any]:
    return {"capabilities": store.capabilities}


@app.get("/capabilities/{capability_id}")
def capability_detail(capability_id: str) -> dict[str, Any]:
    body = enrich_capability(store, graph, registry, capability_id)
    if not body.get("capability"):
        raise HTTPException(status_code=404, detail=f"Unknown capability: {capability_id}")
    return body


@app.get("/enterprises")
def enterprises() -> dict[str, Any]:
    return {"enterprises": [enterprise_card(store, str(e["id"])) for e in store.enterprises]}


@app.get("/enterprises/{enterprise_id}")
def enterprise_detail(enterprise_id: str) -> dict[str, Any]:
    card = enterprise_card(store, enterprise_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"Unknown enterprise: {enterprise_id}")
    featured = next(
        (row for row in (store.demo or {}).get("featuredEnterprises") or [] if row.get("enterpriseId") == enterprise_id),
        None,
    )
    if featured:
        return featured_row(store, featured)
    return card


@app.get("/use-cases")
def use_cases() -> dict[str, Any]:
    return {"useCases": store.use_cases}


@app.get("/use-cases/{use_case_id}")
def use_case_detail(use_case_id: str) -> dict[str, Any]:
    body = enrich_use_case(store, graph, registry, use_case_id)
    if not body.get("useCase"):
        raise HTTPException(status_code=404, detail=f"Unknown use case: {use_case_id}")
    return body


@app.get("/demo")
def demo() -> dict[str, Any]:
    return demo_index(store)


@app.get("/demo/{enterprise_id}")
def demo_enterprise(enterprise_id: str) -> dict[str, Any]:
    featured = next(
        (row for row in (store.demo or {}).get("featuredEnterprises") or [] if row.get("enterpriseId") == enterprise_id),
        None,
    )
    if not featured:
        raise HTTPException(status_code=404, detail=f"Unknown demo enterprise: {enterprise_id}")
    return featured_row(store, featured)


@app.get("/demo/{enterprise_id}/{use_case_id}")
def demo_briefing(enterprise_id: str, use_case_id: str) -> dict[str, Any]:
    body = briefing(store, graph, registry, enterprise_id, use_case_id)
    if not body:
        raise HTTPException(status_code=404, detail=f"Unknown briefing: {enterprise_id}/{use_case_id}")
    return body


@app.get("/explore")
def explore() -> dict[str, Any]:
    return explore_summary(store, registry)


@app.get("/explore/agents")
def explore_agents() -> dict[str, Any]:
    return {"agents": list_agents(store)}


@app.get("/explore/agents/{agent_id}")
def explore_agent(agent_id: str) -> dict[str, Any]:
    body = agent_detail(store, agent_id)
    if not body:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_id}")
    return body


@app.get("/explore/purposes")
def explore_purposes() -> dict[str, Any]:
    return {"purposes": list_purposes(store)}


@app.get("/explore/purposes/{purpose_id}")
def explore_purpose(purpose_id: str) -> dict[str, Any]:
    body = purpose_detail(store, purpose_id)
    if not body:
        raise HTTPException(status_code=404, detail=f"Unknown purpose: {purpose_id}")
    return body


@app.get("/explore/policies")
def explore_policies() -> dict[str, Any]:
    return {"policies": list_policies(store)}


@app.get("/explore/policies/{policy_id}")
def explore_policy(policy_id: str) -> dict[str, Any]:
    body = policy_detail(store, policy_id)
    if not body:
        raise HTTPException(status_code=404, detail=f"Unknown policy: {policy_id}")
    return body


@app.get("/explore/autonomy")
def explore_autonomy() -> dict[str, Any]:
    return autonomy_index(store)


@app.get("/explore/providers")
def explore_providers() -> dict[str, Any]:
    return {"providers": list_providers(store), "routes": list_routes(store)}


@app.get("/explore/providers/{provider_id}")
def explore_provider(provider_id: str) -> dict[str, Any]:
    body = provider_detail(store, provider_id)
    if not body:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider_id}")
    return body


@app.get("/explore/my-context")
def explore_my_context_index() -> dict[str, Any]:
    return {
        "enterprises": [
            {"id": e.get("id"), "label": e.get("label"), "domainId": e.get("domainId")} for e in store.enterprises
        ],
        "note": "Configured onboarding knowledge vs minimal runtime requests.",
    }


@app.get("/explore/my-context/{enterprise_id}")
def explore_my_context(enterprise_id: str) -> dict[str, Any]:
    body = my_context(store, enterprise_id)
    if not body:
        raise HTTPException(status_code=404, detail=f"Unknown enterprise: {enterprise_id}")
    return body


@app.get("/explore/evidence-store")
def explore_evidence_store() -> dict[str, Any]:
    return {"evidence": list_store(), "note": "Canonical normalized evidence for cross-intent reuse (demo store)."}


@app.post("/intents")
def post_intent(body: dict[str, Any]) -> dict[str, Any]:
    return execute_intent(store, graph, registry, body)


@app.get("/executions/latest")
def execution_latest() -> dict[str, Any]:
    return get_execution("latest")


@app.get("/executions/{execution_id}")
def execution_detail(execution_id: str) -> dict[str, Any]:
    return get_execution(execution_id)


@app.post("/executions/reset")
def execution_reset() -> dict[str, Any]:
    return reset_executions()


if serve_frontend():
    log.info("serving frontend from %s", FRONTEND_DIST)

    @app.get("/")
    def spa_index() -> FileResponse:
        return FileResponse(FRONTEND_DIST / "index.html")

    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")
