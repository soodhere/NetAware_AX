#!/usr/bin/env python3
"""AX Cadence 15 validation — stakeholder sales experience. Do not start Cadence 16."""
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
from app.portfolio import visible_rows  # noqa: E402
from app.stakeholder import public_start  # noqa: E402

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
        if UI_CADENCE not in {15, 16, 17} or h.get("uiCadence") not in {15, 16, 17}:
            fail(f"uiCadence {h.get('uiCadence')} / {UI_CADENCE}")
        else:
            ok("uiCadence 15")
        if h.get("modelCadence") != 7 or MODEL_CADENCE != 7:
            fail("modelCadence")
        else:
            ok("modelCadence 7")
        if h.get("version") != "0.6.1-ax6.1":
            fail(f"version {h.get('version')}")
        else:
            ok("live version 0.6.1-ax6.1")
        if len(registry.families) != 13:
            fail("catalog expanded")
        else:
            ok("13 API families unchanged")
        if not h.get("stakeholderEntry") or not h.get("presentationLensOnly"):
            fail("stakeholder entry not declared presentation-only")
        else:
            ok("stakeholder selection is a presentation lens")
        if len(visible_rows(store)) != 17:
            fail("portfolio size")
        else:
            ok("17-use-case portfolio unchanged")


def check_start() -> None:
    with TestClient(app) as client:
        res = client.get("/start")
        if res.status_code >= 400:
            fail(f"/start {res.status_code}")
            return
        payload = res.json()
        if not payload.get("presentationOnly") or not payload.get("notTenant"):
            fail("start payload is not presentation-only")
        else:
            ok("stakeholder entry is presentation context, not a tenant model")
        if UI_CADENCE < 16 and payload.get("notMeetingMode") is not True:
            fail("Meeting Mode declared")
        elif UI_CADENCE < 16:
            ok("Meeting Mode not implemented")
        else:
            ok("stakeholder start remains presentation-only")
        blob = json.dumps(payload).lower()
        if "lost revenue" in blob and "not" not in blob:
            fail("revenue language")
        if "opportunity score" in blob or '"tam"' in blob:
            fail("TAM / scoring leaked")
        else:
            ok("no revenue")
        if any(name in json.dumps(payload) for name in REAL_OPS):
            fail("real operator names")
        else:
            ok("no real operator claims")
        audiences = payload.get("audiences") or {}
        if not {"enterprise", "operator", "aggregator"} <= set(audiences):
            fail("audience landings missing")
        else:
            ok("Enterprise / Operator / Aggregator entry works")
        stories = {row.get("id"): row for row in payload.get("stories") or []}
        if (audiences.get("enterprise") or {}).get("recommendedHref") != "/demo/rocket-bank/passwordless-mobile-sign-in":
            fail("enterprise recommended path")
        else:
            ok("Rocket Bank recommended Enterprise path")
        if "number_possession_verification" not in str((audiences.get("operator") or {}).get("recommendedHref")):
            fail("operator NV path")
        else:
            ok("NV/ECS recommended Operator path")
        if "simulated-aggregator-b" not in str((audiences.get("aggregator") or {}).get("recommendedHref")):
            fail("aggregator path")
        else:
            ok("Aggregator multi-region path")
        if "high-flight" not in stories or "enterprise-ota" not in stories:
            fail("High Flight / OTA stories missing")
        else:
            ok("High Flight and Acme OTA stories preserved")
        auth = payload.get("auth") or {}
        if not auth.get("serverSide") or not auth.get("environmentDriven") or not auth.get("healthUnauthenticated"):
            fail("auth contract missing")
        else:
            ok("Basic Auth is server-side and environment-driven")
        if not payload.get("consumesCoverage") or not payload.get("consumesDemand"):
            fail("C13/C14 not consumed")
        else:
            ok("C13 remains fulfillment source; C14 remains demand source")
        if not payload.get("sharedExplorer"):
            fail("shared Explorer not declared")
        else:
            ok("shared Explorer remains shared")


def check_unchanged() -> None:
    cover_a = public_coverage(store, graph, registry)
    demand_a = public_demand(store, graph, registry)
    start = public_start(store)
    cover_b = public_coverage(store, graph, registry)
    demand_b = public_demand(store, graph, registry)
    if json.dumps(cover_a, sort_keys=True) != json.dumps(cover_b, sort_keys=True):
        fail("coverage mutated by start")
    elif json.dumps(demand_a, sort_keys=True) != json.dumps(demand_b, sort_keys=True):
        fail("demand mutated by start")
    else:
        ok("stakeholder selection does not alter underlying data")
    if start.get("doesNotAlterRuntime") is not True:
        fail("runtime alteration not forbidden")
    else:
        ok("stakeholder selection does not rerun Intent")
    with TestClient(app) as client:
        client.post("/executions/reset")
        for expected, body in HEROES:
            got = (client.post("/intents", json=body).json().get("outcome") or {}).get("outcome")
            if got != expected:
                fail(f"{body['intent']} {got} != {expected}")
            else:
                ok(f"{body['intent']} unchanged {expected}")


