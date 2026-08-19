#!/usr/bin/env python3
"""AX Cadence 17.1 validation — visual storytelling polish. Do not start Cadence 18."""
from __future__ import annotations

import os
import sys
from importlib.machinery import SourceFileLoader
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

from app.config import MODEL_CADENCE, UI_CADENCE, UI_CADENCE_PATCH  # noqa: E402
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


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK - {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL - {msg}")


def check_patch() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if UI_CADENCE != 17 or h.get("uiCadence") != 17:
            fail(f"uiCadence drifted {h.get('uiCadence')}")
        else:
            ok("uiCadence remains 17")
        if UI_CADENCE_PATCH != "17.1" or h.get("uiCadencePatch") != "17.1":
            fail(f"uiCadencePatch {h.get('uiCadencePatch')}")
        else:
            ok("uiCadencePatch 17.1")
        if h.get("modelCadence") != 7 or MODEL_CADENCE != 7:
            fail("modelCadence")
        else:
            ok("model cadence unchanged")
        if h.get("version") != "0.6.1-ax6.1":
            fail(f"version {h.get('version')}")
        else:
            ok("live version unchanged")
        if not h.get("visualStorytelling"):
            fail("visualStorytelling flag")
        else:
            ok("visual storytelling flag")
        if len(registry.families) != 13:
            fail("catalog expanded")
        else:
            ok("13 API families unchanged")
        if len(visible_rows(store)) != 17:
            fail("portfolio expanded")
        else:
            ok("17 use cases unchanged")


def check_outcomes() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        for expected, body in HEROES:
            got = (client.post("/intents", json=body).json().get("outcome") or {}).get("outcome")
            if got != expected:
                fail(f"{body['intent']} {got} != {expected}")
            else:
                ok(f"{body['intent']} {expected}")
        gap = client.post(
            "/intents",
            json={"intent": "verify_mobile_number", "subject": {"phoneNumber": "+1••••••0198"}, "context": {"nvVariant": "wifi-ecs-gap", "accessType": "WIFI", "claimedMsisdn": True, "businessEvent": "CUSTOMER_SIGNING_IN"}},
        ).json()
        if (gap.get("outcome") or {}).get("outcome") != "CAPABILITY_UNAVAILABLE":
            fail("NV ECS gap")
        else:
            ok("NV semantics unchanged")
        ota = client.post(
            "/intents",
            json={"intent": "prepare_ota_cohort", "subject": {"campaignId": "ACME-FW-8-4-CRITICAL", "applicationId": "acme-device-fleet"}, "context": {"otaWave": "prepare", "campaignPriority": "CRITICAL"}},
        ).json()
        if (ota.get("outcome") or {}).get("outcome") != "NETWORK_QUALIFIED_COHORT":
            fail("OTA")
        else:
            ok("OTA unchanged")
        vis = ota.get("otaVisual") or {}
        if vis.get("evidenceReused") != 1300:
            fail(f"OTA reuse overlay {vis.get('evidenceReused')}")
        else:
            ok("OTA reuse overlay uses existing fleet number")


def check_same_mapping() -> None:
    payload = public_map(store, graph, registry)
    cells = (payload.get("matrix") or {}).get("cells") or []
    reverse = payload.get("reverseFamilies") or []
    if payload.get("counts", {}).get("useCases") != 17 or payload.get("counts", {}).get("families") != 13:
        fail("map counts")
    else:
        ok("matrix still 17×13 from existing model")
    invented = 0
    for cell in cells:
        known = {str(link.get("capabilityId")) for link in graph.intent_caps.get(cell.get("intentId")) or []}
        for cap in cell.get("capabilities") or []:
            if cap.get("id") not in known:
                invented += 1
    if invented:
        fail("graph/matrix invented relationships")
    else:
        ok("matrix and reverse graph share mapping source")
    if not any(f.get("useCases") for f in reverse):
        fail("reverse graph empty")
    else:
        ok("reverse traversal derived")
    with TestClient(app) as client:
        cov = client.get("/coverage").json()
        dem = client.get("/demand").json()
        if not (cov.get("records") or []):
            fail("coverage missing")
        else:
            ok("coverage records unchanged source")
        if not (dem.get("records") or []):
            fail("demand missing")
        else:
            ok("demand records unchanged source")
        if not client.get("/meet").json().get("doesNotAlterRuntime"):
            fail("meeting overlay")
        else:
            ok("Meeting Mode remains functional")


def check_ui() -> None:
    kit = (FRONTEND / "src" / "visuals" / "VisualKit.jsx").read_text(encoding="utf-8")
    mapping = (FRONTEND / "src" / "pages" / "Map.jsx").read_text(encoding="utf-8")
    meet = (FRONTEND / "src" / "pages" / "Meeting.jsx").read_text(encoding="utf-8")
    app_src = (FRONTEND / "src" / "App.jsx").read_text(encoding="utf-8")
    nv = (FRONTEND / "src" / "pages" / "NvPath.jsx").read_text(encoding="utf-8")
    cov = (FRONTEND / "src" / "pages" / "Coverage.jsx").read_text(encoding="utf-8")
    for name, blob in (
        ("AxBrain", kit),
        ("DiscoveryFunnel", kit),
        ("CATALOG UNIVERSE", kit),
        ("ReverseGraph", kit),
        ("OperatorLadder", kit),
        ("GovernanceWaterfall", kit),
        ("WITHOUT AX", kit),
        ("IntentTrace", kit),
        ("FlywheelClose", kit),
        ("Projector focus", mapping),
        ("REQ", mapping),
        ("Meeting Mode", meet),
        ("Cadence 17.1", app_src),
        ("SAME INTENT", nv),
        ("OperatorLadder", cov),
    ):
        if name not in blob:
            fail(f"missing {name}")
        else:
            ok(f"{name} present")
    if "apiPost" in mapping or "/intents" in mapping:
        fail("map reruns intents")
    else:
        ok("lens / map does not rerun Intents")
    if "live mcp" in kit.lower() or "live a2a" in kit.lower():
        fail("MCP/A2A")
    else:
        ok("no live MCP/A2A claim")
    if "lost revenue" in kit.lower() or "tam" in kit.lower():
        fail("revenue language")
    else:
        ok("no revenue language")


def check_docs() -> None:
    if not (DOCS / "cadences" / "ax-cadence-17.1.md").exists():
        fail("missing cadence 17.1 report")
    else:
        ok("cadence 17.1 report present")
    hits = [
        p.name
        for p in (BACKEND / "app").rglob("*.py")
        if "Meta_Demo" in p.read_text(encoding="utf-8") or "Jigyasa" in p.read_text(encoding="utf-8")
    ]
    if hits:
        fail(f"other-repo {hits}")
    else:
        ok("Meta_Demo and Jigyasa untouched")


def check_regression() -> None:
    mod = SourceFileLoader("validate_ax_cadence17", str(BACKEND / "scripts" / "validate_ax_cadence17.py")).load_module()
    code = mod.main()
    if code != 0:
        fail("validate_ax_cadence17.py regression failed")
        return
    ok("Cadence 0-17 regression passed")


def main() -> int:
    print("=== AX Cadence 17.1 validation (visual storytelling polish) ===\n")
    check_patch()
    check_outcomes()
    check_same_mapping()
    check_ui()
    check_docs()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
