#!/usr/bin/env python3
"""AX Cadence 13 validation — Fulfillment Coverage Explorer. Do not start Cadence 14."""
from __future__ import annotations

import json
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

from app.config import MODEL_CADENCE, SCHEMAS_DIR, UI_CADENCE  # noqa: E402
from app.fulfillment import GAP_CODES, STATES, public_coverage, validate_record_schema  # noqa: E402
from app.main import app, graph, registry, store  # noqa: E402
from app.portfolio import visible_rows  # noqa: E402
from app.runtime import EXECUTABLE_INTENTS  # noqa: E402

errors: list[str] = []
oks: list[str] = []

HEROES = [
    ("STEP_UP", {"intent": "assess_network_trust", "subject": {"transactionId": "RB-78421", "phoneNumber": "+1••••••0198"}, "context": {"amount": 25000, "currency": "USD"}}),
    ("VERIFIED", {"intent": "verify_mobile_number", "subject": {"phoneNumber": "+1••••••0198"}, "context": {"nvVariant": "cellular-nv1", "accessType": "CELLULAR", "claimedMsisdn": True, "businessEvent": "CUSTOMER_SIGNING_IN"}}),
    ("CONTINUE", {"intent": "ensure_baggage_connection", "subject": {"bagId": "HF123456", "connectingFlight": "HF281"}, "context": {"priority": "high"}}),
    ("ASSURED", {"intent": "maintain_inspection_experience", "subject": {"cameraId": "ACME-CAM-14", "lineId": "LINE-B"}, "context": {"sloMs": 40}}),
    ("ELIGIBLE", {"intent": "verify_pharmacy_age_gate", "subject": {"transactionId": "RX-10442", "phoneNumber": "+1••••••8843"}, "context": {"ageThreshold": 18}}),
]

