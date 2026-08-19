#!/usr/bin/env python3
"""AX Cadence 11 validation — device fleet / OTA readiness. Do not start Cadence 12."""
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
from app.main import app, registry, store  # noqa: E402
from app.runtime import EXECUTABLE_INTENTS  # noqa: E402

errors: list[str] = []
oks: list[str] = []

INTENT = "prepare_ota_cohort"
ALIAS = "rollout_firmware_safely"
FORBIDDEN_NET = {"createSession", "verifyLocation", "retrieveLocation", "checkNetworkQuality", "phoneNumberVerify", "checkSimSwap", "checkDeviceSwap"}


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK - {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL - {msg}")


def _post(client: TestClient, wave: str) -> dict:
    res = client.post(
        "/intents",
        json={
            "intent": INTENT,
            "subject": {"campaignId": "ACME-FW-8-4-CRITICAL", "applicationId": "acme-device-fleet"},
            "context": {"otaWave": wave, "campaignPriority": "CRITICAL"},
        },
    )
    if res.status_code >= 400:
        fail(f"{wave} HTTP {res.status_code}: {res.text[:280]}")
        return {}
    return res.json()


def check_health() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if UI_CADENCE < 11 or h.get("uiCadence") not in {11, 12, 13, 14, 15, 16, 17}:
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
        if INTENT not in EXECUTABLE_INTENTS:
            fail("prepare_ota_cohort not executable")
        elif ALIAS in EXECUTABLE_INTENTS or "assure_ramp_scan_capability" in EXECUTABLE_INTENTS:
            fail("documentation aliases leaked into EXECUTABLE_INTENTS")
        else:
            ok("prepare_ota_cohort live; working aliases not executable")
        if len(registry.families) != 13:
            fail(f"catalog {len(registry.families)}")
        else:
            ok("catalog remains 13 families")


def check_profile() -> None:
    profile = store.intent_profile_by_id.get(INTENT) or {}
    if not profile:
        fail("missing prepare_ota_cohort Intent Profile")
        return
    if profile.get("complexity") != "ADVANCED_AGENTIC":
        fail(f"complexity {profile.get('complexity')}")
    else:
        ok("scenario is ADVANCED_AGENTIC")
    gap = profile.get("decisionGap") or {}
    if not (gap.get("alreadyHave") and gap.get("decide") and gap.get("gap") and gap.get("networkAdds")):
        fail("Decision Gap missing")
    else:
        ok("Decision Gap exists")
    if profile.get("networkContributionTier") not in {"A", "B"}:
        fail(f"tier {profile.get('networkContributionTier')}")
    else:
        ok(f"networkContributionTier {profile.get('networkContributionTier')}")
    if INTENT not in LIVE_PROFILE_INTENTS:
        fail("profile not in LIVE_PROFILE_INTENTS")
    ota_doc = store.ota_device_fleet or {}
    if not ota_doc.get("networkDoesNotFlashFirmware"):
        fail("OTA model must state network does not flash firmware")
    else:
        ok("enterprise OTA owns firmware; NetAware never installs")


def check_ota_run() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        prepare = _post(client, "prepare")
        reassess = _post(client, "reassess")
        if not prepare or not reassess:
            return
        if prepare.get("intentId") != INTENT or reassess.get("intentId") != INTENT:
            fail("Intent drifted across waves")
        else:
            ok("same prepare_ota_cohort Intent across prepare / reassess")
        if (prepare.get("outcome") or {}).get("outcome") != "NETWORK_QUALIFIED_COHORT":
            fail(f"prepare outcome {(prepare.get('outcome') or {}).get('outcome')}")
        else:
            ok("network-ready cohort produced")
        if (reassess.get("outcome") or {}).get("outcome") != "COHORT_EXPANDED":
            fail(f"reassess outcome {(reassess.get('outcome') or {}).get('outcome')}")
        else:
            ok("second-step reassessment exists")
        vis = prepare.get("otaVisual") or {}
        vis2 = reassess.get("otaVisual") or {}
        cohorts = vis.get("cohorts") or {}
        cohorts2 = vis2.get("cohorts") or {}
        funnel = {row["id"]: row["count"] for row in vis.get("funnel") or []}
        if funnel.get("campaign") != 10000 or funnel.get("eligible") != 8400:
            fail(f"funnel {funnel}")
        else:
            ok("fleet size 10,000 / enterprise eligible 8,400")
        if cohorts.get("rollOutNow") + sum(r["count"] for r in vis.get("deferredReasons") or []) != 8400:
            fail("cohort numbers do not reconcile")
        else:
            ok("fleet funnel numbers reconcile")
        if cohorts.get("rollOutNow") != 5900 or cohorts.get("deferUnreachable") != 1200:
            fail(f"prepare cohorts {cohorts}")
        else:
            ok("deferred cohort produced with unreachable / roaming / API gap")
        if not vis.get("simulatedFleet") or vis.get("didNotInstallFirmware") is not True:
            fail("simulated / no-firmware labels missing")
        else:
            ok("all fleet numbers labelled simulated; firmware not installed")
        if (vis2.get("movement") or {}).get("added", 0) <= 0 or cohorts2.get("rollOutNow") <= cohorts.get("rollOutNow"):
            fail("reassessment did not expand cohort")
        else:
            ok("some deferred devices become ready and expand the cohort")
        telco = prepare.get("telcoFinder") or {}
        api = prepare.get("apiFinder") or {}
        if not telco.get("separateFromApiFinder") or not (telco.get("result") or {}).get("groups"):
            fail("Telco Finder provider grouping missing")
        else:
            ok("Telco Finder provider grouping")
        if not api.get("separateFromTelcoFinder") or not api.get("providerGroups"):
            fail("API Finder not separate")
        else:
            ok("API Finder separate from Telco Finder")
        invoked = {i.get("operationId") for i in prepare.get("invocations") or [] if i.get("apiKind") == "NETWORK"}
        if "getReachabilityStatus" not in invoked:
            fail("Reachability not primary evidence")
        else:
            ok("Reachability is primary network evidence")
        if "getRoamingStatus" not in invoked:
            fail("Roaming not invoked where available")
        else:
            ok("Roaming interpreted through configured policy")
        if invoked & FORBIDDEN_NET:
            fail(f"forced extra Network APIs {invoked & FORBIDDEN_NET}")
        else:
            ok("no QoD, Location, NV, SIM/Device Swap, or experimental Insights in OTA")
        if len(prepare.get("invocations") or []) > 40:
            fail(f"too many invocation rows {len(prepare.get('invocations') or [])}")
        else:
            ok("representative samples, not 10,000 invocation rows")
        blob = json.dumps(prepare).lower() + json.dumps(reassess).lower()
        if "roaming is not automatically bad" not in blob and "not automatically bad" not in blob:
            fail("missing roaming-is-not-automatically-bad")
        else:
            ok("no assumption roaming = bad")
        enterprise_ops = [i for i in prepare.get("invocations") or [] if i.get("operationId") == "addDevicesToCampaign"]
        if not enterprise_ops or enterprise_ops[0].get("apiKind") != "ENTERPRISE":
            fail("enterprise OTA action missing or mislabelled")
        elif "SIMULATED ENTERPRISE API" not in (enterprise_ops[0].get("source") or ""):
            fail("enterprise OTA action not labelled simulated enterprise API")
        else:
            ok("enterprise OTA action labelled simulated enterprise API")
        auto = prepare.get("autonomy") or {}
        if "install_firmware" not in (auto.get("notAuthorized") or []) or "submit_cohort_to_ota" not in (auto.get("actWithApproval") or []):
            fail(f"autonomy {auto}")
        else:
            ok("autonomy boundaries correct")
        demand = prepare.get("demandSupply") or {}
        if demand.get("unreachableIsNotUnfulfilledDemand") is not True:
            fail("unreachable confused with API availability failure")
        elif demand.get("unfulfilledCapability") != "roaming_status":
            fail("unfulfilled qualified demand not tied to roaming capability gap")
        else:
            ok("API unreachable result not confused with unfulfilled qualified demand")
        vol = (vis.get("volume") or {})
        if vol.get("label") != "SIMULATED DEMO VOLUME":
            fail("volume not labelled simulated")
        elif "revenue" in json.dumps(vol).lower() and "no revenue" not in json.dumps(vol).lower():
            fail("fake revenue")
        else:
            ok("volume is explicitly simulated; no fake revenue")
        routes = {row.get("route") for row in vis.get("providers") or []}
        if not {"DIRECT", "AGGREGATED"} <= routes:
            fail(f"provider routes {routes}")
        else:
            ok("provider routes use existing DIRECT / AGGREGATED model")
        if vis.get("footer") and "DID NOT INSTALL FIRMWARE" not in vis.get("footer"):
            fail("firmware disclaimer missing")
        else:
            ok("NetAware never performs firmware installation")


def check_regression_heroes() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        cases = [
            ("ASSURED", {"intent": "maintain_inspection_experience", "subject": {"cameraId": "ACME-CAM-14", "lineId": "LINE-B"}, "context": {"sloMs": 40}}),
            ("VERIFIED", {"intent": "verify_mobile_number", "subject": {"phoneNumber": "+1••••••0198"}, "context": {"nvVariant": "cellular-nv1", "accessType": "CELLULAR", "claimedMsisdn": True, "businessEvent": "CUSTOMER_SIGNING_IN"}}),
            ("STEP_UP", {"intent": "assess_network_trust", "subject": {"transactionId": "RB-78421", "phoneNumber": "+1••••••0198"}, "context": {"amount": 25000, "currency": "USD"}}),
            ("CONTINUE", {"intent": "ensure_baggage_connection", "subject": {"bagId": "HF123456", "connectingFlight": "HF281"}, "context": {"priority": "high"}}),
            ("ELIGIBLE", {"intent": "verify_pharmacy_age_gate", "subject": {"transactionId": "RX-10442", "phoneNumber": "+1••••••8843"}, "context": {"ageThreshold": 18}}),
        ]
        for expected, body in cases:
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
        rec_out = (rec.json().get("outcome") or {}).get("outcome")
        if rec_out != "CONTINUITY_ALIGNED":
            fail(f"recovery {rec_out}")
        else:
            ok("Rocket Bank recovery CONTINUITY_ALIGNED")
        bad = client.post("/intents", json={"intent": ALIAS, "subject": {}, "context": {}})
        if bad.status_code < 400:
            fail("rollout_firmware_safely must not execute")
        else:
            ok("rollout_firmware_safely remains non-executable")


def check_ui() -> None:
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    ota = (FRONTEND / "src" / "pages" / "OtaFleet.jsx").read_text(encoding="utf-8")
    if "OtaFleetVisual" not in runtime or "prepare_ota_cohort" not in runtime:
        fail("OTA runtime visual missing")
    else:
        ok("Business View fleet funnel / cohort tiles present")
    if "OtaVariantBar" not in runtime or "reassess" not in ota:
        fail("prepare/reassess selector missing")
    else:
        ok("two-step prepare / reassess selector")
    if ALIAS in runtime:
        fail("working alias leaked into Runtime")
    leaked = [name for name in ("Demand Map", "Fulfillment Coverage", "Meeting Mode") if name.lower() in runtime.lower() or name.lower() in ota.lower()]
    if leaked:
        fail(f"Cadence 12+ leaked into UI: {leaked}")
    else:
        ok("Demand Map / Fulfillment Coverage UI not started")
    explore = (BACKEND / "app" / "explore_meta.py").read_text(encoding="utf-8")
    if "fleet-firmware-rollout" not in explore or INTENT not in explore:
        fail("Explorer linkage missing")
    else:
        ok("Explorer linkage: Manufacturing / IoT → Fleet Firmware Rollout")


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
    src = (BACKEND / "app" / "runtime.py").read_text(encoding="utf-8")
    if "interpret_profile" in src or "interpreter_spike" in src:
        fail("interpreter spike wired into live execute_intent")
    else:
        ok("no interpreter refactor; CityCare spike remains parallel")
    if not (DOCS / "cadences" / "ax-cadence-11.md").exists():
        fail("missing ax-cadence-11.md")
    else:
        ok("cadence 11 report present")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    mod = SourceFileLoader("validate_ax_cadence10", str(BACKEND / "scripts" / "validate_ax_cadence10.py")).load_module()
    code = mod.main()
    if code != 0:
        fail("validate_ax_cadence10.py regression failed")
        return
    ok("Cadence 0-10 regression passed")


def main() -> int:
    print("=== AX Cadence 11 validation (device fleet / OTA readiness) ===\n")
    check_health()
    check_profile()
    check_ota_run()
    check_regression_heroes()
    check_ui()
    check_boundaries()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
