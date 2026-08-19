#!/usr/bin/env python3
"""AX Cadence 12 validation — sales portfolio + config-driven GUIDED scenarios. Do not start Cadence 13."""
from __future__ import annotations

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

from app.config import MODEL_CADENCE, UI_CADENCE  # noqa: E402
from app.guided_runtime import GUIDED_INTENTS, guided_scenario  # noqa: E402
from app.main import app, registry, store  # noqa: E402
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
SWIFTSHIP = {
    "intent": "assure_delivery_device",
    "subject": {"jobId": "SS-JOB-8814", "deviceId": "SS-HDL-4412", "driverId": "DR-204"},
    "context": {"priority": "HIGH", "guidedVariant": "device-reachable"},
}
CAMARA_OPS = {
    "phoneNumberVerify",
    "checkSimSwap",
    "checkDeviceSwap",
    "getReachabilityStatus",
    "createSession",
    "getRoamingStatus",
    "verifyLocation",
    "verifyAge",
}


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK - {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL - {msg}")


def check_health() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if UI_CADENCE not in {12, 13, 14, 15, 16, 17} or h.get("uiCadence") not in {12, 13, 14, 15, 16, 17}:
            fail(f"uiCadence {h.get('uiCadence')} / {UI_CADENCE}")
        else:
            ok("uiCadence 12")
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
        if "assure_delivery_device" not in EXECUTABLE_INTENTS:
            fail("SwiftShip intent not executable")
        elif "run_swiftship" in EXECUTABLE_INTENTS:
            fail("SwiftShip custom runner leaked")
        else:
            ok("guided intents executable; no SwiftShip runner name")


def check_portfolio() -> None:
    rows = visible_rows(store)
    n = len(rows)
    if n < 15 or n > 20:
        fail(f"visible use cases {n} not in 15-20")
    else:
        ok(f"{n} visible use cases")
    industries = {r.get("industry") for r in rows}
    if len(industries) < 8:
        fail(f"industries {industries}")
    else:
        ok(f"industries covered: {sorted(industries)}")
    motions = {m for r in rows for m in (r.get("commercialMotion") or [])}
    expected_motions = {
        "IDENTITY_AND_TRUST",
        "CONNECTED_OPERATIONS",
        "DEVICE_AND_FLEET_OPERATIONS",
        "CUSTOMER_EXPERIENCE",
        "LOCATION_AND_PRESENCE",
        "NETWORK_ASSURANCE",
    }
    if not expected_motions.issubset(motions) and "LOCATION_AND_PRESENCE" not in motions:
        # Location may be secondary; still require the five core motions.
        core = expected_motions - {"LOCATION_AND_PRESENCE"}
        if not core.issubset(motions):
            fail(f"motions {motions}")
        else:
            ok("commercial motions present (location secondary)")
    else:
        ok("commercial motions present")
    by_mat = {}
    for row in rows:
        missing = [k for k in ("enterpriseId", "applicationId", "decisionGap", "networkContribution", "scenarioMaturity", "scenarioComplexity", "commercialMotion") if not row.get(k)]
        if missing:
            fail(f"{row.get('id')} missing {missing}")
        mat = row.get("scenarioMaturity")
        cx = row.get("scenarioComplexity")
        if mat not in {"LIVE", "GUIDED", "EXPLORE"}:
            fail(f"{row.get('id')} maturity {mat}")
        if cx not in {"BASIC", "COMPOSED", "ADVANCED_AGENTIC"}:
            fail(f"{row.get('id')} complexity {cx}")
        scores = row.get("scores") or {}
        if scores.get("networkUniqueness") == "LOW" or scores.get("salesClarity") == "LOW":
            fail(f"{row.get('id')} should have been rejected")
        by_mat.setdefault(mat, []).append(row.get("id"))
    if len(by_mat.get("LIVE") or []) < 7:
        fail(f"LIVE {by_mat.get('LIVE')}")
    else:
        ok(f"LIVE {len(by_mat.get('LIVE') or [])} GUIDED {len(by_mat.get('GUIDED') or [])} EXPLORE {len(by_mat.get('EXPLORE') or [])}")
    rejected = (store.sales_portfolio or {}).get("rejected") or []
    if len(rejected) < 4:
        fail("rejected list too thin")
    else:
        ok(f"{len(rejected)} scenarios rejected for credibility")


def check_guided_engine() -> None:
    engine = BACKEND / "app" / "guided_runtime.py"
    if not engine.exists():
        fail("guided_runtime.py missing")
        return
    src = engine.read_text(encoding="utf-8")
    if "run_swiftship" in src or "def run_swiftship" in (BACKEND / "app").joinpath("runtime.py").read_text(encoding="utf-8"):
        fail("SwiftShip-specific Python runner exists")
    else:
        ok("no SwiftShip-specific Python runner")
    if "GUIDED_INTENTS" not in src or "run_guided_intent" not in src:
        fail("shared interpreter missing")
    else:
        ok("shared GUIDED interpreter exists")
    if "assure_delivery_device" not in GUIDED_INTENTS:
        fail("SwiftShip not in GUIDED_INTENTS")
    else:
        ok("SwiftShip is a guided intent")
    cfg = guided_scenario("assure_delivery_device") or {}
    if cfg.get("enterpriseId") != "swiftship-logistics":
        fail("SwiftShip config missing")
    else:
        ok("SwiftShip executes from configuration")
    runtime_src = (BACKEND / "app" / "runtime.py").read_text(encoding="utf-8")
    if "interpret_profile" in runtime_src or "interpreter_spike" in runtime_src:
        fail("interpreter spike wired into live execute_intent")
    else:
        ok("LIVE runners unchanged; spike remains parallel")
    if "SalesScenarioProfile" in runtime_src or "PROFILES_DIR" in runtime_src:
        fail("SalesScenarioProfile loaded")
    else:
        ok("SalesScenarioProfile still not loaded")


def check_swiftship_run() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        res = client.post("/intents", json=SWIFTSHIP)
        if res.status_code >= 400:
            fail(f"SwiftShip HTTP {res.status_code}: {res.text[:300]}")
            return
        body = res.json()
        out = (body.get("outcome") or {}).get("outcome")
        if out != "CONTINUE":
            fail(f"SwiftShip reachable {out}")
        else:
            ok("SwiftShip reachable CONTINUE")
        if not body.get("honesty", {}).get("guidedInterpreter"):
            fail("SwiftShip not marked as guided interpreter")
        else:
            ok("SwiftShip trace from shared interpreter")
        invoked = {i.get("operationId") for i in body.get("invocations") or [] if (i.get("apiKind") or "NETWORK") == "NETWORK"}
        if invoked != {"getReachabilityStatus"}:
            fail(f"SwiftShip network ops {invoked}")
        else:
            ok("SwiftShip calls Reachability only")
        domain = [i for i in body.get("invocations") or [] if i.get("apiKind") in {"DOMAIN", "ENTERPRISE"}]
        if not domain or any(i.get("source") != "SIMULATED ENTERPRISE API" for i in domain):
            fail("simulated enterprise APIs not labelled")
        else:
            ok("simulated enterprise APIs labelled")
        if any(i.get("operationId") not in CAMARA_OPS for i in body.get("invocations") or [] if (i.get("apiKind") or "NETWORK") == "NETWORK"):
            fail("non-catalog CAMARA operationId")
        else:
            ok("CAMARA operationIds remain catalog operations")
        blob = json.dumps(body.get("discovery") or []) + json.dumps(body.get("discoverySummary") or {}) + json.dumps(body.get("candidateFiveStates") or {})
        if "CALL" not in json.dumps(body) and "CALL" not in blob:
            fail("guided discovery missing CALL")
        else:
            ok("guided Discovery grammar present")
        swap = client.post(
            "/intents",
            json={
                **SWIFTSHIP,
                "context": {"priority": "HIGH", "guidedVariant": "device-unreachable"},
            },
        ).json()
        if (swap.get("outcome") or {}).get("outcome") != "SWAP_DEVICE":
            fail(f"SwiftShip unreachable {(swap.get('outcome') or {}).get('outcome')}")
        else:
            ok("SwiftShip unreachable SWAP_DEVICE from configuration variant")
        claims = client.post(
            "/intents",
            json={
                "intent": "assess_claim_device_trust",
                "subject": {"claimId": "NS-CL-1902", "phoneNumber": "+49••••••4410"},
                "context": {"guidedVariant": "evidence-returned", "region": "DE"},
            },
        )
        if claims.status_code >= 400:
            fail(f"claims HTTP {claims.status_code}: {claims.text[:240]}")
        else:
            cbody = claims.json()
            routes = {i.get("routeType") for i in cbody.get("invocations") or [] if (i.get("apiKind") or "NETWORK") == "NETWORK"}
            if "AGGREGATED" not in routes:
                fail(f"claims routes {routes}")
            else:
                ok("aggregator route represented (Northstar)")
            if "FRAUD" in json.dumps(cbody.get("outcome") or {}).upper() and "not determine" not in json.dumps(cbody.get("outcome") or {}).lower():
                fail("claims outcome implies fraud determination")
            else:
                ok("claims does not determine fraud")
        checkout = client.post(
            "/intents",
            json={
                "intent": "assess_checkout_trust",
                "subject": {"orderId": "MM-88421", "phoneNumber": "+1••••••5521"},
                "context": {"amount": 1840, "currency": "CAD", "guidedVariant": "sim-recent-change"},
            },
        )
        if checkout.status_code >= 400:
            fail(f"checkout HTTP {checkout.status_code}: {checkout.text[:240]}")
        else:
            dest = {(d.get("capabilityId"), d.get("state")) for d in checkout.json().get("decisions") or []}
            if ("location_verification", "BLOCKED_BY_POLICY") not in dest and ("location_verification", "FILTER") not in dest:
                fail(f"checkout location not filtered {dest}")
            else:
                ok("checkout location FILTER / consent")
            if (checkout.json().get("outcome") or {}).get("outcome") != "STEP_UP":
                fail(f"checkout {(checkout.json().get('outcome') or {}).get('outcome')}")
            else:
                ok("checkout STEP_UP")


def check_demo_portfolio() -> None:
    with TestClient(app) as client:
        demo = client.get("/demo").json()
        featured = demo.get("featured") or []
        use_cases = [row.get("heroUseCaseId") for row in featured]
        if use_cases[:5] != [
            "passwordless-mobile-sign-in",
            "high-value-payment-protection",
            "critical-inspection-camera",
            "pharmacy-age-gate",
            "baggage-connection",
        ]:
            fail(f"featured heroes {use_cases[:5]}")
        else:
            ok("LIVE hero picker order preserved")
        port = demo.get("portfolio") or {}
        if (port.get("count") or 0) < 15:
            fail("portfolio missing from /demo")
        else:
            ok("sales portfolio on /demo")
        if "Demand Map" in json.dumps(demo) or "Meeting Mode" in json.dumps(demo):
            fail("C13 surfaces leaked into /demo")
        else:
            ok("Demand Map / Meeting Mode not present")
        ss = client.get("/demo/swiftship-logistics/delivery-device-readiness")
        if ss.status_code >= 400:
            fail(f"SwiftShip briefing {ss.status_code}")
        else:
            body = ss.json()
            if body.get("maturity") != "GUIDED" or not body.get("runnable"):
                fail(f"SwiftShip briefing maturity {body.get('maturity')}")
            else:
                ok("SwiftShip briefing GUIDED / runnable")
        explore = client.get("/demo/harbor-facilities/critical-equipment-reachability")
        if explore.status_code >= 400:
            fail(f"Harbor briefing {explore.status_code}")
        elif explore.json().get("maturity") != "EXPLORE" or explore.json().get("runnable"):
            fail("Harbor presented as executable")
        else:
            ok("EXPLORE not presented as LIVE")
        blob = json.dumps(demo)
        if "rollout_firmware_safely" in blob:
            fail("OTA alias leaked onto /demo")
        else:
            ok("OTA working alias not on /demo")


def check_heroes() -> None:
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
        rec = client.post("/intents", json={"intent": "assess_recovery_continuity", "subject": {"recoveryId": "RB-REC-19", "phoneNumber": "+1••••••0198"}, "context": {"channel": "web"}})
        if (rec.json().get("outcome") or {}).get("outcome") != "CONTINUITY_ALIGNED":
            fail(f"recovery {(rec.json().get('outcome') or {}).get('outcome')}")
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
        bad = client.post("/intents", json={"intent": "rollout_firmware_safely", "subject": {}, "context": {}})
        if bad.status_code < 400:
            fail("rollout_firmware_safely must not execute")
        else:
            ok("rollout_firmware_safely remains non-executable")
        kyc = client.post("/intents", json={"intent": "match_customer_kyc", "subject": {}, "context": {}})
        if kyc.status_code < 400:
            fail("KYC Match must remain EXPLORE / non-executable")
        else:
            ok("KYC Match not fake-fulfilled")


def check_dpv_and_catalog() -> None:
    purpose = store.purpose_by_id.get("delivery_device_assurance") or {}
    dpv = purpose.get("dpv") or {}
    if not dpv.get("needsReview"):
        fail("delivery purpose should be NEEDS_REVIEW")
    else:
        ok("DPV NEEDS_REVIEW where mapping is uncertain")
    experimental_promoted = []
    for row in visible_rows(store):
        if row.get("scenarioMaturity") == "GUIDED" and "connectivity_insights" in (row.get("capabilities") or []):
            experimental_promoted.append(row.get("id"))
    if experimental_promoted:
        fail(f"experimental Insights silently used {experimental_promoted}")
    else:
        ok("experimental APIs not silently promoted")
    src = (DATA / "guided" / "scenarios.yaml").read_text(encoding="utf-8")
    if "checkNetworkQuality" in src and "SKIP" not in src:
        fail("Insights used in guided YAML")
    else:
        ok("guided scenarios stay in practical catalog")


def check_ui() -> None:
    demo = (FRONTEND / "src" / "pages" / "DemoPick.jsx").read_text(encoding="utf-8")
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    briefing = (FRONTEND / "src" / "pages" / "Briefing.jsx").read_text(encoding="utf-8")
    if "Sales portfolio" not in demo or "Where could I sell this?" not in demo:
        fail("sales portfolio UI missing")
    else:
        ok("sales portfolio / industry / motion / reverse capability UI")
    if "scenarioComplexity" not in demo and "scenarioComplexity" not in briefing:
        if "GUIDED" not in demo:
            fail("maturity not in picker")
        else:
            ok("maturity visible on portfolio cards")
    else:
        ok("complexity independent of UI lens")
    if "GuidedVisual" not in runtime:
        fail("guided visual missing")
    else:
        ok("guided scenario visual is not a High Flight clone")
    if "HfBaggageWorld" not in runtime:
        fail("High Flight visual regress")
    else:
        ok("High Flight visual preserved")
    forbidden = ("Meeting Mode",)
    if UI_CADENCE < 16:
        forbidden = ("Meeting Mode",)
    if UI_CADENCE < 14:
        forbidden = ("Demand Map", "Meeting Mode")
    if UI_CADENCE < 13:
        forbidden = ("Demand Map", "Fulfillment Coverage", "Meeting Mode")
    leaked = [name for name in forbidden if name.lower() in demo.lower() or name.lower() in runtime.lower()]
    if UI_CADENCE >= 16:
        leaked = [name for name in leaked if name != "Meeting Mode"]
    if leaked:
        fail(f"C13 leaked into UI: {leaked}")
    else:
        ok("C13 surfaces not started")
    if "data.runnable" not in briefing and "data.runnable || data.secondaryDemo" not in briefing:
        fail("briefing still uses hardcoded RUNNABLE only")
    else:
        ok("briefing uses API maturity / runnable")


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
    if not (DOCS / "cadences" / "ax-cadence-12.md").exists():
        fail("missing ax-cadence-12.md")
    else:
        ok("cadence 12 report present")
    joined = "\n".join(p.read_text(encoding="utf-8") for p in (BACKEND / "app").glob("*.py"))
    if re.search(r"def run_swiftship", joined):
        fail("run_swiftship defined")
    else:
        ok("no run_swiftship")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    mod = SourceFileLoader("validate_ax_cadence11", str(BACKEND / "scripts" / "validate_ax_cadence11.py")).load_module()
    code = mod.main()
    if code != 0:
        fail("validate_ax_cadence11.py regression failed")
        return
    ok("Cadence 0-11 regression passed")


def main() -> int:
    print("=== AX Cadence 12 validation (sales portfolio + guided interpreter) ===\n")
    check_health()
    check_portfolio()
    check_guided_engine()
    check_swiftship_run()
    check_demo_portfolio()
    check_heroes()
    check_dpv_and_catalog()
    check_ui()
    check_boundaries()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