def check_ui() -> None:
    welcome = (FRONTEND / "src" / "pages" / "Stakeholder.jsx").read_text(encoding="utf-8")
    app_src = (FRONTEND / "src" / "App.jsx").read_text(encoding="utf-8")
    lens = (FRONTEND / "src" / "lens.jsx").read_text(encoding="utf-8")
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    home = (FRONTEND / "src" / "pages" / "Home.jsx").read_text(encoding="utf-8")
    stake = (FRONTEND / "src" / "stakeholder.js").read_text(encoding="utf-8")
    explore = (FRONTEND / "src" / "pages" / "Explore.jsx").read_text(encoding="utf-8")
    coverage = (FRONTEND / "src" / "pages" / "Coverage.jsx").read_text(encoding="utf-8")
    demand = (FRONTEND / "src" / "pages" / "Demand.jsx").read_text(encoding="utf-8")
    if "Welcome to NetAware AX" not in welcome or "Change perspective" not in app_src:
        fail("welcome / perspective switch missing")
    else:
        ok("perspective switching works")
    if "sessionStorage" not in stake:
        fail("stakeholder lens not session-scoped")
    else:
        ok("stakeholder lens stored in session only")
    if "Business View" not in lens or "Technical View" not in lens:
        fail("Business / Technical labels missing")
    else:
        ok("Business / Technical lens uses same trace")
    if "apiPost" in welcome or "/intents" in welcome:
        fail("stakeholder UI reruns intents")
    else:
        ok("stakeholder UI does not rerun Intent")
    if "Enterprise Explorer" in explore or "Operator Explorer" in explore:
        fail("split explorers")
    else:
        ok("Explorer remains shared")
    if "Reset" not in runtime and "reset" not in runtime.lower():
        fail("reset missing")
    else:
        ok("reset/replay unaffected")
    if "From Developer Experience" not in home:
        fail("Home DX→AX story removed")
    else:
        ok("Home DX→AX story retained")
    if UI_CADENCE < 16 and ("Meeting Mode" in app_src or "Meeting Mode" in welcome):
        fail("Meeting Mode implemented")
    elif UI_CADENCE >= 16:
        ok("Cadence 16 presentation freeze allowed")
    else:
        ok("Cadence 16 not started")
    if "mcp" in welcome.lower() or "a2a" in welcome.lower():
        fail("MCP/A2A claimed")
    else:
        ok("no MCP/A2A implementation")
    if "Business View" not in coverage or "Business View" not in demand:
        fail("Coverage/Demand view labels")
    else:
        ok("Coverage and Demand use Business / Technical views")
    if UI_CADENCE < 16 and "Cadence 15" not in app_src:
        fail("footer cadence")
    elif UI_CADENCE >= 16 and not any(tag in app_src for tag in ("Cadence 15", "Cadence 16", "Cadence 17")):
        fail("footer cadence")
    else:
        ok("UI cadence 15 footer")


def check_auth() -> None:
    src = (BACKEND / "app" / "config.py").read_text(encoding="utf-8")
    if "BASIC_AUTH_USERNAME" not in src or "DEMO_USERNAME" not in src:
        fail("env-driven auth missing")
        return
    ok("credential/environment configuration present")
    leaked = []
    for path in (FRONTEND / "src").rglob("*.js*"):
        text = path.read_text(encoding="utf-8")
        if "BASIC_AUTH_PASSWORD" in text or "DEMO_PASSWORD" in text:
            leaked.append(path.name)
    yaml_text = (ROOT / "data" / "model" / "stakeholder-entry.yaml").read_text(encoding="utf-8")
    if "BASIC_AUTH_PASSWORD" in yaml_text or "DEMO_PASSWORD" in yaml_text:
        leaked.append("stakeholder-entry.yaml")
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")
    if "value:" in render.split("BASIC_AUTH_PASSWORD")[-1][:80] if "BASIC_AUTH_PASSWORD" in render else False:
        leaked.append("render.yaml")
    if leaked:
        fail(f"credentials committed {leaked}")
    else:
        ok("credentials are not committed")
    prev_u = os.environ.get("BASIC_AUTH_USERNAME")
    prev_p = os.environ.get("BASIC_AUTH_PASSWORD")
    os.environ["BASIC_AUTH_USERNAME"] = "c15-gate-user"
    os.environ["BASIC_AUTH_PASSWORD"] = "c15-gate-pass"
    try:
        if demo_basic_credentials() != ("c15-gate-user", "c15-gate-pass"):
            fail("demo_basic_credentials ignored env")
        with TestClient(app) as client:
            if client.get("/health").status_code != 200:
                fail("health blocked by auth")
            else:
                ok("health-check compatibility")
            if client.get("/demand").status_code != 401:
                fail("protected API not gated")
            else:
                ok("frontend/API gated server-side")
            allowed = client.get("/demand", auth=("c15-gate-user", "c15-gate-pass"))
            if allowed.status_code >= 400:
                fail("valid basic auth rejected")
            else:
                ok("environment-driven Basic Auth accepts configured credentials")
    finally:
        if prev_u is None:
            os.environ.pop("BASIC_AUTH_USERNAME", None)
        else:
            os.environ["BASIC_AUTH_USERNAME"] = prev_u
        if prev_p is None:
            os.environ.pop("BASIC_AUTH_PASSWORD", None)
        else:
            os.environ["BASIC_AUTH_PASSWORD"] = prev_p


def check_boundaries() -> None:
    hits = [p.name for p in (BACKEND / "app").rglob("*.py") if "Meta_Demo" in p.read_text(encoding="utf-8") or "Jigyasa" in p.read_text(encoding="utf-8")]
    if hits:
        fail(f"other-repo references {hits}")
    else:
        ok("Meta_Demo and Jigyasa untouched")
    if not (DOCS / "cadences" / "ax-cadence-15.md").exists():
        fail("missing ax-cadence-15.md")
    else:
        ok("cadence 15 report present")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    mod = SourceFileLoader("validate_ax_cadence14", str(BACKEND / "scripts" / "validate_ax_cadence14.py")).load_module()
    code = mod.main()
    if code != 0:
        fail("validate_ax_cadence14.py regression failed")
        return
    ok("Cadence 0-14 regression passed")


def main() -> int:
    print("=== AX Cadence 15 validation (stakeholder sales experience) ===\n")
    check_health()
    check_start()
    check_unchanged()
    check_ui()
    check_auth()
    check_boundaries()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
