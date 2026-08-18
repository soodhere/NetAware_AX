#!/usr/bin/env python3
"""AX Cadence 7 validation — model alignment only. Live heroes unchanged."""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
DOCS = ROOT / "docs"
DATA = ROOT / "data"
sys.path.insert(0, str(BACKEND))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient  # noqa: E402

from app.config import MODEL_CADENCE, MODEL_DIR, PROFILES_DIR, SCHEMAS_DIR, UI_CADENCE  # noqa: E402
from app.main import app, store, registry  # noqa: E402
from app.runtime import EXECUTABLE_INTENTS  # noqa: E402

errors: list[str] = []
oks: list[str] = []

FUTURE_INTENTS = {
    "rollout_firmware_safely",
    "assure_ramp_scan_capability",
}
C9_INTENT = "verify_mobile_number"
NV_OPS = {"phoneNumberVerify", "phoneNumberShare"}
CANONICAL_FILTERS = {
    "NOT_RELEVANT",
    "PURPOSE_NOT_PERMITTED",
    "NOT_SUBSCRIBED",
    "NOT_ENTITLED",
    "CONSENT_MISSING",
    "AGREEMENT_GAP",
    "REGION_NOT_SUPPORTED",
    "PROVIDER_NOT_AVAILABLE",
    "OPERATOR_NOT_SUPPORTED",
    "ENTITLEMENT_SERVER_UNAVAILABLE",
    "ACCESS_TYPE_INCOMPATIBLE",
    "TECHNICAL_PREREQUISITE_MISSING",
    "EVIDENCE_REUSED",
    "NOT_REQUIRED",
    "AUTONOMY_FORBIDS",
    "SELECTED",
}
TMF_CLASSES = {
    "TMF931_DIRECT",
    "TMF931_INSPIRED",
    "NETAWARE_SPECIFIC",
    "AX_SPECIFIC",
    "RUNTIME_DISCOVERED",
}
HEROES = [
    (
        "STEP_UP",
        {
            "intent": "assess_network_trust",
            "subject": {"transactionId": "RB-78421", "phoneNumber": "+1••••••0198"},
            "context": {"amount": 25000, "currency": "USD"},
        },
    ),
    (
        "AT_RISK",
        {
            "intent": "ensure_baggage_connection",
            "subject": {"bagId": "HF123456", "connectingFlight": "HF281"},
            "context": {"priority": "high"},
        },
    ),
    (
        "ASSURED",
        {
            "intent": "maintain_inspection_experience",
            "subject": {"cameraId": "ACME-CAM-14", "lineId": "LINE-B"},
            "context": {"sloMs": 40},
        },
    ),
    (
        "ELIGIBLE",
        {
            "intent": "verify_pharmacy_age_gate",
            "subject": {"transactionId": "RX-10442", "phoneNumber": "+1••••••8843"},
            "context": {"ageThreshold": 18},
        },
    ),
]


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK - {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL - {msg}")


def _doc(doc: dict) -> dict:
    merged = dict(doc.get("model") or {})
    merged.update({k: v for k, v in doc.items() if k != "model"})
    return merged


def check_health_and_baseline() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if h.get("version") != "0.6.1-ax6.1":
            fail(f"live version must remain 0.6.1-ax6.1: {h.get('version')}")
        else:
            ok("live version 0.6.1-ax6.1")
        if h.get("cadence") != 6 or h.get("cadencePatch") != "6.1":
            fail(f"product cadence must remain 6 / 6.1: {h.get('cadence')} {h.get('cadencePatch')}")
        else:
            ok("product cadence 6 / 6.1")
        if h.get("modelCadence") != 7 or MODEL_CADENCE != 7:
            fail(f"modelCadence {h.get('modelCadence')}")
        else:
            ok("modelCadence 7")
        if not h.get("productBehaviorFrozen"):
            fail("product behavior must stay frozen")
        else:
            ok("product behavior frozen")
        if set(h.get("executableIntents") or []) != set(EXECUTABLE_INTENTS):
            fail("executable intent set changed")
        elif FUTURE_INTENTS & set(EXECUTABLE_INTENTS):
            fail("OTA/ramp leaked into EXECUTABLE_INTENTS")
        elif UI_CADENCE >= 9:
            if C9_INTENT not in EXECUTABLE_INTENTS:
                fail("Cadence 9 must execute verify_mobile_number")
            else:
                ok("verify_mobile_number live; OTA/ramp still future")
        elif C9_INTENT in EXECUTABLE_INTENTS:
            fail("verify_mobile_number leaked before Cadence 9")
        else:
            ok("executable intents unchanged (5)")


def check_nv_model() -> None:
    fam = next((f for f in registry.families if f.get("id") == "number-verification"), None)
    if not fam:
        fail("Number Verification family missing")
        return
    if len([f for f in registry.families if "number-verification" in str(f.get("id"))]) != 1:
        fail("Number Verification must remain one family")
    else:
        ok("Number Verification is one family")
    ops = []
    for spec in fam.get("technicalSpecs") or []:
        ops.extend(spec.get("operations") or [])
    ids = {row.get("operationId") for row in ops}
    if ids != NV_OPS:
        fail(f"NV operations changed: {ids}")
    else:
        ok("phoneNumberVerify / phoneNumberShare unchanged")
    labelled = False
    for row in ops:
        label = str(row.get("productLabel") or "")
        if label in {"NV1", "NV2"}:
            labelled = True
            fail(f"{row.get('operationId')} still labelled {label}")
    if not labelled:
        ok("NV operations are not labelled NV1/NV2")

    paths = store.nv_paths
    path_ids = {p.get("id") for p in paths.get("paths") or []}
    if path_ids != {"NV1_NETWORK_BASED", "NV2_OPERATOR_TOKEN"}:
        fail(f"NV paths {path_ids}")
    else:
        ok("NV1_NETWORK_BASED and NV2_OPERATOR_TOKEN modelled")
    for path in paths.get("paths") or []:
        if path.get("id") == "NV1_NETWORK_BASED" and path.get("not") == "phoneNumberVerify":
            ok("NV1 is not phoneNumberVerify")
        if path.get("id") == "NV2_OPERATOR_TOKEN" and path.get("not") == "phoneNumberShare":
            ok("NV2 is not phoneNumberShare")
    if (paths.get("accessTypes") or {}).get("source") != "RUNTIME_CLIENT_CONTEXT":
        fail("access type source must be RUNTIME_CLIENT_CONTEXT")
    else:
        ok("access type sourced from runtime/client context")

    blob = json.dumps(paths)
    if "SMS OTP" not in blob and "SMS OTP" not in _yaml_text("data/model/nv-paths.yaml"):
        fail("NV model must forbid SMS OTP fallback")
    else:
        ok("SMS OTP forbidden as AX NV fallback")


def check_operator_ecs() -> None:
    readiness = store.operator_readiness
    if readiness.get("source") != "CONFIGURED_OPERATOR_READINESS":
        fail("ECS source is not CONFIGURED_OPERATOR_READINESS")
    else:
        ok("ECS modelled as configured operator readiness")
    states = {(op.get("entitlementServer") or {}).get("available") for op in readiness.get("operators") or []}
    if not {"AVAILABLE", "UNAVAILABLE", "UNKNOWN"} <= states:
        fail(f"ECS states incomplete: {states}")
    else:
        ok("ECS AVAILABLE / UNAVAILABLE / UNKNOWN present")
    codes = store.discovery.get("filterCodes") or []
    if "ENTITLEMENT_SERVER_UNAVAILABLE" not in codes:
        fail("missing ENTITLEMENT_SERVER_UNAVAILABLE")
    else:
        ok("filter ENTITLEMENT_SERVER_UNAVAILABLE")
    catalog_blob = json.dumps(registry.to_public()).lower()
    if "entitlement configuration server" in catalog_blob or "entitlement-server" in catalog_blob:
        fail("ECS leaked into API catalog payload")
    else:
        ok("ECS is not an API catalog family")
    family_ids = {str(f.get("id")) for f in registry.families}
    forbidden = {"connected-network-type", "otp-validation", "one-time-password", "esim", "device-reachability-status-subscriptions"}
    if family_ids & forbidden:
        fail(f"forbidden families in active catalog: {family_ids & forbidden}")
    else:
        ok("no Connected Network Type / OTP / ECS / reachability-subscriptions family")


def check_dpv() -> None:
    allow = (_load_allowlist())
    for purpose in store.purposes:
        dpv = purpose.get("dpv") or {}
        pid = str(dpv.get("id") or "")
        if not pid:
            fail(f"purpose {purpose.get('id')} missing DPV id")
            continue
        if pid not in allow:
            fail(f"invented or unlisted DPV id {pid} on {purpose.get('id')}")
            continue
        if not str(dpv.get("context") or "").strip():
            fail(f"purpose {purpose.get('id')} missing context")
            continue
        expected_iri = f"https://w3id.org/dpv#{pid.split(':', 1)[-1]}"
        if dpv.get("iri") != expected_iri:
            fail(f"purpose {purpose.get('id')} IRI {dpv.get('iri')}")
        else:
            ok(f"{purpose.get('id')} -> {pid}")
    fake = [p for p in store.purposes if str((p.get("dpv") or {}).get("id") or "").startswith("dpv:") is False]
    if fake:
        fail("non-DPV purpose identifiers in dpv.id")


def _load_allowlist() -> set[str]:
    import yaml

    data = yaml.safe_load((SCHEMAS_DIR / "dpv-purpose-allowlist.yaml").read_text(encoding="utf-8"))
    return set(data.get("ids") or [])


def check_tmf931() -> None:
    tmf = store.tmf931
    classes = {str(c) for c in (tmf.get("classifications") or {})}
    if classes != TMF_CLASSES:
        fail(f"TMF classifications {classes}")
    else:
        ok("TMF931 classification vocabulary valid")
    fields = {str(f.get("id")): f for f in tmf.get("fields") or []}
    required = {
        "enterprise",
        "application",
        "apiProduct",
        "subscription",
        "scope",
        "purpose",
        "legalBasis",
        "agreement",
        "securityGrantType",
        "region",
        "provider",
        "entitlement",
        "agent",
        "intent",
        "autonomy",
        "capabilityDiscovery",
        "telcoFinder",
        "apiFinder",
        "evidence",
        "accessType",
        "ecsReadiness",
        "nvPath",
        "salesScenarioProfile",
    }
    missing = required - set(fields)
    if missing:
        fail(f"TMF931 fields missing {missing}")
    else:
        ok("required TMF931 alignment fields present")
    for key in ("agent", "intent", "autonomy", "evidence"):
        if (fields.get(key) or {}).get("classification") != "AX_SPECIFIC":
            fail(f"{key} must be AX_SPECIFIC")
        elif not (fields.get(key) or {}).get("doNotForceIntoTmf931"):
            fail(f"{key} must not be forced into TMF931")
    else:
        ok("Agent / Intent / Autonomy / Evidence not forced into TMF931")
    for row in tmf.get("fields") or []:
        if row.get("classification") not in TMF_CLASSES:
            fail(f"invalid classification on {row.get('id')}")


def check_subscription_entitlement() -> None:
    if len(store.subscriptions) < 1 or len(store.entitlements) < 1:
        fail("subscriptions/entitlements missing")
        return
    sub_ids = {s.get("id") for s in store.subscriptions}
    for ent in store.entitlements:
        if not ent.get("applicationId") or not ent.get("agentId"):
            fail(f"entitlement {ent.get('id')} missing application/agent")
        if ent.get("subscriptionId") not in sub_ids:
            fail(f"entitlement {ent.get('id')} dangling subscription")
        if not ent.get("capabilityId") and not ent.get("capabilityFamily"):
            fail(f"entitlement {ent.get('id')} has no capability target")
    else:
        ok("entitlements are application/agent grants bound to subscriptions")
    if store.is_subscribed == store.is_entitled:  # type: ignore[comparison-overlap]
        fail("subscription helper collapsed onto entitlement")
    else:
        ok("subscription and entitlement are separate helpers")
    codes = set(store.discovery.get("filterCodes") or [])
    if not {"NOT_SUBSCRIBED", "NOT_ENTITLED"} <= codes:
        fail("discovery missing NOT_SUBSCRIBED / NOT_ENTITLED")
    else:
        ok("NOT_SUBSCRIBED and NOT_ENTITLED are canonical filters")


def check_discovery_model() -> None:
    groups = [g.get("id") for g in store.discovery.get("groups") or []]
    if groups != ["CANDIDATE_GENERATION", "CONFIGURED_ELIGIBILITY", "RUNTIME_FEASIBILITY", "SELECT"]:
        fail(f"discovery groups {groups}")
    else:
        ok("discovery stage groups encoded")
    codes = set(store.discovery.get("filterCodes") or [])
    if codes != CANONICAL_FILTERS:
        fail(f"filter codes mismatch extra={codes - CANONICAL_FILTERS} missing={CANONICAL_FILTERS - codes}")
    else:
        ok("canonical discovery filter codes")


def check_product_alignment() -> None:
    pa = store.product_alignment
    assets = {a.get("id") for a in pa.get("existingNetAwareAssets") or []}
    ext = {a.get("id") for a in pa.get("axExtensions") or []}
    needed_assets = {"onboarding", "apiCatalog", "subscriptions", "telcoFinder", "apiFinder", "providerRouting", "invocation"}
    needed_ext = {"intent", "agentAuthorization", "capabilityDiscovery", "autonomy", "evidenceReuse", "planReplanVerify"}
    if not needed_assets <= assets:
        fail(f"alignment assets missing {needed_assets - assets}")
    elif not needed_ext <= ext:
        fail(f"AX extensions missing {needed_ext - ext}")
    else:
        ok("NetAware assets vs AX extensions mapped")
    if "replace" in str(pa.get("customerLine") or "").lower() and "does not replace" not in str(pa.get("customerLine") or "").lower():
        fail("customer line must say AX does not replace NetAware assets")
    else:
        ok("customer line: AX does not replace NetAware assets")


def check_high_flight_and_ota() -> None:
    hf = _doc(store.high_flight_replacement)
    if hf.get("executable") or (hf.get("replacement") or {}).get("executableNow"):
        fail("High Flight replacement must not be executable")
    else:
        ok("High Flight replacement documented, not executable")
    if (hf.get("currentHero") or {}).get("disposition") != "DEMOTE":
        fail("current baggage-connection not marked DEMOTE")
    else:
        ok("current High Flight hero marked DEMOTE")
    if "baggage location" not in json.dumps(hf.get("replacement") or {}).lower():
        fail("replacement must explicitly reject reachability = baggage location")
    else:
        ok("High Flight model forbids reachability = bag location")

    ota = _doc(store.ota_device_fleet)
    if ota.get("executable") or ota.get("applicationExistsNow"):
        fail("OTA model must not be live")
    else:
        ok("OTA model frozen, not executable")
    if ota.get("intentId") != "rollout_firmware_safely":
        fail("OTA intent id")
    else:
        ok("OTA intent rollout_firmware_safely")
    if not ota.get("networkDoesNotFlashFirmware"):
        fail("OTA must state network does not flash firmware")
    else:
        ok("OTA: network does not flash firmware")
    domain_ops = set(((ota.get("domainOperations") or {}).get("operations") or []))
    needed = {"listDevices", "getDevice", "getTwin", "getPackage", "createCampaign", "startWave", "getCampaignStats", "latestCheckIn"}
    if not needed <= domain_ops:
        fail(f"OTA domain ops missing {needed - domain_ops}")
    else:
        ok("OTA domain/enterprise operations frozen")
    if (ota.get("domainOperations") or {}).get("notCamara") is not True:
        fail("OTA domain ops must be marked not CAMARA")
    camara = set((ota.get("networkOperations") or {}).get("fromActiveCatalog") or [])
    if "createCampaign" in camara or "getPackage" in camara:
        fail("firmware operations leaked into network operations")
    else:
        ok("firmware distribution stays on enterprise OTA API")


def check_catalog_size() -> None:
    if len(registry.families) != 13:
        fail(f"catalog families {len(registry.families)}")
    else:
        ok("13 business families unchanged")
    connected = [f for f in registry.families if "connected-network" in str(f.get("id"))]
    if connected:
        fail("Connected Network Type admitted")
    otp = [op.operation_id for op in registry.operations if "otp" in op.operation_id.lower() or "one-time-password" in op.source.lower()]
    if otp:
        fail(f"OTP operations in active catalog: {otp}")
    else:
        ok("OTP SMS not in active catalog")


def check_sales_profile() -> None:
    schema_path = SCHEMAS_DIR / "sales-scenario-profile.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    required = set(schema.get("required") or [])
    expected = {
        "id",
        "audience",
        "lensDefault",
        "enterpriseId",
        "applicationId",
        "intentId",
        "scenarioSeed",
        "demoMode",
    }
    if not expected <= required:
        fail(f"SalesScenarioProfile required fields {required}")
    else:
        ok("SalesScenarioProfile schema present")
    props = schema.get("properties") or {}
    for field in (
        "industryLabel",
        "region",
        "topology",
        "meetingGoal",
        "businessProblem",
        "existingSystems",
        "domainApis",
        "purpose",
        "networkSubjectModel",
        "relevantCapabilities",
        "providerTopology",
        "subscriptions",
        "entitlements",
        "policyRef",
        "autonomy",
        "expectedOutcome",
        "commercialMessage",
    ):
        if field not in props:
            fail(f"profile schema missing {field}")
    else:
        ok("sales profile fields encoded")

    example = PROFILES_DIR / "examples" / "operator-cto-de-ota.yaml"
    if not example.exists():
        fail("missing example sales profile")
        return
    import yaml

    inst = yaml.safe_load(example.read_text(encoding="utf-8"))
    missing = [k for k in schema["required"] if k not in inst]
    if missing:
        fail(f"example profile missing {missing}")
    else:
        ok("example SalesScenarioProfile validates required fields")
    if str((inst.get("purpose") or {}).get("id") or "") not in _load_allowlist():
        fail("example profile DPV id not allowlisted")
    else:
        ok("example profile uses a real DPV id")

    runtime_src = (BACKEND / "app" / "runtime.py").read_text(encoding="utf-8")
    model_src = (BACKEND / "app" / "model.py").read_text(encoding="utf-8")
    main_src = (BACKEND / "app" / "main.py").read_text(encoding="utf-8")
    joined = runtime_src + model_src + main_src
    if "PROFILES_DIR" in joined or "data/profiles" in joined.replace("\\", "/"):
        fail("runtime loads sales profiles")
    else:
        ok("runtime does not load SalesScenarioProfile")
    if "rollout_firmware_safely" in EXECUTABLE_INTENTS:
        fail("OTA intent executable")


def check_no_new_ui() -> None:
    if UI_CADENCE >= 8:
        ok("Discovery / lens UI belongs to Cadence 8+")
        return
    app_js = (FRONTEND / "src").read_text if False else None
    blob = ""
    for path in (FRONTEND / "src").rglob("*.jsx"):
        blob += path.read_text(encoding="utf-8")
    if "Discovery" in blob and "Discovery tab" in blob:
        fail("Discovery UI added")
    if re.search(r"Basic\s*/\s*Advanced|lensDefault|demoMode", blob):
        fail("Basic/Advanced lens added to UI")
    else:
        ok("no Discovery tab / Basic-Advanced lens in UI")
    footer = (FRONTEND / "src" / "App.jsx").read_text(encoding="utf-8")
    if "Cadence 6 · presentation freeze" not in footer:
        fail("footer presentation freeze line changed")
    else:
        ok("presentation footer unchanged")


def check_heroes_unchanged() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        for expected, body in HEROES:
            res = client.post("/intents", json=body)
            if res.status_code >= 400:
                fail(f"{body['intent']} HTTP {res.status_code}: {res.text[:200]}")
                continue
            outcome = (res.json().get("outcome") or {}).get("outcome")
            if outcome != expected:
                fail(f"{body['intent']} outcome {outcome} != {expected}")
            else:
                ok(f"{body['intent']} -> {expected}")
        rec_body = {
            "intent": "assess_recovery_continuity",
            "subject": {"recoveryId": "RB-REC-19", "phoneNumber": "+1••••••0198"},
            "context": {"channel": "web"},
        }
        rec = client.post("/intents", json=rec_body)
        rec_out = (rec.json().get("outcome") or {}).get("outcome")
        if rec_out != "CONTINUITY_ALIGNED":
            fail(f"recovery outcome {rec_out}")
        else:
            ok("recovery CONTINUITY_ALIGNED (evidence reuse)")
        still_future = set(FUTURE_INTENTS)
        if UI_CADENCE < 9:
            still_future.add(C9_INTENT)
        for intent in still_future:
            bad = client.post("/intents", json={"intent": intent, "subject": {}, "context": {}})
            if bad.status_code < 400:
                fail(f"{intent} must not be executable")
        else:
            ok("future OTA/ramp intents are not executable")


def check_boundaries() -> None:
    hits = []
    for path in (BACKEND / "app").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in {"Meta_Demo", "Jigyasa"}:
                    hits.append(f"{path.name}:{node.value}")
    if hits:
        fail(f"runtime constants reference other repos: {hits}")
    else:
        ok("backend app does not import Meta_Demo or Jigyasa")
    if not (DOCS / "cadences" / "ax-cadence-7.md").exists():
        fail("missing ax-cadence-7.md")
    else:
        ok("cadence 7 report present")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    for name, rel in (
        ("validate_ax_cadence0", "validate_ax_cadence0.py"),
        ("validate_ax_cadence6_1_mod", "validate_ax_cadence6.1.py"),
    ):
        mod = SourceFileLoader(name, str(BACKEND / "scripts" / rel)).load_module()
        code = mod.main()
        if code != 0:
            fail(f"{rel} regression failed")
            return
    ok("cadence 0 and 6.1 regression passed")


def main() -> int:
    print("=== AX Cadence 7 validation (model alignment) ===\n")
    check_health_and_baseline()
    check_nv_model()
    check_operator_ecs()
    check_dpv()
    check_tmf931()
    check_subscription_entitlement()
    check_discovery_model()
    check_product_alignment()
    check_high_flight_and_ota()
    check_catalog_size()
    check_sales_profile()
    check_no_new_ui()
    check_heroes_unchanged()
    check_boundaries()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  • {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
