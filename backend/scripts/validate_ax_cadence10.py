#!/usr/bin/env python3
"""AX Cadence 10 validation — Decision Gap + High Flight baggage evolution. Do not start Cadence 11."""
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
from app.intent_profile import LIVE_PROFILE_INTENTS  # noqa: E402
from app.interpreter_spike import citycare_spike_agrees_with_live, interpret_profile  # noqa: E402
from app.main import app, registry, store  # noqa: E402
from app.runtime import EXECUTABLE_INTENTS  # noqa: E402

errors: list[str] = []
oks: list[str] = []

LIVE = [
    "verify_mobile_number",
    "assess_network_trust",
    "assess_recovery_continuity",
    "maintain_inspection_experience",
    "verify_pharmacy_age_gate",
    "ensure_baggage_connection",
]


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK - {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL - {msg}")


def _post(client: TestClient, body: dict) -> dict:
    res = client.post("/intents", json=body)
    if res.status_code >= 400:
        fail(f"{body.get('intent')} HTTP {res.status_code}: {res.text[:240]}")
        return {}
    return res.json()


def check_health() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if UI_CADENCE < 10 or h.get("uiCadence") not in {10, 11, 12, 13, 14, 15, 16, 17}:
            fail(f"uiCadence {h.get('uiCadence')}")
        else:
            ok(f"uiCadence {h.get('uiCadence')}")
        if h.get("modelCadence") != 7 or MODEL_CADENCE != 7:
            fail(f"modelCadence {h.get('modelCadence')}")
        else:
            ok("modelCadence 7")
        if h.get("version") != "0.6.1-ax6.1":
            fail(f"live version {h.get('version')}")
        else:
            ok("live version 0.6.1-ax6.1")
        if {"rollout_firmware_safely", "assure_ramp_scan_capability"} & set(EXECUTABLE_INTENTS):
            fail("Cadence 11 intents leaked")
        else:
            ok("OTA / alias Intent not executable")
        if len(registry.families) != 13:
            fail(f"catalog {len(registry.families)}")
        else:
            ok("catalog remains 13 families")


def check_profiles() -> None:
    schema = json.loads((DATA / "schemas" / "intent-profile.json").read_text(encoding="utf-8"))
    required = set(schema.get("required") or [])
    if not {
        "intentId",
        "label",
        "businessOutcome",
        "complexity",
        "decisionGap",
        "networkContributionTier",
    } <= required:
        fail("IntentProfile schema missing required fields")
    else:
        ok("IntentProfile schema present")
    ids = {p.get("intentId") for p in store.intent_profiles}
    if set(LIVE_PROFILE_INTENTS) - ids:
        fail(f"missing profiles {set(LIVE_PROFILE_INTENTS) - ids}")
    else:
        ok("IntentProfile exists for every live Intent")
    complexities = {p.get("complexity") for p in store.intent_profiles}
    if not {"COMPOSED", "ADVANCED_AGENTIC"} <= complexities:
        fail(f"scenarioComplexity missing {complexities}")
    else:
        ok("scenarioComplexity is a model dimension")
    gap_keys = {"alreadyHave", "decide", "gap", "networkAdds", "ax", "outcome"}
    for intent in LIVE:
        profile = store.intent_profile_by_id.get(intent) or {}
        gap = profile.get("decisionGap") or {}
        if set(gap_keys) - set(gap):
            fail(f"{intent} Decision Gap incomplete")
        else:
            ok(f"{intent} Decision Gap complete")


def check_request_small_and_gap() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        bodies = [
            {"intent": "verify_mobile_number", "subject": {"phoneNumber": "+1••••••0198"}, "context": {"nvVariant": "cellular-nv1", "accessType": "CELLULAR"}},
            {"intent": "assess_network_trust", "subject": {"transactionId": "RB-78421", "phoneNumber": "+1••••••0198"}, "context": {"amount": 25000, "currency": "USD"}},
            {"intent": "maintain_inspection_experience", "subject": {"cameraId": "ACME-CAM-14", "lineId": "LINE-B"}, "context": {"sloMs": 40}},
            {"intent": "verify_pharmacy_age_gate", "subject": {"transactionId": "RX-10442", "phoneNumber": "+1••••••8843"}, "context": {"ageThreshold": 18}},
            {"intent": "ensure_baggage_connection", "subject": {"bagId": "HF123456", "connectingFlight": "HF281"}, "context": {"priority": "high"}},
        ]
        expected = {
            "verify_mobile_number": "VERIFIED",
            "assess_network_trust": "STEP_UP",
            "maintain_inspection_experience": "ASSURED",
            "verify_pharmacy_age_gate": "ELIGIBLE",
            "ensure_baggage_connection": "CONTINUE",
        }
        for body in bodies:
            trace = _post(client, body)
            if not trace:
                continue
            req = trace.get("request") or {}
            if set(req.keys()) - {"intent", "subject", "context", "agentId"}:
                fail(f"{body['intent']} request grew extra fields {req.keys()}")
            else:
                ok(f"{body['intent']} request body remains small")
            if not (trace.get("decisionGap") or {}).get("gap"):
                fail(f"{body['intent']} missing Decision Gap on trace")
            else:
                ok(f"{body['intent']} trace has Decision Gap")
            if (trace.get("outcome") or {}).get("outcome") != expected[body["intent"]]:
                fail(f"{body['intent']} outcome {(trace.get('outcome') or {}).get('outcome')}")
            else:
                ok(f"{body['intent']} -> {expected[body['intent']]}")
            if (trace.get("intentProfile") or {}).get("intentId") != body["intent"]:
                fail(f"{body['intent']} profile not attached")
            else:
                ok(f"{body['intent']} IntentProfile attached from configuration")
            if not any((p.get("layer") for p in trace.get("policyEvaluations") or [])):
                fail(f"{body['intent']} missing policy provenance layers")
            else:
                ok(f"{body['intent']} policy provenance labels present")
            if body["intent"] != "verify_mobile_number" and "nv1" in json.dumps(req).lower():
                fail("NV path leaked onto another Intent request")
        client.post("/executions/reset")
        client.post("/intents", json=bodies[1])
        rec = _post(
            client,
            {
                "intent": "assess_recovery_continuity",
                "subject": {"recoveryId": "RB-REC-19", "phoneNumber": "+1••••••0198"},
                "context": {"channel": "web"},
            },
        )
        if (rec.get("outcome") or {}).get("outcome") != "CONTINUITY_ALIGNED":
            fail("recovery changed")
        else:
            ok("Recovery CONTINUITY_ALIGNED unchanged")
        if not (rec.get("decisionGap") or {}).get("gap"):
            fail("recovery missing Decision Gap")
        else:
            ok("recovery Decision Gap present")


def check_nv_simulation() -> None:
    nv = (FRONTEND / "src" / "pages" / "NvPath.jsx").read_text(encoding="utf-8")
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    if "Simulate runtime context" not in nv:
        fail("NV selector not labelled as simulation")
    else:
        ok("NV selector is presenter/demo simulation")
    if "Application chooses" not in nv or "NetAware chooses" not in nv:
        fail("who-chooses strip missing")
    else:
        ok("application chooses Intent; NetAware chooses NV1/NV2 path")
    with TestClient(app) as client:
        cellular = _post(
            client,
            {
                "intent": "verify_mobile_number",
                "subject": {"phoneNumber": "+1••••••0198"},
                "context": {"nvVariant": "cellular-nv1", "accessType": "CELLULAR"},
            },
        )
        wifi = _post(
            client,
            {
                "intent": "verify_mobile_number",
                "subject": {"phoneNumber": "+1••••••0198"},
                "context": {"nvVariant": "wifi-nv2", "accessType": "WIFI"},
            },
        )
        gap = _post(
            client,
            {
                "intent": "verify_mobile_number",
                "subject": {"phoneNumber": "+1••••••0198"},
                "context": {"nvVariant": "wifi-ecs-gap", "accessType": "WIFI"},
            },
        )
        if (cellular.get("pathSelection") or {}).get("selectedPath") != "NV1_NETWORK_BASED":
            fail("C9 cellular NV1 changed")
        elif (wifi.get("pathSelection") or {}).get("selectedPath") != "NV2_OPERATOR_TOKEN":
            fail("C9 wifi NV2 changed")
        elif (gap.get("outcome") or {}).get("outcome") != "CAPABILITY_UNAVAILABLE":
            fail("C9 ECS gap changed")
        else:
            ok("C9 NV engine semantics unchanged")
        if (cellular.get("request") or {}).get("intent") != "verify_mobile_number":
            fail("NV request intent drifted")
        else:
            ok("NV HTTP request still only verify_mobile_number")
    change = re.search(r"const changeLens = \((.*?)\) => \{([\s\S]*?)\n  \};", runtime)
    if not change:
        fail("changeLens missing")
    elif "apiPost" in change.group(2) or "/intents" in change.group(2):
        fail("switching lens reruns the scenario")
    else:
        ok("lens switch does not rerun")


def check_high_flight() -> None:
    with TestClient(app) as client:
        ready = _post(
            client,
            {
                "intent": "ensure_baggage_connection",
                "subject": {"bagId": "HF123456", "connectingFlight": "HF281"},
                "context": {"priority": "high", "hfVariant": "scanner-ready"},
            },
        )
        down = _post(
            client,
            {
                "intent": "ensure_baggage_connection",
                "subject": {"bagId": "HF123456", "connectingFlight": "HF281"},
                "context": {"priority": "high", "hfVariant": "scanner-unreachable"},
            },
        )
        if not ready or not down:
            return
        if ready.get("intentId") != down.get("intentId"):
            fail("High Flight Intent drifted across states")
        else:
            ok("same High Flight Intent across READY / NOT_REACHABLE")
        if (ready.get("outcome") or {}).get("outcome") != "CONTINUE":
            fail(f"READY outcome {(ready.get('outcome') or {}).get('outcome')}")
        else:
            ok("scanner READY → CONTINUE")
        if (down.get("outcome") or {}).get("outcome") != "SWAP_DEVICE":
            fail(f"UNREACHABLE outcome {(down.get('outcome') or {}).get('outcome')}")
        else:
            ok("scanner NOT_REACHABLE → SWAP_DEVICE")
        blob = json.dumps(ready) + json.dumps(down)
        if "EXPEDITE_TRANSFER" in blob or '"AT_RISK"' in json.dumps(ready.get("outcome") or {}):
            fail("featured High Flight still expedite/AT_RISK")
        else:
            ok("EXPEDITE_TRANSFER is not the featured network-driven outcome")
        if "HF123456" not in blob or "HF-HDL-0192" not in blob:
            fail("bag or scanner missing")
        else:
            ok("bag remains domain context; scanner is network subject")
        if "BRS" not in blob or "DCS" not in blob:
            fail("BRS/DCS missing from High Flight trace")
        else:
            ok("BRS / DCS / Ground Operations remain enterprise systems")
        invoked_ready = {i.get("operationId") for i in ready.get("invocations") or []}
        invoked_down = {i.get("operationId") for i in down.get("invocations") or []}
        if "verifyLocation" in invoked_ready | invoked_down:
            fail("Network Location used")
        else:
            ok("no Network Location as bag tracking")
        if "getReachabilityStatus" not in invoked_ready:
            fail("READY missing reachability")
        else:
            ok("Reachability invoked")
        if "assignAlternateScanner" not in invoked_down:
            fail("UNREACHABLE missing enterprise device swap")
        else:
            ok("alternate scanner is an ENTERPRISE inventory action")
        swap = next((i for i in down.get("invocations") or [] if i.get("operationId") == "assignAlternateScanner"), {})
        if swap.get("apiKind") != "ENTERPRISE":
            fail("device swap labelled as Network API")
        else:
            ok("device swap is not a Network API")
        loc = next((d for d in ready.get("decisions") or [] if d.get("capabilityId") == "location_verification"), {})
        qod = next((d for d in ready.get("decisions") or [] if d.get("capabilityId") == "quality_on_demand"), {})
        if loc.get("state") != "NOT_REQUIRED" or qod.get("state") != "NOT_REQUIRED":
            fail(f"Location/QoD {loc.get('state')} {qod.get('state')}")
        else:
            ok("Location and QoD NOT_REQUIRED by default")
        demand = down.get("demandSupply") or down.get("networkOpportunity") or {}
        if demand.get("apiSuccessfullyReportedUnreachable") is not True:
            fail("unreachable success not distinguished from unfulfilled demand")
        elif demand.get("demandFulfilled") is False:
            fail("successful unreachable report mislabelled unfulfilled demand")
        else:
            ok("API-success/unreachable is not unfulfilled demand")
        visual = ready.get("hfVisual") or {}
        if not visual.get("baggageWorld"):
            fail("Baggage world visual missing")
        else:
            ok("Baggage world visual present")


def check_spike() -> None:
    profile = store.intent_profile_by_id.get("verify_pharmacy_age_gate") or {}
    interpreted = interpret_profile(profile)
    if interpreted.get("notALiveRunner") is not True:
        fail("spike must declare it is not a live runner")
    else:
        ok("shared interpreter spike is not a live runner")
    if "verify_pharmacy_age_gate" in EXECUTABLE_INTENTS and citycare_spike_agrees_with_live(profile, "ELIGIBLE"):
        ok("CityCare spike agrees with live ELIGIBLE without forking the runner")
    else:
        fail("CityCare spike disagrees or forked")
    src = (BACKEND / "app" / "runtime.py").read_text(encoding="utf-8")
    if "interpret_profile" in src or "interpreter_spike" in src:
        fail("spike wired into live execute_intent")
    else:
        ok("spike is parallel/read-only")


def check_ui() -> None:
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    gap = (FRONTEND / "src" / "pages" / "DecisionGap.jsx").read_text(encoding="utf-8")
    if "DecisionGapVisual" not in runtime or "You already have" not in gap:
        fail("Decision Gap visual missing")
    else:
        ok("Decision Gap visual on live runtime")
    if "HfBaggageWorld" not in runtime or "HfVariantBar" not in runtime:
        fail("High Flight baggage world / variant bar missing")
    else:
        ok("High Flight BRS/DCS visual and two-state selector")
    leaked = [
        name
        for name in ("Demand Map", "Meeting Mode", "rollout_firmware_safely", "SalesScenarioProfile")
        if name.lower() in runtime.lower()
    ]
    if leaked:
        fail(f"Cadence 11+ leaked into Runtime: {leaked}")
    else:
        ok("OTA / Demand Map / Meeting Mode / MCP not started")


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
    if not (DOCS / "cadences" / "ax-cadence-10.md").exists():
        fail("missing ax-cadence-10.md")
    else:
        ok("cadence 10 report present")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    mod = SourceFileLoader("validate_ax_cadence9", str(BACKEND / "scripts" / "validate_ax_cadence9.py")).load_module()
    code = mod.main()
    if code != 0:
        fail("validate_ax_cadence9.py regression failed")
        return
    ok("Cadence 0-9 regression passed")


def main() -> int:
    print("=== AX Cadence 10 validation (Decision Gap + High Flight evolution) ===\n")
    check_health()
    check_profiles()
    check_request_small_and_gap()
    check_nv_simulation()
    check_high_flight()
    check_spike()
    check_ui()
    check_boundaries()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
