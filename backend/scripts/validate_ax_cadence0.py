#!/usr/bin/env python3
"""AX Cadence 0 validation. No execution engine. No other-repo runtime imports."""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app, graph, registry, store  # noqa: E402

FORBIDDEN_RUNTIME = (
    "Meta_Demo",
    "meta_demo",
    "Jigyasa",
    "jigyasa",
)
ALLOWED_COMMENT_HITS = {"validate_ax_cadence0.py"}

errors: list[str] = []
oks: list[str] = []


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK — {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL — {msg}")


def check_catalog() -> None:
    if not registry.operations:
        fail("registry is empty")
        return
    n = len(registry.families)
    if n < 12 or n > 15:
        fail(f"business family count {n} is not a small practical set")
    else:
        ok(f"AX_ACTIVE_CATALOG has {n} business families")
    ok(f"technical specs {registry.technical_spec_count()} · operations {len(registry.operations)}")
    missing_maturity = [op for op in registry.operations if not op.spec_maturity]
    if missing_maturity:
        fail("operations missing specMaturity metadata")
    else:
        ok("every active operation has specMaturity metadata")
    missing_status = [op for op in registry.operations if op.business_status != "CURRENT_FOCUS"]
    if missing_status:
        fail("active operations must be CURRENT_FOCUS")
    else:
        ok("every active operation is CURRENT_FOCUS")
    experimental = [op for op in registry.operations if "experimental" in op.source]
    unlabeled = [op for op in experimental if op.spec_maturity != "experimental"]
    if unlabeled:
        fail(f"experimental sources without experimental specMaturity: {unlabeled[:3]}")
    elif not experimental:
        fail("CURRENT_FOCUS catalog should include labelled experimental specs (Device Identifier, Recycling, Age, Insights)")
    else:
        ok(f"{len(experimental)} experimental-spec operations labelled experimental (allowed as CURRENT_FOCUS)")
    restored = {"retrieveIdentifier", "checkNumberRecycling", "verifyAge", "checkNetworkQuality"}
    have = {op.operation_id for op in registry.operations}
    missing = restored - have
    if missing:
        fail(f"restored CURRENT_FOCUS operations missing: {missing}")
    else:
        ok("Device Identifier, Number Recycling, Age Verification, Connectivity Insights restored")
    forbidden = [op for op in registry.operations if "iot" in op.source.lower() or "webrtc" in op.source.lower()]
    if forbidden:
        fail("unrelated experimental APIs leaked into active catalog")
    else:
        ok("unrelated experimental APIs are not in the active catalog")
    missing_ids = [op for op in registry.operations if not op.operation_id]
    if missing_ids:
        fail("catalog rows missing operationId")
    else:
        ok("every active catalog row has operationId from spec")


def check_mappings_in_active_catalog() -> None:
    for row in store.mappings.get("capabilityOperations") or []:
        if not registry.has_operation(row["operationId"], row["source"]):
            fail(f"mapping not in active catalog: {row['operationId']} @ {row['source']}")
    ok("all capabilityOperations are in AX_ACTIVE_CATALOG only")


def check_source_backed_ops() -> None:
    for row in store.mappings.get("capabilityOperations") or []:
        evidence = row.get("evidence")
        op_id = row["operationId"]
        source = row["source"]
        if not registry.has_operation(op_id, source):
            fail(f"mapped operation not in catalog: {op_id} @ {source}")
            continue
        if evidence == "SOURCE_BACKED":
            op = registry.canonical(op_id, source)
            if not op or op.superseded:
                fail(f"SOURCE_BACKED operation is missing or superseded: {op_id} @ {source}")
    ok("every mapped operationId+source exists in the pinned catalog")


def check_duplicates() -> None:
    by_id: dict[str, list[str]] = defaultdict(list)
    for op in registry.operations:
        by_id[op.operation_id].append(op.source)
    dupes = {k: v for k, v in by_id.items() if len(v) > 1}
    unexplained = []
    for op_id, sources in dupes.items():
        unique_sources = set(sources)
        if len(unique_sources) == 1:
            unexplained.append(op_id)
        # Duplicates across different source files (superseded packs, sibling APIs) are expected.
    if unexplained:
        fail(f"duplicate operationIds in the same source file: {unexplained[:8]}")
    else:
        ok(f"duplicate operationIds explained by distinct sources ({len(dupes)} ids)")


def check_intents_capabilities() -> None:
    for row in store.mappings.get("intentCapabilities") or []:
        if row["intentId"] not in store.intent_by_id:
            fail(f"intentCapabilities unknown intent {row['intentId']}")
        if row["capabilityId"] not in store.capability_by_id:
            fail(f"intentCapabilities unknown capability {row['capabilityId']}")
        if row.get("evidence") not in {"SOURCE_BACKED", "INFERRED", "NEEDS_REVIEW"}:
            fail(f"intentCapabilities missing evidence grade: {row}")
    ok("every Intent references valid Capabilities with evidence grades")


def check_capability_ops() -> None:
    mapped_caps = {row["capabilityId"] for row in store.mappings.get("capabilityOperations") or []}
    for cap in store.capabilities:
        cap_id = cap["id"]
        ops = [r for r in store.mappings.get("capabilityOperations") or [] if r["capabilityId"] == cap_id]
        if not ops:
            fail(f"capability {cap_id} has no catalog operations and is not NEEDS_REVIEW")
            continue
        for row in ops:
            ev = row.get("evidence")
            if ev not in {"SOURCE_BACKED", "INFERRED", "NEEDS_REVIEW"}:
                fail(f"capability {cap_id} operation missing evidence")
            if ev != "NEEDS_REVIEW" and not registry.has_operation(row["operationId"], row["source"]):
                fail(f"capability {cap_id} points at missing op {row['operationId']}")
    unused = mapped_caps - {c["id"] for c in store.capabilities}
    if unused:
        fail(f"capabilityOperations reference unknown capabilities: {unused}")
    else:
        ok("every Capability references valid catalog Operations (or explicit NEEDS_REVIEW rows)")


def check_use_cases_intents() -> None:
    for row in store.mappings.get("useCaseIntents") or []:
        if row["useCaseId"] not in store.use_case_by_id:
            fail(f"unknown use case {row['useCaseId']}")
        if row["intentId"] not in store.intent_by_id:
            fail(f"use case {row['useCaseId']} references unknown intent {row['intentId']}")
    for uc in store.use_cases:
        if not graph.use_case_intents.get(uc["id"]):
            fail(f"use case {uc['id']} has no intents")
    ok("every UseCase references valid Intent(s)")


def check_domains() -> None:
    for row in store.mappings.get("domainUseCases") or []:
        if row["domainId"] not in store.domain_by_id:
            fail(f"unknown domain {row['domainId']}")
        if row["useCaseId"] not in store.use_case_by_id:
            fail(f"domain {row['domainId']} unknown use case {row['useCaseId']}")
    for d in store.domains:
        if not graph.domain_use_cases.get(d["id"]):
            fail(f"domain {d['id']} has no use cases")
    ok("every Domain references valid UseCases")


def check_forward() -> None:
    for intent_id in ["assess_network_trust", "ensure_baggage_connection", "maintain_inspection_experience"]:
        fwd = graph.forward_intent(intent_id)
        if not fwd.get("intent") or not fwd.get("useCase") or not fwd.get("domain"):
            fail(f"forward traversal incomplete for {intent_id}")
            continue
        ops = [op for cap in fwd["capabilities"] for op in cap["operations"]]
        if not ops:
            fail(f"forward traversal found no operations for {intent_id}")
        else:
            ok(f"forward {fwd['domain']['id']} → {fwd['useCase']['id']} → {intent_id} → {len(ops)} ops")


def check_reverse() -> None:
    samples = ["verifyLocation", "createSession", "phoneNumberVerify", "getReachabilityStatus"]
    for op_id in samples:
        rev = graph.reverse_operation(op_id)
        if not rev["catalogVariants"]:
            fail(f"reverse: {op_id} not in catalog")
            continue
        if op_id in {"verifyLocation", "createSession", "phoneNumberVerify", "getReachabilityStatus"}:
            if not rev["intents"] or not rev["useCases"] or not rev["domains"]:
                fail(f"reverse traversal incomplete for {op_id}")
            else:
                ok(
                    f"reverse {op_id} → caps={len(rev['capabilities'])} "
                    f"intents={len(rev['intents'])} domains={len(rev['domains'])}"
                )


def check_agents() -> None:
    for agent in store.agents:
        app_id = agent["actsOnBehalfOf"]
        if app_id not in store.application_by_id:
            fail(f"agent {agent['id']} actsOnBehalfOf unknown application {app_id}")
        if agent["id"] == app_id:
            fail(f"agent {agent['id']} is not distinct from application")
        for intent_id in agent.get("allowedIntents") or []:
            if intent_id not in store.intent_by_id:
                fail(f"agent {agent['id']} allowedIntents unknown {intent_id}")
    ok("Agent allowedIntents reference valid Intents; Agent ≠ Application")


def check_routes_providers() -> None:
    provider_ops = {
        (row["providerId"], item["operationId"], item["source"])
        for block in store.provider_capabilities
        for item in block.get("operations") or []
        for row in [block]
    }
    for block in store.provider_capabilities:
        if block["providerId"] not in store.provider_by_id:
            fail(f"providerCapabilities unknown provider {block['providerId']}")
        for item in block.get("operations") or []:
            if not registry.has_operation(item["operationId"], item["source"]):
                fail(f"provider {block['providerId']} advertises missing {item['operationId']}")
    for route in store.routes:
        rtype = route.get("type")
        if rtype not in {"DIRECT", "AGGREGATED", "HYBRID", "EXISTING_ENTERPRISE_INTEGRATION"}:
            fail(f"route {route.get('id')} invalid type {rtype}")
        if rtype == "EXISTING_ENTERPRISE_INTEGRATION":
            if route.get("enterpriseId") not in store.enterprise_by_id:
                fail(f"route {route['id']} unknown enterprise")
            continue
        if route.get("providerId") not in store.provider_by_id:
            fail(f"route {route['id']} unknown provider")
        if not registry.has_operation(route["operationId"], route["source"]):
            fail(f"route {route['id']} missing catalog op")
        key = (route["providerId"], route["operationId"], route["source"])
        if key not in provider_ops:
            fail(f"route {route['id']} provider does not advertise operation")
    ok("route/provider references are valid")


def check_no_foreign_runtime() -> None:
    hits: list[str] = []
    scan_roots = [BACKEND / "app", ROOT / "data"]
    for root in scan_roots:
        for path in root.rglob("*"):
            if path.suffix.lower() not in {".py", ".yaml", ".yml", ".json", ".md"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in FORBIDDEN_RUNTIME:
                if token in text:
                    hits.append(f"{path.relative_to(ROOT)}:{token}")
    # Manifest historical notes may mention Meta use cases from the CAMARA survey copy.
    # Runtime Python must not.
    py_hits = [h for h in hits if h.endswith(".py:" + h.split(":")[-1]) or str(h).endswith(".py:Meta_Demo") or ".py:" in h]
    py_hits = [h for h in hits if h.split(":")[0].endswith(".py")]
    if py_hits:
        fail(f"runtime python references forbidden tokens: {py_hits}")
    else:
        ok("backend Python does not import or reference Meta_Demo or Jigyasa")


def check_http() -> None:
    client = TestClient(app)
    health = client.get("/health").json()
    if health.get("cadence") not in {0, 1, 2, 3, 4, 5, 6} or not health.get("registryLoaded"):
        fail(f"health cadence/registry unexpected: {health}")
    else:
        ok("GET /health registryLoaded")
    if str(health.get("cadencePatch")) not in {"0.2", "1", "2", "3", "4", "5", "6", "6.1"}:
        fail(f"unexpected cadencePatch {health.get('cadencePatch')}")
    else:
        ok(f"GET /health cadencePatch {health.get('cadencePatch')}")
    if health.get("catalog", {}).get("businessFamilies") != len(registry.families):
        fail("health catalog.businessFamilies mismatch")
    else:
        ok("health reports business family count, not YAML-file count")
    if health.get("executionEngine") and int(health.get("cadence") or 0) < 2:
        fail("health claims execution engine")
    else:
        ok("health execution-engine flag matches cadence")
    bag = client.get("/intents/ensure_baggage_connection")
    if bag.status_code != 200:
        fail("GET /intents/ensure_baggage_connection failed")
    else:
        body = bag.json()
        ops = [op["operationId"] for cap in body["capabilities"] for op in cap["operations"]]
        if "getReachabilityStatus" not in ops:
            fail("baggage intent did not resolve reachability operation")
        else:
            ok("GET /intents/ensure_baggage_connection resolves catalog operations")
        if "checkNetworkQuality" not in ops:
            fail("baggage intent should restore Connectivity Insights as considered")
        else:
            ok("High Flight restores Connectivity Insights (experimental maturity labelled)")
    rb = client.get("/intents/assess_network_trust")
    if rb.status_code != 200:
        fail("Rocket Bank intent missing")
    else:
        ops = [op["operationId"] for cap in rb.json()["capabilities"] for op in cap["operations"]]
        if "retrieveIdentifier" not in ops or "checkNumberRecycling" not in ops:
            fail("Rocket Bank should restore Device Identifier and Number Recycling")
        else:
            ok("Rocket Bank restores Device Identifier and Number Recycling")
    acme = client.get("/intents/maintain_inspection_experience")
    if acme.status_code != 200:
        fail("Acme intent missing")
    else:
        ops = [op["operationId"] for cap in acme.json()["capabilities"] for op in cap["operations"]]
        if "createApplicationProfile" not in ops or "checkNetworkQuality" not in ops:
            fail("Acme should restore Application Profiles and Connectivity Insights")
        elif "createSession" not in ops:
            fail("Acme lost QoD")
        else:
            ok("Acme restores Insights/Profiles under CURRENT_FOCUS with experimental maturity")
    loc = client.get("/catalog/verifyLocation")
    if loc.status_code != 200 or not loc.json().get("intents"):
        fail("GET /catalog/verifyLocation reverse mapping failed")
    else:
        ok("GET /catalog/verifyLocation reverse mapping works")
    qod = client.get("/catalog/createSession")
    if qod.status_code != 200:
        fail("GET /catalog/createSession failed")
    else:
        domains = qod.json().get("domains") or []
        if len(domains) < 4:
            fail("QoD reverse mapping should span multiple domains")
        else:
            ok(f"GET /catalog/createSession reverse spans {len(domains)} domains")
    apis = client.get("/catalog/apis")
    if apis.status_code != 200 or len(apis.json().get("apis") or []) != len(registry.apis):
        fail("GET /catalog/apis failed")
    else:
        ok("GET /catalog/apis reverse-maps each active API")
    ident = client.get("/catalog/retrieveIdentifier")
    if ident.status_code != 200:
        fail("Device Identifier should be in the active business catalog")
    else:
        variants = ident.json().get("catalogVariants") or []
        if not variants or variants[0].get("spec_maturity") != "experimental":
            fail("Device Identifier must expose experimental specMaturity")
        else:
            ok("Device Identifier is CURRENT_FOCUS with experimental specMaturity")
    age = client.get("/catalog/verifyAge")
    if age.status_code != 200:
        fail("Age Verification should be restored")
    else:
        ok("Age Verification restored")
    client.close()


def evidence_counts() -> dict[str, int]:
    counts = {"SOURCE_BACKED": 0, "INFERRED": 0, "NEEDS_REVIEW": 0}
    for group in ("intentCapabilities", "capabilityOperations"):
        for row in store.mappings.get(group) or []:
            ev = row.get("evidence")
            if ev in counts:
                counts[ev] += 1
    return counts


def main() -> int:
    check_catalog()
    check_mappings_in_active_catalog()
    check_source_backed_ops()
    check_duplicates()
    check_intents_capabilities()
    check_capability_ops()
    check_use_cases_intents()
    check_domains()
    check_forward()
    check_reverse()
    check_agents()
    check_routes_providers()
    check_no_foreign_runtime()
    check_http()
    counts = evidence_counts()
    print(
        "EVIDENCE — "
        f"SOURCE_BACKED={counts['SOURCE_BACKED']} "
        f"INFERRED={counts['INFERRED']} "
        f"NEEDS_REVIEW={counts['NEEDS_REVIEW']}"
    )
    if errors:
        print(f"\nCadence 0 FAILED ({len(errors)} errors, {len(oks)} ok)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"\nCadence 0 PASSED ({len(oks)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
