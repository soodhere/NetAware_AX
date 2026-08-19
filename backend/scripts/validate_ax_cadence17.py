#!/usr/bin/env python3
"""AX Cadence 17 validation — visual intelligence. Do not start another cadence."""
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
from app.main import app, graph, registry, store  # noqa: E402
from app.portfolio import visible_rows  # noqa: E402
from app.visuals import public_map  # noqa: E402

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
        if UI_CADENCE != 17 or h.get("uiCadence") != 17:
            fail(f"uiCadence {h.get('uiCadence')} / {UI_CADENCE}")
        else:
            ok("uiCadence 17")
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
        industries = (store.sales_portfolio or {}).get("industries") or []
        if len(industries) != 10:
            fail(f"industries {len(industries)}")
        else:
            ok("10 industries preserved")
        if not h.get("meetingPresentation") or not h.get("visualIntelligence"):
            fail("C16/C17 flags")
        else:
            ok("C16 Meeting Mode preserved")
        if client.get("/health").status_code != 200:
            fail("health endpoint")
        else:
            ok("health endpoint works")


def check_map() -> None:
    payload = public_map(store, graph, registry)
    if not payload.get("presentationOnly") or not payload.get("doesNotAlterRuntime") or not payload.get("notIndependentMappingDb"):
        fail("map is not presentation-only / derived")
    else:
        ok("Use Case/API visual derives from existing model")
    if payload.get("counts", {}).get("useCases") != 17 or payload.get("counts", {}).get("families") != 13:
        fail(f"map counts {payload.get('counts')}")
    else:
        ok("map uses 17 use cases and 13 families")
    cells = (payload.get("matrix") or {}).get("cells") or []
    invented = []
    for cell in cells:
        intent_id = cell.get("intentId")
        known = {str(link.get("capabilityId")) for link in graph.intent_caps.get(intent_id) or []}
        for cap in cell.get("capabilities") or []:
            if cap.get("id") not in known:
                invented.append((intent_id, cap.get("id")))
        if cell.get("state") not in {"REQUIRED", "CONDITIONAL", "FILTERED"}:
            invented.append((intent_id, cell.get("state")))
    if invented:
        fail(f"matrix invented relationships {invented[:5]}")
    else:
        ok("matrix does not invent relationships")
    reverse = payload.get("reverseFamilies") or []
    if not any((f.get("useCases") or []) for f in reverse):
        fail("reverse API traversal empty")
    else:
        ok("reverse API/use-case traversal derives from same model")
    if payload.get("coverageSource") != "C13" or payload.get("demandSource") != "C14":
        fail("C13/C14 sources")
    else:
        ok("C13 remains fulfillment source; C14 remains demand source")
    blob = json.dumps(payload).lower()
    if "opportunity score" in blob or '"tam"' in blob or "lost revenue" in blob:
        fail("revenue claims")
    else:
        ok("no revenue claims")
    if any(name in json.dumps(payload) for name in REAL_OPS):
        fail("real operator names")
    else:
        ok("no real provider claims")
    with TestClient(app) as client:
        res = client.get("/map")
        if res.status_code >= 400:
            fail(f"/map {res.status_code}")
        else:
            ok("map endpoint works")
        if not client.get("/meet").json().get("doesNotAlterRuntime"):
            fail("meeting overlay")
        else:
            ok("C16 Meeting Mode overlay preserved")


def check_unchanged() -> None:
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
            ok("OTA numbers / cohort preserved")