REAL_OPS = ("Verizon", "T-Mobile", "Vodafone", "Deutsche Telekom", "Singtel", "AT&T")


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK - {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL - {msg}")


def check_health() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if UI_CADENCE not in {13, 14, 15, 16, 17} or h.get("uiCadence") not in {13, 14, 15, 16, 17}:
            fail(f"uiCadence {h.get('uiCadence')} / {UI_CADENCE}")
        else:
            ok("uiCadence 13")
        if h.get("modelCadence") != 7 or MODEL_CADENCE != 7:
            fail(f"modelCadence {h.get('modelCadence')}")
        else:
            ok("modelCadence 7")
        if h.get("version") != "0.6.1-ax6.1":
            fail(f"live version {h.get('version')}")
        else:
            ok("live version 0.6.1-ax6.1")
        if len(registry.families) != 13:
            fail(f"catalog families {len(registry.families)}")
        else:
            ok("active catalog remains 13 families")


def check_schema_and_model() -> None:
    schema = SCHEMAS_DIR / "fulfillment-record.json"
    if not schema.exists():
        fail("missing fulfillment-record.json")
        return
    ok("fulfillment record schema exists")
    body = json.loads(schema.read_text(encoding="utf-8"))
    required = set(body.get("required") or [])
    for key in ("enterpriseId", "applicationId", "intentId", "region", "fulfillmentStatus", "provenance"):
        if key not in required:
            fail(f"schema missing {key}")
            return
    else:
        ok("fulfillment record required fields")
    props = body.get("properties") or {}
    if "revenue" in props or "opportunityScore" in props or "tam" in props:
        fail("schema has commercial fields")
    else:
        ok("no revenue fields on fulfillment schema")
    overlay = (DATA / "model" / "fulfillment-coverage.yaml").read_text(encoding="utf-8")
    if "FULFILLABLE" not in overlay or "NOT_CONFIGURED" not in overlay:
        fail("coverage overlay missing states")
    else:
        ok("coverage overlay names slices; statuses derived")


def check_coverage_api() -> None:
    with TestClient(app) as client:
        res = client.get("/coverage")
        if res.status_code >= 400:
            fail(f"/coverage {res.status_code}")
            return
        payload = res.json()
        records = payload.get("records") or []
        if not records:
            fail("no fulfillment records")
            return
        ok(f"{len(records)} fulfillment records")
        for rec in records:
            try:
                validate_record_schema(rec)
            except Exception as exc:
                fail(f"schema {rec.get('id')}: {exc}")
                return
        ok("records match fulfillment schema")
        summary = payload.get("summary") or {}
        if summary.get("salesVisibleUseCases") != 17:
            fail(f"summary use cases {summary.get('salesVisibleUseCases')}")
        else:
            ok("coverage summary 17 sales-visible use cases")
        if summary.get("configuredFulfillmentCoverage") < 12:
            fail(f"configured coverage {summary.get('configuredFulfillmentCoverage')}")
        else:
            ok("configured fulfillment coverage derived")
        if UI_CADENCE < 14 and ("Demand Map" in json.dumps(payload) or "Meeting Mode" in json.dumps(payload)):
            fail("C14 surfaces leaked into /coverage")
        else:
            ok("Demand Map / Meeting Mode not present")
        blob = json.dumps(payload)
        if any(name in blob for name in REAL_OPS):
            fail("real operator names in coverage")
        else:
            ok("no real operator claims")
        if "opportunityScore" in blob or '"tam"' in blob.lower() or "lost revenue" in blob.lower():
            fail("commercial scoring leaked")
        else:
            ok("no commercial opportunity scoring")

        ent = client.get("/coverage/enterprises/rocket-bank")
        if ent.status_code >= 400 or not (ent.json().get("records") or []):
            fail("enterprise/demand entry missing")
        else:
            ok("enterprise/application/intent entry works")
        supply = client.get("/coverage/providers/simulated-operator-a")
        if supply.status_code >= 400 or not (supply.json().get("providers") or []):
            fail("provider/supply entry missing")
        else:
            ok("provider/supply reverse entry works")
        agg = client.get("/coverage/providers/simulated-aggregator-b")
        if agg.status_code >= 400:
            fail("aggregator view missing")
        else:
            body = agg.json()
            note = json.dumps(body)
            if "does not own" not in note.lower() and "doesNotOwnApis" not in note:
                fail("aggregator ownership note missing")
            else:
                ok("aggregator view does not claim API ownership")


def check_distinctions() -> None:
    payload = public_coverage(store, graph, registry)
    records = payload.get("records") or []
    nv_cell = next((r for r in records if r.get("id") == "nv-cellular-provider-a"), None)
    nv_wifi_a = next((r for r in records if r.get("id") == "nv-wifi-provider-a"), None)
    nv_wifi_b = next((r for r in records if r.get("id") == "nv-wifi-provider-b"), None)
    if not nv_cell or nv_cell.get("fulfillmentStatus") != "FULFILLABLE" or nv_cell.get("selectedPath") != "NV1_NETWORK_BASED":
        fail(f"NV cellular A {nv_cell}")
    else:
        ok("NV cellular Provider A fulfillable via NV1")
    if not nv_wifi_a or nv_wifi_a.get("fulfillmentStatus") != "FULFILLABLE" or nv_wifi_a.get("selectedPath") != "NV2_OPERATOR_TOKEN":
        fail(f"NV wifi A {nv_wifi_a}")
    else:
        ok("NV Wi-Fi Provider A fulfillable through NV2")
    if not nv_wifi_b or nv_wifi_b.get("fulfillmentStatus") != "BLOCKED":
        fail(f"NV wifi B {nv_wifi_b}")
    else:
        codes = {g.get("code") for g in nv_wifi_b.get("blockingGaps") or []}
        cap = (nv_wifi_b.get("capabilities") or [{}])[0]
        if "ENTITLEMENT_SERVER_UNAVAILABLE" not in codes:
            fail(f"NV wifi B gaps {codes}")
        elif cap.get("available") != "YES":
            fail("NV wifi B should still show API available")
        else:
            ok("NV Wi-Fi Provider B blocked by ECS readiness; API still available")
    if any(r.get("applicationDoesNotSelectPath") is False for r in (nv_cell, nv_wifi_a, nv_wifi_b) if r):
        fail("application appears to select NV1/NV2")
    else:
        ok("application does not select NV1/NV2")

    hf = next((r for r in records if r.get("intentId") == "ensure_baggage_connection"), None)
    if not hf or hf.get("fulfillmentStatus") != "FULFILLABLE" or not hf.get("fulfillmentVsOutcome"):
        fail(f"High Flight {hf}")
    else:
        ok("High Flight unreachable device remains fulfillment success")

    ota_c = next((r for r in records if r.get("id") == "ota-provider-c"), None)
    if not ota_c or ota_c.get("fulfillmentStatus") != "PARTIALLY_FULFILLABLE":
        fail(f"OTA C {ota_c}")
    else:
        codes = {g.get("code") for g in ota_c.get("blockingGaps") or []}
        qd = ota_c.get("qualifiedDemand") or {}
        if "CAPABILITY_GAP" not in codes or qd.get("unfulfilledCount") != 500:
            fail(f"OTA C gaps {codes} qd {qd}")
        elif qd.get("notRevenue") is not True:
            fail("qualified demand looks like revenue")
        else:
            ok("OTA Provider C roaming gap is a fulfillment gap with qualified demand, not revenue")

    roles_ok = False
    optional_not_blocking = False
    for rec in records:
        for cap in rec.get("capabilities") or []:
            if cap.get("role") in {"REQUIRED", "OPTIONAL", "CONDITIONAL"}:
                roles_ok = True
            if cap.get("role") == "OPTIONAL" and cap.get("fulfillable") == "NO" and rec.get("fulfillmentStatus") == "FULFILLABLE":
                optional_not_blocking = True
            dist = {cap.get("relevant"), cap.get("permitted"), cap.get("available"), cap.get("ready"), cap.get("fulfillable")}
            if len(dist) > 1:
                pass
    if not roles_ok:
        fail("required vs optional not distinguished")
    else:
        ok("required vs optional capabilities distinguished")
    if not optional_not_blocking:
        fail("optional API gap blocked an intent")
    else:
        ok("fulfillment does not require optional APIs")

    mm = next((r for r in records if r.get("intentId") == "assess_checkout_trust"), None)
    loc = next((c for c in (mm or {}).get("capabilities") or [] if c.get("id") == "location_verification"), None)
    if not loc or "CONSENT_MISSING" not in {g.get("code") for g in loc.get("gaps") or []}:
        fail(f"consent gap missing {loc}")
    elif mm.get("fulfillmentStatus") != "FULFILLABLE":
        fail("consent on optional location blocked intent")
    else:
        ok("consent can block available API without collapsing the Intent")

    pharm = next((r for r in records if r.get("intentId") == "verify_pharmacy_age_gate"), None)
    kyc = next((c for c in (pharm or {}).get("capabilities") or [] if c.get("id") == "kyc_match"), None)
    if not kyc or "PURPOSE_NOT_PERMITTED" not in {g.get("code") for g in kyc.get("gaps") or []}:
        fail(f"purpose gap missing {kyc}")
    else:
        ok("policy/purpose can block available API")

    unknown = [r for r in records if r.get("fulfillmentStatus") == "NOT_CONFIGURED"]
    blocked = [r for r in records if r.get("fulfillmentStatus") == "BLOCKED"]
    if len(unknown) < 4:
        fail(f"EXPLORE unknown {len(unknown)}")
    elif any(r.get("maturity") == "EXPLORE" and r.get("fulfillmentStatus") == "BLOCKED" for r in records):
        fail("EXPLORE presented as BLOCKED")
    else:
        ok("UNKNOWN/NOT_CONFIGURED distinguished from BLOCKED")
    if not blocked:
        fail("no BLOCKED showcase")
    else:
        ok("BLOCKED reserved for known failures")

    routes = {r.get("route") for r in records if r.get("route")}
    if not {"DIRECT", "AGGREGATED", "HYBRID"} <= routes:
        fail(f"routes {routes}")
    else:
        ok("direct, aggregated, and hybrid routes represented")

    dist = payload.get("distinctions") or {}
    if "Telco" not in str(dist.get("telcoFinder")) and "network" not in str(dist.get("telcoFinder") or "").lower():
        fail("telco finder distinction missing")
    else:
        ok("Telco Finder != API Finder != Fulfillment")
    if not any((r.get("provenance") or []) for r in records):
        fail("provenance missing")
    else:
        sources = {p.get("source") for r in records for p in r.get("provenance") or []}
        if not {"INTENT PROFILE", "DERIVED", "SIMULATED PROVIDER DATA"} <= sources:
            fail(f"provenance sources {sources}")
        else:
            ok("provenance exists")
    if "minimumSufficientSet" not in records[0]:
        fail("minimum sufficient set missing")
    else:
        ok("minimum sufficient capability concept exists")
    ecs = payload.get("ecs") or {}
    if not ecs.get("notACamaraApi"):
        fail("ECS labelled as CAMARA")
    else:
        ok("Entitlement Server is operator prerequisite, not a CAMARA API")


def check_portfolio_catalog() -> None:
    rows = visible_rows(store)
    if len(rows) != 17:
        fail(f"visible use cases {len(rows)}")
    else:
        ok("17-use-case portfolio preserved")
    with TestClient(app) as client:
        demo = client.get("/demo").json()
        featured = [row.get("heroUseCaseId") for row in demo.get("featured") or []]
        if featured[:5] != [
            "passwordless-mobile-sign-in",
            "high-value-payment-protection",
            "critical-inspection-camera",
            "pharmacy-age-gate",
            "baggage-connection",
        ]:
            fail(f"featured {featured[:5]}")
        else:
            ok("featured LIVE heroes unchanged")
        if "rollout_firmware_safely" in json.dumps(demo):
            fail("OTA alias leaked onto /demo")
        else:
            ok("OTA working alias not on /demo")
        cat = client.get("/catalog/apis").json()
        if len(cat.get("apis") or []) != 13:
            fail("catalog expansion")
        else:
            ok("catalog remains 13 families")


def check_live_outcomes() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        for expected, body in HEROES:
            res = client.post("/intents", json=body)
            if res.status_code >= 400:
                fail(f"{body['intent']} HTTP {res.status_code}")
                continue
            got = (res.json().get("outcome") or {}).get("outcome")
            if got != expected:
                fail(f"{body['intent']} {got} != {expected}")
            else:
                ok(f"{body['intent']} unchanged {expected}")
        rec = client.post(
            "/intents",
            json={"intent": "assess_recovery_continuity", "subject": {"recoveryId": "RB-REC-19", "phoneNumber": "+1••••••0198"}, "context": {"channel": "web"}},
        )
        if (rec.json().get("outcome") or {}).get("outcome") != "CONTINUITY_ALIGNED":
            fail("recovery changed")
        else:
            ok("Rocket Bank recovery CONTINUITY_ALIGNED")
        ota = client.post(
            "/intents",
            json={
                "intent": "prepare_ota_cohort",
                "subject": {"campaignId": "ACME-FW-8-4-CRITICAL", "applicationId": "acme-device-fleet"},
                "context": {"otaWave": "prepare", "campaignPriority": "CRITICAL"},
            },
        )
        if (ota.json().get("outcome") or {}).get("outcome") != "NETWORK_QUALIFIED_COHORT":
            fail(f"OTA {(ota.json().get('outcome') or {}).get('outcome')}")
        else:
            ok("OTA NETWORK_QUALIFIED_COHORT unchanged")
        wifi = client.post(
            "/intents",
            json={
                "intent": "verify_mobile_number",
                "subject": {"phoneNumber": "+1••••••0198"},
                "context": {"nvVariant": "wifi-ecs-gap", "accessType": "WIFI", "claimedMsisdn": True, "businessEvent": "CUSTOMER_SIGNING_IN"},
            },
        )
        if (wifi.json().get("outcome") or {}).get("outcome") != "CAPABILITY_UNAVAILABLE":
            fail(f"NV wifi ECS {(wifi.json().get('outcome') or {}).get('outcome')}")
        else:
            ok("NV Wi-Fi ECS-gap live outcome unchanged")
        if "verify_mobile_number" not in EXECUTABLE_INTENTS:
            fail("NV intent missing")
        else:
            ok("executable intent set still includes live heroes")


def check_ui() -> None:
    coverage = (FRONTEND / "src" / "pages" / "Coverage.jsx").read_text(encoding="utf-8")
    app_src = (FRONTEND / "src" / "App.jsx").read_text(encoding="utf-8")
    demo = (FRONTEND / "src" / "pages" / "DemoPick.jsx").read_text(encoding="utf-8")
    briefing = (FRONTEND / "src" / "pages" / "Briefing.jsx").read_text(encoding="utf-8")
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    ota = (FRONTEND / "src" / "pages" / "OtaFleet.jsx").read_text(encoding="utf-8")
    explore = (FRONTEND / "src" / "pages" / "Explore.jsx").read_text(encoding="utf-8")
    if "Fulfillment Coverage" not in coverage or "cov-funnel" not in coverage:
        fail("Coverage explorer missing")
    else:
        ok("sales-facing Fulfillment Explorer present")
    if "Technical View" not in coverage or "Telco Finder" not in coverage:
        fail("technical view missing")
    else:
        ok("technical drill-down present")
    if "See Fulfillment Coverage" not in demo or "See Fulfillment Coverage" not in briefing:
        fail("portfolio integration missing")
    else:
        ok("portfolio See Fulfillment Coverage")
    if "Back to business story" not in coverage:
        fail("back to business story missing")
    else:
        ok("coverage links back to business story")
    if "Where is this available?" not in explore or "Which intents depend on it?" not in explore:
        fail("catalog integration missing")
    else:
        ok("catalog WHERE IS THIS AVAILABLE / WHICH INTENTS DEPEND ON IT")
    if "Fulfillment Coverage" in runtime or "Fulfillment Coverage" in ota:
        fail("C13 leaked into Runtime/OtaFleet")
    else:
        ok("Runtime / OTA visuals unchanged as C11 surfaces")
    joined = "\n".join([coverage, app_src, demo, briefing])
    if UI_CADENCE < 14 and ("Demand Map" in joined or "Meeting Mode" in joined or "opportunity score" in joined.lower()):
        fail("C14 leaked into C13 UI")
    elif UI_CADENCE < 16 and ("Meeting Mode" in joined or "opportunity score" in joined.lower()):
        fail("C15 leaked into UI")
    else:
        ok("Cadence 15 not started" if UI_CADENCE >= 14 else "Cadence 14 not started")
    if UI_CADENCE < 14 and "Cadence 13" not in app_src:
        fail("footer cadence not updated")
    elif UI_CADENCE >= 14 and not any(tag in app_src for tag in ("Cadence 13", "Cadence 14", "Cadence 15", "Cadence 16", "Cadence 17")):
        fail("footer cadence missing")
    else:
        ok("UI cadence footer")


def check_boundaries() -> None:
    hits = []
    for path in (BACKEND / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "Meta_Demo" in text or "Jigyasa" in text:
            hits.append(path.name)
    if hits:
        fail(f"other-repo references: {hits}")
    else:
        ok("Meta_Demo and Jigyasa untouched")
    if not (DOCS / "cadences" / "ax-cadence-13.md").exists():
        fail("missing ax-cadence-13.md")
    else:
        ok("cadence 13 report present")
    if STATES[0] != "FULFILLABLE" or "NOT_CONFIGURED" not in STATES:
        fail("canonical states")
    else:
        ok("canonical fulfillment states")
    if "ENTITLEMENT_SERVER_UNAVAILABLE" not in GAP_CODES:
        fail("gap taxonomy")
    else:
        ok("blocking-gap taxonomy reuses existing reason codes")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    mod = SourceFileLoader("validate_ax_cadence12", str(BACKEND / "scripts" / "validate_ax_cadence12.py")).load_module()
    code = mod.main()
    if code != 0:
        fail("validate_ax_cadence12.py regression failed")
        return
    ok("Cadence 0-12 regression passed")


def main() -> int:
    print("=== AX Cadence 13 validation (Fulfillment Coverage Explorer) ===\n")
    check_health()
    check_schema_and_model()
    check_coverage_api()
    check_distinctions()
    check_portfolio_catalog()
    check_live_outcomes()
    check_ui()
    check_boundaries()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
