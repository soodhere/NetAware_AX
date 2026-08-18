#!/usr/bin/env python3
"""AX Cadence 4 validation. Acme closed-loop + CityCare governance + regression."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app, registry  # noqa: E402

ACME = {
    "intent": "maintain_inspection_experience",
    "subject": {"cameraId": "ACME-CAM-14", "lineId": "LINE-B"},
    "context": {"sloMs": 40},
}

CITYCARE = {
    "intent": "verify_pharmacy_age_gate",
    "subject": {"transactionId": "RX-10442", "phoneNumber": "+1••••••8843"},
    "context": {"ageThreshold": 18},
}

RB = {
    "intent": "assess_network_trust",
    "subject": {"transactionId": "RB-78421", "phoneNumber": "+1••••••0198"},
    "context": {"amount": 25000, "currency": "USD"},
}

HF = {
    "intent": "ensure_baggage_connection",
    "subject": {"bagId": "HF123456", "connectingFlight": "HF281"},
    "context": {"priority": "high"},
}

errors: list[str] = []
oks: list[str] = []


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK — {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL — {msg}")


def check_acme() -> None:
    with TestClient(app) as client:
        resp = client.post("/intents", json=ACME)
        if resp.status_code != 200:
            fail(f"Acme POST failed: {resp.status_code} {resp.text}")
            return
        trace = resp.json()
        ok("Acme POST /intents works")

        if (trace.get("purpose") or {}).get("source") != "CONFIGURED APPLICATION / INTENT PROFILE":
            fail("Acme purpose not from configuration")
        else:
            ok("Acme configured purpose")

        qod_initial = next((d for d in trace.get("decisions") or [] if d.get("id") == "dec-qod-initial"), None)
        if not qod_initial or qod_initial.get("state") != "NOT_REQUIRED":
            fail(f"initial QoD decision unexpected: {qod_initial}")
        else:
            ok("initial QoD NOT_REQUIRED")

        if not trace.get("conditionChange") or trace["conditionChange"].get("trigger") != "OBJECTIVE_BREACH":
            fail("objective breach not recorded")
        else:
            ok("deterministic OBJECTIVE_BREACH")

        history = trace.get("planHistory") or []
        if len(history) < 2:
            fail("Acme planHistory missing v1/v2")
        else:
            ok("Acme genuine replan with plan v1/v2")

        invoked = [i.get("operationId") for i in trace.get("invocations") or []]
        if "createSession" not in invoked:
            fail(f"QoD createSession not invoked: {invoked}")
        else:
            ok("QoD createSession invoked after replan")
        if invoked.count("checkNetworkQuality") < 2:
            fail("post-action observe missing (need initial + verify)")
        else:
            ok("post-action observation for verification")

        if "getSession" not in invoked:
            fail("getSession verification missing")
        else:
            ok("verification getSession invoked")

        outcome = trace.get("outcome") or {}
        if outcome.get("outcome") != "ASSURED" or outcome.get("verification") != "PASSED":
            fail(f"Acme outcome unexpected: {outcome}")
        else:
            ok("outcome ASSURED with verification PASSED")

        auto = trace.get("autonomy") or {}
        if auto.get("invoke_qod") != "ACT" or auto.get("approvalRequired") is not False:
            fail(f"Acme autonomy unexpected: {auto}")
        else:
            ok("QoD autonomy ACT without approval")

        second = client.post("/intents", json=ACME).json()
        if second.get("executionId") != trace.get("executionId"):
            fail("Acme replay not deterministic")
        else:
            ok("Acme replay deterministic")


def check_citycare() -> None:
    with TestClient(app) as client:
        resp = client.post("/intents", json=CITYCARE)
        if resp.status_code != 200:
            fail(f"CityCare POST failed: {resp.status_code} {resp.text}")
            return
        trace = resp.json()
        ok("CityCare POST /intents works")

        invoked = {i.get("operationId") for i in trace.get("invocations") or []}
        if invoked != {"verifyAge"}:
            fail(f"CityCare invoked unexpected: {invoked}")
        else:
            ok("only verifyAge invoked")

        if not registry.has_operation("verifyAge") or not registry.has_operation("KYC_Match"):
            fail("catalog missing verifyAge or KYC_Match")
        else:
            ok("verifyAge and KYC_Match catalog-backed")

        age = next((d for d in trace.get("decisions") or [] if d.get("capabilityId") == "age_verification"), None)
        kyc = next((d for d in trace.get("decisions") or [] if d.get("capabilityId") == "kyc_match"), None)
        if not age or age.get("state") != "SELECTED":
            fail(f"age verification not selected: {age}")
        else:
            ok("Age Verification selected")
        if not kyc or kyc.get("state") != "BLOCKED_BY_POLICY":
            fail(f"KYC Match not blocked: {kyc}")
        else:
            ok("KYC Match BLOCKED_BY_POLICY")

        outcome = trace.get("outcome") or {}
        if outcome.get("outcome") != "ELIGIBLE" or outcome.get("broaderKycUsed") is not False:
            fail(f"CityCare outcome unexpected: {outcome}")
        else:
            ok("ELIGIBLE with broaderKycUsed false")

        raw = json.dumps(outcome).lower()
        if "dateofbirth" in raw or "address" in raw or "full name" in raw:
            fail("outcome contains broad KYC fields")
        else:
            ok("no broad KYC fields in response")

        auto = trace.get("autonomy") or {}
        if auto.get("dispense_or_refuse_medication") != "NOT_AUTHORIZED":
            fail("autonomy allows dispensing")
        else:
            ok("autonomy prevents dispensing decision")

        second = client.post("/intents", json=CITYCARE).json()
        if second.get("executionId") != trace.get("executionId"):
            fail("CityCare replay not deterministic")
        else:
            ok("CityCare replay deterministic")


def check_regression() -> None:
    with TestClient(app) as client:
        health = client.get("/health").json()
        if health.get("cadence") not in {4, 5, 6}:
            fail(f"cadence not 4/5: {health.get('cadence')}")
        else:
            ok(f"health cadence {health.get('cadence')}")
        intents = set(health.get("executableIntents") or [])
        heroes = {
            "assess_network_trust",
            "ensure_baggage_connection",
            "maintain_inspection_experience",
            "verify_pharmacy_age_gate",
        }
        if not heroes.issubset(intents):
            fail(f"hero intents missing: {intents}")
        elif health.get("cadence") in {5, 6}:
            if "assess_recovery_continuity" not in intents:
                fail(f"cadence 5/6 missing recovery intent: {intents}")
            else:
                ok("five executable intents (four heroes + recovery reuse)")
        elif intents != heroes:
            fail(f"executable intents unexpected: {intents}")
        else:
            ok("four executable intents")

        rb = client.post("/intents", json=RB).json()
        if rb.get("outcome", {}).get("outcome") != "STEP_UP":
            fail("Rocket Bank regression failed")
        else:
            ok("Rocket Bank unchanged")

        hf = client.post("/intents", json=HF).json()
        if hf.get("outcome", {}).get("outcome") != "AT_RISK":
            fail("High Flight regression failed")
        else:
            ok("High Flight unchanged")


def check_foreign() -> None:
    hits = []
    for path in (BACKEND / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "Meta_Demo" in text or "Jigyasa" in text:
            hits.append(str(path.relative_to(ROOT)))
    if hits:
        fail(f"forbidden repo references: {hits}")
    else:
        ok("no Meta_Demo/Jigyasa references")


def main() -> int:
    for path in [
        ROOT / "data" / "runtime" / "acme-inspection.yaml",
        ROOT / "data" / "runtime" / "citycare-pharmacy.yaml",
        FRONTEND / "src" / "pages" / "Runtime.jsx",
    ]:
        if path.exists():
            ok(f"{path.name} exists")
        else:
            fail(f"missing {path.name}")

    check_acme()
    check_citycare()
    check_regression()
    check_foreign()

    if errors:
        print(f"\nCadence 4 FAILED ({len(errors)} errors, {len(oks)} ok)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"\nCadence 4 PASSED ({len(oks)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
