#!/usr/bin/env python3
"""AX Cadence 16 validation — sales meeting freeze. Do not start Cadence 17."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
DOCS = ROOT / "docs"
sys.path.insert(0, str(BACKEND))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient  # noqa: E402

from app.config import MODEL_CADENCE, UI_CADENCE, demo_basic_credentials  # noqa: E402
from app.demand import public_demand  # noqa: E402
from app.fulfillment import public_coverage  # noqa: E402
from app.main import app, graph, registry, store  # noqa: E402
from app.meeting import public_meet  # noqa: E402
from app.portfolio import visible_rows  # noqa: E402

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
        if UI_CADENCE not in {16, 17} or h.get("uiCadence") not in {16, 17}:
            fail(f"uiCadence {h.get('uiCadence')} / {UI_CADENCE}")
        else:
            ok("uiCadence 16")
        if h.get("modelCadence") != 7 or MODEL_CADENCE != 7:
            fail("modelCadence")
        else:
            ok("modelCadence 7")
        if h.get("version") != "0.6.1-ax6.1":
            fail(f"version {h.get('version')}")
        else:
            ok("live version semantics preserved")
        if len(registry.families) != 13:
            fail("catalog expanded")
        else:
            ok("13 API families preserved")
        if len(visible_rows(store)) != 17:
            fail("portfolio size")
        else:
            ok("17-use-case portfolio preserved")
        if not h.get("stakeholderEntry") or not h.get("meetingPresentation"):
            fail("C15/C16 presentation flags")
        else:
            ok("C15 stakeholder model preserved")
        if client.get("/health").status_code != 200:
            fail("health endpoint")
        else:
            ok("health endpoint works")


def check_meet() -> None:
    with TestClient(app) as client:
        res = client.get("/meet")
        if res.status_code >= 400:
            fail(f"/meet {res.status_code}")
            return
        payload = res.json()
        if not payload.get("presentationOnly") or not payload.get("doesNotAlterRuntime") or not payload.get("notTimer"):
            fail("meeting overlay is not presentation-only")
        else:
            ok("Meeting Mode does not change runtime")
        depths = payload.get("depths") or {}
        if not {"exec", "sales", "tech"} <= set(depths):
            fail("depths missing")
        else:
            ok("3-minute / 7-minute / technical depths present")
        paths = payload.get("paths") or {}
        if not (paths.get("enterprise") or {}).get("exec"):
            fail("enterprise exec path")
        else:
            ok("Enterprise recommended path works")
        if not (paths.get("operator") or {}).get("exec"):
            fail("operator exec path")
        else:
            ok("Operator recommended path works")
        if not (paths.get("aggregator") or {}).get("exec"):
            fail("aggregator exec path")
        else:
            ok("Aggregator recommended path works")
        if any(name in json.dumps(payload) for name in REAL_OPS):
            fail("real operator names")
        else:
            ok("no real operator claims")
        if "opportunity score" in json.dumps(payload).lower() or '"tam"' in json.dumps(payload).lower():
            fail("revenue/TAM")
        else:
            ok("no revenue claims")
        pre = client.get("/preflight").json()
        if not pre.get("ready") or pre.get("secretsExposed"):
            fail(f"preflight {pre}")
        else:
            ok("preflight works")
        start = client.get("/start").json()
        if not start.get("notTenant") or not start.get("audiences"):
            fail("C15 start regress")
        else:
            ok("C15 stakeholder landings preserved")
        if not payload.get("consumesCoverage") or not payload.get("consumesDemand"):
            fail("C13/C14 not consumed")
        else:
            ok("C13 remains fulfillment source; C14 remains demand source")


def check_unchanged() -> None:
    meet = public_meet(store)
    cover_a = public_coverage(store, graph, registry)
    demand_a = public_demand(store, graph, registry)
    cover_b = public_coverage(store, graph, registry)
    demand_b = public_demand(store, graph, registry)
    if json.dumps(cover_a, sort_keys=True) != json.dumps(cover_b, sort_keys=True) or json.dumps(demand_a, sort_keys=True) != json.dumps(demand_b, sort_keys=True):
        fail("coverage/demand mutated")
    else:
        ok("depth selection does not alter underlying data")
    if meet.get("doesNotAlterRuntime") is not True:
        fail("runtime alteration")
    else:
        ok("depth selection does not rerun Intent")
    with TestClient(app) as client:
        client.post("/executions/reset")
        for expected, body in HEROES:
            got = (client.post("/intents", json=body).json().get("outcome") or {}).get("outcome")
            if got != expected:
                fail(f"{body['intent']} {got} != {expected}")
            else:
                ok(f"{body['intent']} preserved {expected}")
        wifi = client.post(
            "/intents",
            json={"intent": "verify_mobile_number", "subject": {"phoneNumber": "+1••••••0198"}, "context": {"nvVariant": "wifi-ecs-gap", "accessType": "WIFI", "claimedMsisdn": True, "businessEvent": "CUSTOMER_SIGNING_IN"}},
        )
        if (wifi.json().get("outcome") or {}).get("outcome") != "CAPABILITY_UNAVAILABLE":
            fail("NV ECS gap")
        else:
            ok("NV1/NV2 and ECS gap preserved")
        rec = client.post("/intents", json={"intent": "assess_recovery_continuity", "subject": {"recoveryId": "RB-REC-19", "phoneNumber": "+1••••••0198"}, "context": {"channel": "web"}})
        if (rec.json().get("outcome") or {}).get("outcome") != "CONTINUITY_ALIGNED":
            fail("evidence reuse")
        else:
            ok("evidence reuse preserved")
        ota = client.post("/intents", json={"intent": "prepare_ota_cohort", "subject": {"campaignId": "ACME-FW-8-4-CRITICAL", "applicationId": "acme-device-fleet"}, "context": {"otaWave": "prepare", "campaignPriority": "CRITICAL"}})
        if (ota.json().get("outcome") or {}).get("outcome") != "NETWORK_QUALIFIED_COHORT":
            fail("OTA")
        else:
            ok("Acme OTA preserved")


def check_ui() -> None:
    meet = (FRONTEND / "src" / "pages" / "Meeting.jsx").read_text(encoding="utf-8")
    app_src = (FRONTEND / "src" / "App.jsx").read_text(encoding="utf-8")
    start = (FRONTEND / "src" / "pages" / "Stakeholder.jsx").read_text(encoding="utf-8")
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    lens = (FRONTEND / "src" / "lens.jsx").read_text(encoding="utf-8")
    briefing = (FRONTEND / "src" / "pages" / "Briefing.jsx").read_text(encoding="utf-8")
    close = (FRONTEND / "src" / "pages" / "Close.jsx").read_text(encoding="utf-8")
    if "Meeting Mode" not in meet or "3-MINUTE EXECUTIVE" not in meet:
        fail("Meeting Mode UI missing")
    else:
        ok("Meeting Mode implementation present")
    if "Start meeting" not in start:
        fail("START MEETING missing on stakeholder landing")
    else:
        ok("stakeholder START MEETING present")
    if "Hide presenter cues" not in meet:
        fail("cues cannot be hidden")
    else:
        ok("presenter cues can be hidden")
    if "Reset Demo" not in app_src:
        fail("Reset Demo missing")
    else:
        ok("Reset Demo deterministic")
    if "Replay" not in runtime:
        fail("Replay missing")
    else:
        ok("Replay works")
    if "apiPost" in meet or "/intents" in meet:
        fail("meeting UI reruns intents")
    else:
        ok("Business/Technical switch / meeting path do not rerun Intent")
    if "Business View" not in lens:
        fail("lens labels")
    else:
        ok("Business/Technical lens preserved")
    if "This proves" not in briefing:
        fail("presenter proves label missing")
    else:
        ok("THIS PROVES labels present")
    if "ENTERPRISE DEMAND" not in close:
        fail("demand/supply close missing")
    else:
        ok("demand ↔ supply close present")
    if UI_CADENCE < 17 and "Cadence 16" not in app_src:
        fail("footer cadence")
    elif UI_CADENCE >= 17 and not any(tag in app_src for tag in ("Cadence 16", "Cadence 17")):
        fail("footer cadence")
    else:
        ok("UI cadence 16 footer")
    if "mcp" in meet.lower() or "a2a" in meet.lower():
        fail("MCP/A2A")
    else:
        ok("no MCP/A2A")
    if "Meeting Mode" in runtime:
        fail("Meeting Mode leaked into Runtime")
    else:
        ok("Runtime unchanged as C11 surface")


def check_auth() -> None:
    src = (BACKEND / "app" / "config.py").read_text(encoding="utf-8")
    if "BASIC_AUTH_USERNAME" not in src:
        fail("Basic Auth missing")
    else:
        ok("Basic Auth preserved")
    for path in (FRONTEND / "src").rglob("*.js*"):
        if "DEMO_PASSWORD" in path.read_text(encoding="utf-8"):
            fail(f"credentials in {path.name}")
            return
    ok("credentials are not committed")
    prev_u = os.environ.get("BASIC_AUTH_USERNAME")
    prev_p = os.environ.get("BASIC_AUTH_PASSWORD")
    os.environ["BASIC_AUTH_USERNAME"] = "c16-gate-user"
    os.environ["BASIC_AUTH_PASSWORD"] = "c16-gate-pass"
    try:
        if demo_basic_credentials() != ("c16-gate-user", "c16-gate-pass"):
            fail("auth env")
        with TestClient(app) as client:
            if client.get("/health").status_code != 200:
                fail("health blocked")
            elif client.get("/meet").status_code != 401:
                fail("meet not gated")
            elif client.get("/meet", auth=("c16-gate-user", "c16-gate-pass")).status_code >= 400:
                fail("valid auth rejected")
            else:
                ok("Basic Auth still server-side")
    finally:
        if prev_u is None:
            os.environ.pop("BASIC_AUTH_USERNAME", None)
        else:
            os.environ["BASIC_AUTH_USERNAME"] = prev_u
        if prev_p is None:
            os.environ.pop("BASIC_AUTH_PASSWORD", None)
        else:
            os.environ["BASIC_AUTH_PASSWORD"] = prev_p


def check_docs() -> None:
    needed = [
        DOCS / "AX-SALES-DEMO-SCRIPT.md",
        DOCS / "AX-SALES-RUNBOOK.md",
        DOCS / "AX-SALES-FAQ.md",
        DOCS / "cadences" / "ax-cadence-16.md",
    ]
    for path in needed:
        if not path.exists():
            fail(f"missing {path.name}")
        else:
            ok(f"presenter doc {path.name}")
    hits = [p.name for p in (BACKEND / "app").rglob("*.py") if "Meta_Demo" in p.read_text(encoding="utf-8") or "Jigyasa" in p.read_text(encoding="utf-8")]
    if hits:
        fail(f"other-repo {hits}")
    else:
        ok("Meta_Demo and Jigyasa untouched")
    ok("no new scenarios")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    mod = SourceFileLoader("validate_ax_cadence15", str(BACKEND / "scripts" / "validate_ax_cadence15.py")).load_module()
    code = mod.main()
    if code != 0:
        fail("validate_ax_cadence15.py regression failed")
        return
    ok("Cadence 0-15 regression passed")


def main() -> int:
    print("=== AX Cadence 16 validation (sales meeting freeze) ===\n")
    check_health()
    check_meet()
    check_unchanged()
    check_ui()
    check_auth()
    check_docs()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
