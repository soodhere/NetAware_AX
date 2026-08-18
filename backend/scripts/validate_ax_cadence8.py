#!/usr/bin/env python3
"""AX Cadence 8 validation — Discovery UX + Basic/Advanced lenses. No new live scenarios."""
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

from app.config import APP_VERSION, MODEL_CADENCE, SCHEMAS_DIR, UI_CADENCE  # noqa: E402
from app.discovery_trace import REASON_CODES, STAGE_GROUPS, discovery_event_valid  # noqa: E402
from app.main import app, registry  # noqa: E402
from app.runtime import EXECUTABLE_INTENTS  # noqa: E402

errors: list[str] = []
oks: list[str] = []

FUTURE_INTENTS = {"rollout_firmware_safely", "assure_ramp_scan_capability"}
C9_INTENT = "verify_mobile_number"
PICKER = ["rocket-bank", "acme-manufacturing", "citycare-health", "high-flight-airlines"]
C9_PICKER = [
    "passwordless-mobile-sign-in",
    "high-value-payment-protection",
    "critical-inspection-camera",
    "pharmacy-age-gate",
    "baggage-connection",
]
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
RECOVERY = {
    "intent": "assess_recovery_continuity",
    "subject": {"recoveryId": "RB-REC-19", "phoneNumber": "+1••••••0198"},
    "context": {"channel": "web"},
}


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK - {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL - {msg}")


def _select(events: list[dict], cap: str) -> list[dict]:
    return [e for e in events if e.get("capability") == cap and e.get("stage") == "SELECT"]


def check_health() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if h.get("version") != "0.6.1-ax6.1" or APP_VERSION != "0.6.1-ax6.1":
            fail(f"live version changed: {h.get('version')}")
        else:
            ok("live version 0.6.1-ax6.1")
        if h.get("cadence") != 6 or h.get("cadencePatch") != "6.1":
            fail("product cadence drifted from 6 / 6.1")
        else:
            ok("product cadence 6 / 6.1")
        if h.get("modelCadence") != 7 or MODEL_CADENCE != 7:
            fail(f"modelCadence {h.get('modelCadence')}")
        else:
            ok("modelCadence 7 (discovery enums)")
        if h.get("uiCadence") not in {8, 9} or UI_CADENCE < 8:
            fail(f"uiCadence {h.get('uiCadence')}")
        else:
            ok(f"uiCadence {h.get('uiCadence')}")
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
                fail("Cadence 9 NV intent missing")
            else:
                ok("Cadence 9 added verify_mobile_number only")
        else:
            ok("no new live intents")


def check_schema() -> None:
    schema = json.loads((SCHEMAS_DIR / "discovery-event.json").read_text(encoding="utf-8"))
    if set(schema.get("required") or []) < {"stage", "candidate", "candidateType", "capability", "result", "humanReason", "source"}:
        fail("discovery-event schema required fields incomplete")
    else:
        ok("discovery-event schema present")
    stages = ((schema.get("properties") or {}).get("stage") or {}).get("enum") or []
    if stages != list(STAGE_GROUPS):
        fail(f"schema stages {stages}")
    else:
        ok("schema uses Cadence 7 stage groups")


def check_live_discovery() -> None:
    with TestClient(app) as client:
        traces: dict[str, dict] = {}
        client.post("/executions/reset")
        for expected, body in HEROES:
            res = client.post("/intents", json=body)
            if res.status_code >= 400:
                fail(f"{body['intent']} HTTP {res.status_code}")
                continue
            payload = res.json()
            traces[body["intent"]] = payload
            outcome = (payload.get("outcome") or {}).get("outcome")
            if outcome != expected:
                fail(f"{body['intent']} outcome {outcome} != {expected}")
            else:
                ok(f"{body['intent']} outcome {expected}")
            events = payload.get("discovery") or []
            if not events:
                fail(f"{body['intent']} missing discovery[]")
                continue
            ok(f"{body['intent']} has {len(events)} discovery events")
            for event in events:
                problems = discovery_event_valid(event, REASON_CODES)
                if problems:
                    fail(f"{body['intent']} event {event.get('candidate')}: {problems[0]}")
                    break
            else:
                ok(f"{body['intent']} discovery events valid")
            if not payload.get("discoverySummary") or not payload.get("discoveryMatrix"):
                fail(f"{body['intent']} missing summary/matrix")
            else:
                ok(f"{body['intent']} Basic summary and Advanced matrix from same trace")
            purpose = payload.get("purpose") or {}
            if not (purpose.get("dpv") or {}).get("id", "").startswith("dpv:"):
                fail(f"{body['intent']} purpose is not DPV-backed")
            else:
                ok(f"{body['intent']} DPV {(purpose.get('dpv') or {}).get('id')}")
            finders = (payload.get("discoverySummary") or {}).get("finders") or {}
            if "telcoFinder" not in finders or "apiFinder" not in finders:
                fail(f"{body['intent']} finders collapsed")
            elif finders["telcoFinder"].get("role") == finders["apiFinder"].get("role"):
                fail("Telco Finder role equals API Finder role")
            else:
                ok(f"{body['intent']} Telco Finder distinct from API Finder")
            if not (finders.get("providerRoute") or {}).get("display"):
                fail(f"{body['intent']} provider/route missing")
            else:
                ok(f"{body['intent']} provider/route visible")
            rows = (payload.get("discoveryMatrix") or {}).get("rows") or []
            if not any(r.get("subscription") and r.get("entitlement") for r in rows):
                fail(f"{body['intent']} subscription/entitlement not separately shown")
            else:
                ok(f"{body['intent']} subscription and entitlement are separate matrix columns")

        rb = traces.get("assess_network_trust") or {}
        rb_sel = {e.get("capability"): e.get("reasonCode") for e in (rb.get("discovery") or []) if e.get("stage") == "SELECT"}
        if rb_sel.get("location_verification") != "CONSENT_MISSING":
            fail(f"Rocket Bank location {rb_sel.get('location_verification')}")
        elif rb_sel.get("number_recycling") != "NOT_REQUIRED":
            fail(f"Rocket Bank recycling {rb_sel.get('number_recycling')}")
        else:
            ok("Rocket Bank: location CONSENT_MISSING, recycling NOT_REQUIRED")
        selected = [c for c, code in rb_sel.items() if code == "SELECTED"]
        if len(selected) < 5:
            fail(f"Rocket Bank selected {selected}")
        else:
            ok(f"Rocket Bank selected {len(selected)} capabilities")

        cc = traces.get("verify_pharmacy_age_gate") or {}
        cc_sel = {e.get("capability"): e.get("reasonCode") for e in (cc.get("discovery") or []) if e.get("stage") == "SELECT"}
        if cc_sel.get("age_verification") != "SELECTED":
            fail(f"CityCare age {cc_sel.get('age_verification')}")
        elif cc_sel.get("kyc_match") != "AGREEMENT_GAP":
            fail(f"CityCare KYC {cc_sel.get('kyc_match')}")
        else:
            ok("CityCare: Age SELECTED, KYC AGREEMENT_GAP")

        acme = traces.get("maintain_inspection_experience") or {}
        dyn = (acme.get("discoverySummary") or {}).get("dynamicUsefulness") or {}
        if dyn.get("initial") != "NOT_REQUIRED" or dyn.get("afterBreach") != "SELECTED":
            fail(f"Acme QoD dynamic {dyn}")
        else:
            ok("Acme QoD: NOT_REQUIRED then SELECTED after breach")

        hf = traces.get("ensure_baggage_connection") or {}
        hf_sel = {e.get("capability"): e.get("reasonCode") for e in (hf.get("discovery") or []) if e.get("stage") == "SELECT"}
        if hf_sel.get("location_verification") != "CONSENT_MISSING":
            fail(f"High Flight location {hf_sel.get('location_verification')}")
        elif hf_sel.get("quality_on_demand") != "NOT_REQUIRED":
            fail(f"High Flight QoD {hf_sel.get('quality_on_demand')}")
        elif hf_sel.get("device_reachability") != "SELECTED" or hf_sel.get("connectivity_insights") != "SELECTED":
            fail(f"High Flight selected {hf_sel}")
        else:
            ok("High Flight: location filtered, reachability+connectivity selected, QoD NOT_REQUIRED")

        client.post("/intents", json=HEROES[0][1])
        rec = client.post("/intents", json=RECOVERY).json()
        if (rec.get("outcome") or {}).get("outcome") != "CONTINUITY_ALIGNED":
            fail(f"recovery outcome {(rec.get('outcome') or {}).get('outcome')}")
        reused = [
            e
            for e in (rec.get("discovery") or [])
            if e.get("stage") == "SELECT" and e.get("reasonCode") == "EVIDENCE_REUSED"
        ]
        if len(reused) < 1:
            fail("recovery missing EVIDENCE_REUSED discovery")
        elif rec.get("invocations"):
            fail("recovery invoked APIs instead of reuse")
        else:
            ok(f"evidence reuse discovery ({len(reused)} REUSE events, invocation skipped)")

        still_future = set(FUTURE_INTENTS)
        if UI_CADENCE < 9:
            still_future.add(C9_INTENT)
        for intent in still_future:
            bad = client.post("/intents", json={"intent": intent, "subject": {}, "context": {}})
            if bad.status_code < 400:
                fail(f"{intent} must not be executable")
        else:
            ok("OTA / ramp remain non-executable")


def check_picker_and_catalog() -> None:
    with TestClient(app) as client:
        demo = client.get("/demo").json()
        featured = demo.get("featured") or []
        ids = [(row.get("enterprise") or {}).get("id") for row in featured]
        use_cases = [row.get("heroUseCaseId") for row in featured]
        if UI_CADENCE >= 9:
            if use_cases[:5] != C9_PICKER:
                fail(f"C9 picker use cases {use_cases[:5]}")
            else:
                ok("picker: NV, Rocket Bank, Acme, CityCare, High Flight")
        elif ids[:4] != PICKER:
            fail(f"picker order {ids[:4]}")
        else:
            ok("picker: Rocket Bank, Acme, CityCare, High Flight")
        blob = json.dumps(demo)
        if "rollout_firmware_safely" in blob:
            fail("OTA cards leaked onto Home/picker payload")
        elif UI_CADENCE < 9 and "verify_mobile_number" in blob:
            fail("NV cards leaked onto Home/picker payload")
        else:
            ok("OTA not on Home/picker; NV only from Cadence 9")
        product = demo.get("product") or {}
        if "Agentic Experience" not in (product.get("line") or ""):
            fail("DX to AX home line missing")
        elif "relevant" not in (product.get("discoveryLine") or "").lower():
            fail("discovery line missing from product config")
        else:
            ok("Home still FROM DX TO AX, with discovery line")
        if len(registry.families) != 13:
            fail(f"catalog families {len(registry.families)}")
        else:
            ok("13-family catalog unchanged")


def check_lens_same_trace() -> None:
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    lens = (FRONTEND / "src" / "lens.jsx").read_text(encoding="utf-8")
    if "BASIC_TABS" not in runtime or "ADVANCED_TABS" not in runtime:
        fail("Basic/Advanced tabs missing")
    else:
        ok("Basic and Advanced tab sets present")
    if "sessionStorage" not in lens or 'LENS_KEY' not in lens:
        fail("lens is not session-persisted")
    else:
        ok("lens persisted in sessionStorage")
    change = re.search(r"const changeLens = \((.*?)\) => \{([\s\S]*?)\n  \};", runtime)
    if not change:
        fail("changeLens missing")
    elif "apiPost" in change.group(2) or "/intents" in change.group(2):
        fail("switching lens reruns the scenario")
    else:
        ok("switching lens does not rerun the scenario")
    if "readLens()" not in runtime or '=== "BASIC"' not in runtime:
        fail("default lens wiring missing")
    else:
        ok("default lens is BASIC")
    if "DiscoveryView" not in runtime:
        fail("Discovery view not wired")
    else:
        ok("Discovery is a first-class runtime tab")
    if "writeLens" not in (FRONTEND / "src" / "pages" / "Discovery.jsx").read_text(encoding="utf-8") + runtime:
        fail("lens write missing")
    explore = (FRONTEND / "src" / "pages" / "Explore.jsx").read_text(encoding="utf-8")
    if "DiscoveryLink" not in explore:
        fail("Explorer missing Discovery links")
    else:
        ok("Explorer links to live Discovery")


def check_no_second_engine() -> None:
    src = (BACKEND / "app" / "discovery_trace.py").read_text(encoding="utf-8")
    if "evaluate_capability_policy" not in src:
        fail("discovery is not derived from existing policy evaluation")
    else:
        ok("discovery maps existing runtime decisions (no second engine)")
    joined = (BACKEND / "app" / "runtime.py").read_text(encoding="utf-8")
    if "SalesScenarioProfile" in joined or "PROFILES_DIR" in joined:
        fail("runtime loads sales profiles")
    else:
        ok("SalesScenarioProfile still not loaded")


def check_boundaries() -> None:
    hits = []
    for path in (BACKEND / "app").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "Meta_Demo" in text or "Jigyasa" in text:
            hits.append(path.name)
    if hits:
        fail(f"other-repo references: {hits}")
    else:
        ok("Meta_Demo and Jigyasa untouched")
    if not (DOCS / "cadences" / "ax-cadence-8.md").exists():
        fail("missing ax-cadence-8.md")
    else:
        ok("cadence 8 report present")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    for name, rel in (
        ("validate_ax_cadence7", "validate_ax_cadence7.py"),
    ):
        mod = SourceFileLoader(name, str(BACKEND / "scripts" / rel)).load_module()
        code = mod.main()
        if code != 0:
            fail(f"{rel} regression failed")
            return
    ok("Cadence 0-7 regression passed")


def main() -> int:
    print("=== AX Cadence 8 validation (Discovery + Basic/Advanced) ===\n")
    check_health()
    check_schema()
    check_live_discovery()
    check_picker_and_catalog()
    check_lens_same_trace()
    check_no_second_engine()
    check_boundaries()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
