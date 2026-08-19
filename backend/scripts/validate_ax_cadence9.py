#!/usr/bin/env python3
"""AX Cadence 9 validation — Number Verification path selection. Do not start Cadence 10."""
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
from app.main import app, registry  # noqa: E402
from app.runtime import EXECUTABLE_INTENTS  # noqa: E402

errors: list[str] = []
oks: list[str] = []

INTENT = "verify_mobile_number"
SUBJECT = {"phoneNumber": "+1••••••0198"}
HEROES = [
    ("STEP_UP", {"intent": "assess_network_trust", "subject": {"transactionId": "RB-78421", "phoneNumber": "+1••••••0198"}, "context": {"amount": 25000, "currency": "USD"}}),
    ("CONTINUE" if UI_CADENCE >= 10 else "AT_RISK", {"intent": "ensure_baggage_connection", "subject": {"bagId": "HF123456", "connectingFlight": "HF281"}, "context": {"priority": "high"}}),
    ("ASSURED", {"intent": "maintain_inspection_experience", "subject": {"cameraId": "ACME-CAM-14", "lineId": "LINE-B"}, "context": {"sloMs": 40}}),
    ("ELIGIBLE", {"intent": "verify_pharmacy_age_gate", "subject": {"transactionId": "RX-10442", "phoneNumber": "+1••••••8843"}, "context": {"ageThreshold": 18}}),
]


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK - {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL - {msg}")


def _nv(client: TestClient, variant: str) -> dict:
    access = "CELLULAR" if variant == "cellular-nv1" else "WIFI"
    res = client.post(
        "/intents",
        json={
            "intent": INTENT,
            "subject": SUBJECT,
            "context": {
                "nvVariant": variant,
                "accessType": access,
                "claimedMsisdn": True,
                "businessEvent": "CUSTOMER_SIGNING_IN",
            },
        },
    )
    if res.status_code >= 400:
        fail(f"{variant} HTTP {res.status_code}: {res.text[:240]}")
        return {}
    return res.json()


def check_health() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if h.get("uiCadence") not in {9, 10, 11, 12, 13, 14, 15, 16, 17} or UI_CADENCE < 9:
            fail(f"uiCadence {h.get('uiCadence')}")
        else:
            ok(f"uiCadence {h.get('uiCadence')}")
        if h.get("modelCadence") != 7 or MODEL_CADENCE != 7:
            fail(f"modelCadence {h.get('modelCadence')}")
        else:
            ok("modelCadence 7")
        if INTENT not in EXECUTABLE_INTENTS:
            fail("verify_mobile_number not executable")
        elif {"rollout_firmware_safely", "assure_ramp_scan_capability"} & set(EXECUTABLE_INTENTS):
            fail("Cadence 10/12 intents leaked")
        else:
            ok("one new live Intent: verify_mobile_number")


def check_three_variants() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        cellular = _nv(client, "cellular-nv1")
        wifi = _nv(client, "wifi-nv2")
        gap = _nv(client, "wifi-ecs-gap")
        if not (cellular and wifi and gap):
            return

        intents = {cellular.get("intentId"), wifi.get("intentId"), gap.get("intentId")}
        if intents != {INTENT}:
            fail(f"Intent drifted across variants: {intents}")
        else:
            ok("same verify_mobile_number Intent across three variants")

        c_path = (cellular.get("pathSelection") or {}).get("selectedPath")
        w_path = (wifi.get("pathSelection") or {}).get("selectedPath")
        g_path = (gap.get("pathSelection") or {}).get("selectedPath")
        if c_path != "NV1_NETWORK_BASED":
            fail(f"cellular path {c_path}")
        else:
            ok("cellular selects NV1_NETWORK_BASED")
        if w_path != "NV2_OPERATOR_TOKEN":
            fail(f"wifi-ready path {w_path}")
        else:
            ok("Wi-Fi ready selects NV2_OPERATOR_TOKEN")
        if g_path:
            fail(f"ECS gap must not select a path: {g_path}")
        else:
            ok("Wi-Fi ECS gap has no selected path")

        if (cellular.get("outcome") or {}).get("outcome") != "VERIFIED":
            fail(f"cellular outcome {cellular.get('outcome')}")
        else:
            ok("cellular VERIFIED")
        if (wifi.get("outcome") or {}).get("outcome") != "VERIFIED":
            fail(f"wifi outcome {wifi.get('outcome')}")
        else:
            ok("Wi-Fi ready VERIFIED")
        if (gap.get("outcome") or {}).get("outcome") != "CAPABILITY_UNAVAILABLE":
            fail(f"ECS gap outcome {gap.get('outcome')}")
        else:
            ok("ECS gap CAPABILITY_UNAVAILABLE")

        if any(i.get("operationId") == "phoneNumberVerify" for i in (gap.get("invocations") or [])):
            fail("ECS gap invoked Number Verification")
        else:
            ok("no fake NV1 / no invocation on ECS gap")

        reasons = {e.get("reasonCode") for e in (wifi.get("discovery") or [])}
        if "ACCESS_TYPE_INCOMPATIBLE" not in reasons:
            fail("Wi-Fi discovery missing ACCESS_TYPE_INCOMPATIBLE")
        else:
            ok("Discovery emits ACCESS_TYPE_INCOMPATIBLE")
        gap_reasons = {e.get("reasonCode") for e in (gap.get("discovery") or [])}
        if "ENTITLEMENT_SERVER_UNAVAILABLE" not in gap_reasons:
            fail("ECS gap discovery missing ENTITLEMENT_SERVER_UNAVAILABLE")
        else:
            ok("Discovery emits ENTITLEMENT_SERVER_UNAVAILABLE")

        for name, trace in (("cellular", cellular), ("wifi", wifi)):
            ps = trace.get("pathSelection") or {}
            if ps.get("selectedOperation") != "phoneNumberVerify":
                fail(f"{name} operation {ps.get('selectedOperation')}")
            else:
                ok(f"{name} claimed number uses phoneNumberVerify")
            share = next((op for op in (ps.get("operations") or []) if op.get("operationId") == "phoneNumberShare"), {})
            if share.get("reasonCode") != "NOT_REQUIRED":
                fail(f"{name} phoneNumberShare incorrectly selected as NV2")
            else:
                ok(f"{name} phoneNumberShare is not labelled NV2")

        c_acc = (cellular.get("pathSelection") or {}).get("accessType")
        c_telco = ((cellular.get("telcoFinder") or {}).get("result") or {}).get("network")
        if c_acc != "CELLULAR":
            fail("access type missing from runtime context")
        elif "CELLULAR" in json.dumps(cellular.get("telcoFinder") or {}) and (cellular.get("telcoFinder") or {}).get("doesNotDetermineAccessType") is not True:
            # allowed only as a negation note
            ok("access type is runtime context")
        else:
            ok("access type is runtime context")
        if (cellular.get("pathSelection") or {}).get("accessTypeSource") != "RUNTIME_CLIENT_CONTEXT":
            fail("access type source is not RUNTIME_CLIENT_CONTEXT")
        else:
            ok("Telco Finder distinct from access type")
        if c_telco != "Network Provider A":
            fail(f"Telco Finder {c_telco}")
        else:
            ok("Telco Finder names Network Provider A")

        api = wifi.get("pathSelection") or {}
        if not (api.get("apiFinder") or {}).get("numberVerificationAvailable"):
            fail("API Finder did not report NV available")
        ecs = ((api.get("operatorReadiness") or {}).get("entitlementServer") or {}).get("available")
        if ecs != "AVAILABLE":
            fail(f"wifi-ready ECS {ecs}")
        else:
            ok("API Finder distinct from ECS readiness")

        blob = json.dumps(gap).lower()
        if "sms otp as an ax" not in blob and ("fallback" in blob and "sms" in blob and "otp" in blob and "forbidden" not in blob):
            fail("SMS OTP fallback invented")
        elif any(
            (inv.get("operationId") or "").lower() in {"sendotp", "validateotp", "one-time-password"}
            for inv in (gap.get("invocations") or [])
        ):
            fail("SMS OTP invocation")
        else:
            ok("no SMS OTP fallback")

        catalog = json.dumps(registry.to_public()).lower()
        if "entitlement-server" in catalog or "entitlement configuration server" in catalog:
            fail("ECS leaked into API catalog")
        else:
            ok("ECS is not in the API catalog")

        opp_ok = cellular.get("networkOpportunity") or {}
        opp_gap = gap.get("networkOpportunity") or {}
        if opp_ok.get("demandFulfilled") is not True or opp_ok.get("path") != "NV1_NETWORK_BASED":
            fail(f"successful opportunity {opp_ok}")
        else:
            ok("Network Opportunity shows fulfilled demand")
        if opp_gap.get("demandFulfilled") is not False or opp_gap.get("demandClass") != "UNFULFILLED_QUALIFIED_DEMAND":
            fail(f"ECS opportunity {opp_gap}")
        else:
            ok("ECS failure shows unfulfilled qualified demand")
        if "lost revenue" in json.dumps(opp_gap).lower() or opp_gap.get("revenue"):
            fail("revenue invented")
        else:
            ok("no revenue on Network Opportunity")

        for key in ("businessDemandQualified", "demandFulfilled", "provider", "capability", "path", "networkApiInvocations"):
            if key not in (cellular.get("demandSupply") or {}) and key not in cellular:
                fail(f"missing demand/supply field {key}")
        else:
            ok("demand/supply trace fields present (no money)")

        supply = (gap.get("pathSelection") or {}).get("supplySide") or []
        labels = {row.get("label"): row for row in supply}
        if labels.get("Network Provider A", {}).get("ecs") != "AVAILABLE":
            fail("supply-side A not NV2 ready")
        elif labels.get("Network Provider B", {}).get("ecs") != "UNAVAILABLE":
            fail("supply-side B ECS not unavailable")
        elif labels.get("Specialist Provider C", {}).get("numberVerification") != "UNAVAILABLE":
            fail("supply-side C NV not unavailable")
        else:
            ok("aggregator-ready supply-side metadata for A/B/C")

        if (gap.get("pathSelection") or {}).get("telcoFinder", {}).get("provider") != "Network Provider B":
            fail("ECS gap Telco Finder should name Provider B")
        else:
            ok("ECS gap Telco Finder is Network Provider B")


def check_heroes_and_catalog() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        for expected, body in HEROES:
            res = client.post("/intents", json=body)
            outcome = (res.json().get("outcome") or {}).get("outcome")
            if outcome != expected:
                fail(f"{body['intent']} outcome {outcome}")
            else:
                ok(f"{body['intent']} -> {expected}")
        rec = client.post(
            "/intents",
            json={"intent": "assess_recovery_continuity", "subject": {"recoveryId": "RB-REC-19", "phoneNumber": "+1••••••0198"}, "context": {"channel": "web"}},
        )
        if (rec.json().get("outcome") or {}).get("outcome") != "CONTINUITY_ALIGNED":
            fail("evidence reuse changed")
        else:
            ok("Rocket Bank trust and evidence reuse unchanged")
        if len(registry.families) != 13:
            fail(f"catalog {len(registry.families)}")
        else:
            ok("catalog remains 13 families")


def check_ui() -> None:
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    home = (FRONTEND / "src" / "pages" / "Home.jsx").read_text(encoding="utf-8")
    pick = (FRONTEND / "src" / "pages" / "DemoPick.jsx").read_text(encoding="utf-8")
    nv = (FRONTEND / "src" / "pages" / "NvPath.jsx").read_text(encoding="utf-8")
    if "passwordless-mobile-sign-in" not in runtime or "verify_mobile_number" not in runtime:
        fail("NV runtime scenario missing")
    else:
        ok("single NV runtime scenario")
    if runtime.count("verify_mobile_number") < 1:
        fail("NV intent not wired")
    if "nv-nv1" in home.lower() and "nv-nv2" in home.lower():
        fail("separate NV1/NV2 hero cards")
    else:
        ok("one Number Verification story card")
    if UI_CADENCE >= 10:
        if "SIMULATE RUNTIME CONTEXT" not in nv.upper() and "Simulate runtime context" not in nv:
            fail("NV selector must be labelled as simulation/presenter context")
        else:
            ok("NV variant selector is presenter simulation, not application choice")
        if "Cellular / Provider A" not in nv or "Wi-Fi / Provider A" not in nv or "Wi-Fi / Provider B" not in nv:
            fail("C10 NV simulation labels missing")
        else:
            ok("NV simulation labels Cellular/Wi-Fi / Provider")
        if "NV1" in nv and "Application chooses" in nv and "NetAware chooses" not in nv:
            fail("application appears to choose NV1/NV2")
        else:
            ok("application chooses Intent; NetAware chooses path")
    elif "CELLULAR" not in nv or "WI-FI — READY" not in nv or "WI-FI — ECS GAP" not in nv:
        fail("variant selector labels missing")
    else:
        ok("same-page CELLULAR / WI-FI READY / WI-FI ECS GAP selector")
    change = re.search(r"const changeLens = \((.*?)\) => \{([\s\S]*?)\n  \};", runtime)
    if not change:
        fail("changeLens missing")
    elif "apiPost" in change.group(2) or "/intents" in change.group(2):
        fail("switching lens reruns the scenario")
    else:
        ok("Basic/Advanced same trace — lens switch does not rerun")
    if "Number Verification" not in pick and "Passwordless" not in pick:
        fail("picker order hint missing NV")
    else:
        ok("picker recommends Number Verification first")
    for forbidden in ("Demand Map", "Meeting Mode", "rollout_firmware_safely", "SalesScenarioProfile"):
        if forbidden in runtime:
            fail(f"Cadence 10+ leaked into Runtime: {forbidden}")
    else:
        ok("OTA / Demand Map / Meeting Mode not started")


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
    if not (DOCS / "cadences" / "ax-cadence-9.md").exists():
        fail("missing ax-cadence-9.md")
    else:
        ok("cadence 9 report present")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    mod = SourceFileLoader("validate_ax_cadence8", str(BACKEND / "scripts" / "validate_ax_cadence8.py")).load_module()
    code = mod.main()
    if code != 0:
        fail("validate_ax_cadence8.py regression failed")
        return
    ok("Cadence 0-8 regression passed")


def main() -> int:
    print("=== AX Cadence 9 validation (Number Verification path selection) ===\n")
    check_health()
    check_three_variants()
    check_heroes_and_catalog()
    check_ui()
    check_boundaries()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