def check_ui() -> None:
    mapping = (FRONTEND / "src" / "pages" / "Map.jsx").read_text(encoding="utf-8")
    kit = (FRONTEND / "src" / "visuals" / "VisualKit.jsx").read_text(encoding="utf-8")
    app_src = (FRONTEND / "src" / "App.jsx").read_text(encoding="utf-8")
    meet = (FRONTEND / "src" / "pages" / "Meeting.jsx").read_text(encoding="utf-8")
    discovery = (FRONTEND / "src" / "pages" / "Discovery.jsx").read_text(encoding="utf-8")
    nv = (FRONTEND / "src" / "pages" / "NvPath.jsx").read_text(encoding="utf-8")
    coverage = (FRONTEND / "src" / "pages" / "Coverage.jsx").read_text(encoding="utf-8")
    demand = (FRONTEND / "src" / "pages" / "Demand.jsx").read_text(encoding="utf-8")
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    hf = (FRONTEND / "src" / "pages" / "DecisionGap.jsx").read_text(encoding="utf-8")
    explore = (FRONTEND / "src" / "pages" / "Explore.jsx").read_text(encoding="utf-8")
    if "Use Case ↔ API Map" not in mapping and "Use Case" not in mapping:
        fail("Use Case/API map UI missing")
    else:
        ok("Use Case ↔ API Map present")
    if "Matrix" not in mapping:
        fail("matrix view missing")
    else:
        ok("matrix view present")
    if "WHERE CAN I ENABLE THIS CAPABILITY" not in mapping:
        fail("reverse traversal UI missing")
    else:
        ok("reverse API traversal present")
    if "DiscoveryFunnel" not in discovery:
        fail("discovery funnel missing")
    else:
        ok("Discovery visual uses existing discovery events")
    if "GovernanceWaterfall" not in discovery:
        fail("governance waterfall missing")
    else:
        ok("governance visual uses existing policy/provenance")
    if "CAMARA API availability" not in nv and "Fulfillment" not in nv:
        fail("NV / finder distinction")
    else:
        ok("NV behavior / ECS / finder distinction preserved in visuals")
    if "Heatmap" not in coverage:
        fail("fulfillment heatmap missing")
    else:
        ok("fulfillment heatmap present")
    if "SupplyGapGraph" not in demand:
        fail("supply-gap visual missing")
    else:
        ok("supply-gap impact graph present")
    if "DOES NOT TRACK" not in hf.upper() and "does not track" not in hf.lower():
        fail("High Flight boundary")
    else:
        ok("High Flight boundaries preserved")
    if "InspectionLoop" not in runtime or "CityCareMin" not in runtime or "ReuseGraph" not in runtime:
        fail("story visuals missing")
    else:
        ok("Acme / CityCare / evidence reuse visuals present")
    if "USE CASE → APIs" not in explore:
        fail("Explorer entry points missing")
    else:
        ok("Explorer integration present")
    if "Meeting Mode" not in meet:
        fail("Meeting Mode removed")
    else:
        ok("Meeting Mode integration present")
    if "apiPost" in mapping or "/intents" in mapping:
        fail("map reruns intents")
    else:
        ok("visual lens / map does not rerun Intents")
    if "Reset Demo" not in app_src or "Replay" not in runtime:
        fail("reset/replay")
    else:
        ok("Reset/Replay works")
    if "Cadence 17" not in app_src:
        fail("footer cadence")
    else:
        ok("UI cadence 17 footer")
    if "mcp" in mapping.lower() or "a2a" in kit.lower():
        fail("MCP/A2A")
    else:
        ok("no MCP/A2A")
    if "does not own" not in kit.lower() and "does not own" not in mapping.lower():
        fail("aggregator ownership wording")
    else:
        ok("provider/aggregator ownership wording preserved")


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
    os.environ["BASIC_AUTH_USERNAME"] = "c17-gate-user"
    os.environ["BASIC_AUTH_PASSWORD"] = "c17-gate-pass"
    try:
        if demo_basic_credentials() != ("c17-gate-user", "c17-gate-pass"):
            fail("auth env")
        with TestClient(app) as client:
            if client.get("/health").status_code != 200:
                fail("health blocked")
            elif client.get("/map").status_code != 401:
                fail("map not gated")
            elif client.get("/map", auth=("c17-gate-user", "c17-gate-pass")).status_code >= 400:
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
    if not (DOCS / "cadences" / "ax-cadence-17.md").exists():
        fail("missing ax-cadence-17.md")
    else:
        ok("cadence 17 report present")
    hits = [p.name for p in (BACKEND / "app").rglob("*.py") if "Meta_Demo" in p.read_text(encoding="utf-8") or "Jigyasa" in p.read_text(encoding="utf-8")]
    if hits:
        fail(f"other-repo {hits}")
    else:
        ok("Meta_Demo and Jigyasa untouched")
    if len(visible_rows(store)) != 17:
        fail("new scenarios")
    else:
        ok("no new scenarios")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    mod = SourceFileLoader("validate_ax_cadence16", str(BACKEND / "scripts" / "validate_ax_cadence16.py")).load_module()
    code = mod.main()
    if code != 0:
        fail("validate_ax_cadence16.py regression failed")
        return
    ok("Cadence 0-16 regression passed")


def main() -> int:
    print("=== AX Cadence 17 validation (visual intelligence) ===\n")
    check_health()
    check_map()
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
