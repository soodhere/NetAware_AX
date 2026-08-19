#!/usr/bin/env python3
"""AX Cadence 3 validation. High Flight live run + Rocket Bank regression."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.config import UI_CADENCE  # noqa: E402
from app.main import app, registry  # noqa: E402

HF_CANONICAL = {
    "intent": "ensure_baggage_connection",
    "subject": {"bagId": "HF123456", "connectingFlight": "HF281"},
    "context": {"priority": "high"},
}

RB_CANONICAL = {
    "intent": "assess_network_trust",
    "subject": {"transactionId": "RB-78421", "phoneNumber": "+1••••••0198"},
    "context": {"amount": 25000, "currency": "USD"},
}

RB_INVOKED = {
    "phoneNumberVerify",
    "checkSimSwap",
    "checkDeviceSwap",
    "retrieveIdentifier",
    "getRoamingStatus",
}

HF_DOMAIN = {"getBaggageJourney", "getFlightStatus", "getGroundTransferETA"}
HF_NETWORK = {"getReachabilityStatus", "checkNetworkQuality"}

errors: list[str] = []
oks: list[str] = []


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK — {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL — {msg}")


def check_files() -> None:
    paths = [
        FRONTEND / "src" / "pages" / "Runtime.jsx",
        ROOT / "data" / "runtime" / "high-flight-baggage.yaml",
        BACKEND / "app" / "runtime.py",
    ]
    for path in paths:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")
        else:
            ok(f"{path.name} exists")


def check_high_flight() -> None:
    with TestClient(app) as client:
        health = client.get("/health").json()
        if health.get("cadence") not in {4, 5, 6}:
            fail(f"health cadence unexpected: {health.get('cadence')}")
        else:
            ok(f"GET /health cadence {health.get('cadence')}")
        intents = set(health.get("executableIntents") or [])
        if len(intents) < 2 or "assess_network_trust" not in intents:
            fail(f"executable intents unexpected: {intents}")
        else:
            ok("Rocket Bank and High Flight remain executable")

        unauth = client.post(
            "/intents",
            json={**HF_CANONICAL, "agentId": "payments-protection-agent"},
        )
        if unauth.status_code != 403:
            fail(f"wrong agent should be 403, got {unauth.status_code}")
        else:
            ok("High Flight agent authorization enforced")

        resp = client.post("/intents", json=HF_CANONICAL)
        if resp.status_code != 200:
            fail(f"High Flight POST failed: {resp.status_code} {resp.text}")
            return
        trace = resp.json()
        ok("High Flight POST /intents works")

        purpose = trace.get("purpose") or {}
        if "CONFIGURED" not in str(purpose.get("source", "")).upper():
            fail(f"purpose source unexpected: {purpose}")
        else:
            ok("configured Purpose")

        if (trace.get("actor") or {}).get("agent", {}).get("id") != "baggage-operations-agent":
            fail("baggage agent not resolved")
        else:
            ok("Baggage Operations Agent resolved")

        invoked = {i.get("operationId") for i in trace.get("invocations") or []}
        domain_ops = {i.get("operationId") for i in trace.get("invocations") or [] if i.get("apiKind") in {"DOMAIN", "ENTERPRISE"}}
        network_ops = {i.get("operationId") for i in trace.get("invocations") or [] if (i.get("apiKind") or "NETWORK") == "NETWORK"}

        if UI_CADENCE >= 10:
            needed_domain = {"getBaggageJourney", "getFlightStatus", "getRampAssignment"}
            if not needed_domain <= domain_ops:
                fail(f"C10 domain ops missing: {domain_ops}")
            else:
                ok("BRS / DCS / Ground Operations represented")
            if network_ops != {"getReachabilityStatus"}:
                fail(f"C10 network ops unexpected: {network_ops}")
            else:
                ok("only Reachability invoked for default READY state")
            if "verifyLocation" in invoked or "createSession" in invoked:
                fail("Location or QoD invoked")
            else:
                ok("Location and QoD not invoked")
            loc = next((d for d in trace.get("decisions") or [] if d.get("capabilityId") == "location_verification"), None)
            if not loc or loc.get("state") != "NOT_REQUIRED":
                fail(f"location should be NOT_REQUIRED: {loc}")
            else:
                ok("Location NOT_REQUIRED — not bag tracking")
            qod = next((d for d in trace.get("decisions") or [] if d.get("capabilityId") == "quality_on_demand"), None)
            if not qod or qod.get("state") != "NOT_REQUIRED":
                fail(f"QoD unexpected: {qod}")
            else:
                ok("QoD NOT_REQUIRED")
            outcome = trace.get("outcome") or {}
            if outcome.get("outcome") != "CONTINUE" or outcome.get("recommendedAction") != "CONTINUE":
                fail(f"READY outcome {outcome}")
            else:
                ok("default READY → CONTINUE")
            if "EXPEDITE" in json.dumps(outcome):
                fail("EXPEDITE_TRANSFER still featured")
            else:
                ok("EXPEDITE_TRANSFER is not the featured outcome")
            if "HF-HDL-0192" not in json.dumps(trace.get("telcoFinder") or {}):
                fail("scanner not in Telco Finder")
            else:
                ok("network subject is assigned scanner")
            views = trace.get("views") or {}
            if views.get("derivedFrom") != trace.get("executionId"):
                fail("views not derived from canonical trace")
            else:
                ok("canonical trace backs all views")
            second = client.post("/intents", json=HF_CANONICAL).json()
            if second.get("outcome") != outcome or second.get("executionId") != trace.get("executionId"):
                fail("High Flight replay not deterministic")
            else:
                ok("High Flight replay deterministic")
            return

        if not HF_DOMAIN.issubset(domain_ops):
            fail(f"domain/enterprise ops missing: {domain_ops}")
        else:
            ok("domain and enterprise API steps represented")

        if network_ops != HF_NETWORK:
            fail(f"network ops unexpected: {network_ops}")
        else:
            ok("network operations catalog-backed and selective")

        if "verifyLocation" in invoked or "createSession" in invoked:
            fail("blocked or not-required network API was invoked")
        else:
            ok("Location not invoked; QoD not invoked")

        for op in network_ops:
            if not registry.has_operation(op):
                fail(f"network op not in catalog: {op}")
        else:
            ok("network operationIds exist in AX_ACTIVE_CATALOG")

        telco = trace.get("telcoFinder") or {}
        if "Network Provider A" not in json.dumps(telco):
            fail("Telco Finder missing Network Provider A")
        else:
            ok("Telco Finder represented")
        if "HF-HDL-0192" not in json.dumps(telco) and "handler device" not in json.dumps(telco).lower():
            fail("network subject mapping not explicit")
        else:
            ok("network subject mapping explicit (bag → handler device → MSISDN)")

        finder = trace.get("apiFinder") or {}
        ops = {r.get("operationId") for r in finder.get("results") or []}
        if "getReachabilityStatus" not in ops or "verifyLocation" not in ops:
            fail(f"API Finder incomplete: {ops}")
        else:
            ok("API Finder represented")

        routes = trace.get("routes") or []
        route_types = {r.get("operationId"): r.get("type") for r in routes}
        if route_types.get("getReachabilityStatus") != "DIRECT":
            fail(f"reachability route unexpected: {route_types}")
        else:
            ok("Reachability uses DIRECT route")
        if route_types.get("checkNetworkQuality") != "AGGREGATED":
            fail(f"connectivity route unexpected: {route_types}")
        else:
            ok("Connectivity uses AGGREGATED route")

        history = trace.get("planHistory") or []
        if len(history) < 2:
            fail("planHistory missing v1/v2")
        else:
            ok("initial Plan v1 and Plan v2 in planHistory")
        v1_ops = {s.get("operationId") for s in history[0].get("steps") or []}
        v2_ops = {s.get("operationId") for s in history[1].get("steps") or []}
        if "verifyLocation" not in v1_ops:
            fail("Plan v1 missing location")
        else:
            ok("Plan v1 includes Location Verification")
        if "getGroundTransferETA" not in v2_ops or "getGroundTransferETA" in v1_ops:
            fail("Plan v2 ground ops replan incorrect")
        else:
            ok("Plan v2 adds Ground Operations after replan")
        if v1_ops == v2_ops:
            fail("Plan v2 identical to Plan v1")
        else:
            ok("Plan v2 materially differs from Plan v1")

        replan = trace.get("replan") or {}
        if not replan.get("trigger") or "LOCATION" not in str(replan.get("trigger", "")).upper():
            fail(f"replan trigger missing: {replan}")
        else:
            ok("replan trigger documented")

        loc = next((d for d in trace.get("decisions") or [] if d.get("capabilityId") == "location_verification"), None)
        if not loc or loc.get("state") != "BLOCKED_BY_POLICY":
            fail(f"location decision unexpected: {loc}")
        else:
            ok("Location BLOCKED_BY_POLICY")

        qod = next((d for d in trace.get("decisions") or [] if d.get("capabilityId") == "quality_on_demand"), None)
        if not qod or qod.get("state") != "NOT_REQUIRED":
            fail(f"QoD decision unexpected: {qod}")
        else:
            ok("QoD available but NOT_REQUIRED")

        evidence_types = {e.get("type") for e in trace.get("evidence") or []}
        if any(t in evidence_types for t in {"NETWORK_LOCATION", "LOCATION_VERIFICATION"}):
            fail("synthetic location evidence generated")
        else:
            ok("no synthetic location evidence")

        ground = next((d for d in trace.get("decisions") or [] if d.get("operationId") == "getGroundTransferETA"), None)
        if not ground or ground.get("state") != "INVOKED":
            fail(f"ground ops evidence missing: {ground}")
        else:
            ok("Ground Ops evidence added after replan")

        outcome = trace.get("outcome") or {}
        if outcome.get("outcome") != "AT_RISK":
            fail(f"outcome unexpected: {outcome.get('outcome')}")
        else:
            ok("final AT_RISK deterministic")
        if outcome.get("recommendedAction") != "EXPEDITE_TRANSFER":
            fail("recommended action not EXPEDITE_TRANSFER")
        else:
            ok("EXPEDITE_TRANSFER recommended")
        if not outcome.get("approvalRequired"):
            fail("approvalRequired not true")
        else:
            ok("autonomy produces APPROVAL_REQUIRED")
        if outcome.get("limitingFactor") != "PHYSICAL_TRANSFER_TIME":
            fail(f"limiting factor unexpected: {outcome.get('limitingFactor')}")
        else:
            ok("physical transfer is limiting factor")
        if outcome.get("networkConstraint") is not False:
            fail("networkConstraint should be false")
        else:
            ok("networkConstraint false")

        auto = trace.get("autonomy") or {}
        if auto.get("recommend_expedite_transfer") != "ACT_WITH_APPROVAL":
            fail(f"autonomy unexpected: {auto}")
        else:
            ok("expedite transfer ACT_WITH_APPROVAL")

        views = trace.get("views") or {}
        if views.get("derivedFrom") != trace.get("executionId"):
            fail("views not derived from canonical trace")
        else:
            ok("canonical trace backs all views")

        second = client.post("/intents", json=HF_CANONICAL).json()
        if second.get("outcome") != outcome or second.get("executionId") != trace.get("executionId"):
            fail("High Flight replay not deterministic")
        else:
            ok("High Flight replay deterministic")


def check_rocket_bank_regression() -> None:
    with TestClient(app) as client:
        resp = client.post("/intents", json=RB_CANONICAL)
        if resp.status_code != 200:
            fail(f"Rocket Bank regression failed: {resp.status_code}")
            return
        trace = resp.json()
        invoked = {i.get("operationId") for i in trace.get("invocations") or []}
        if set(invoked) != RB_INVOKED:
            fail(f"Rocket Bank invoked set changed: {invoked}")
        else:
            ok("Rocket Bank still passes — same invoked network APIs")
        if trace.get("outcome", {}).get("outcome") != "STEP_UP":
            fail("Rocket Bank outcome changed")
        else:
            ok("Rocket Bank STEP_UP unchanged")
        if trace.get("planHistory"):
            fail("Rocket Bank should not have planHistory")
        else:
            ok("Rocket Bank trace shape unchanged")


def check_foreign() -> None:
    hits = []
    for path in (BACKEND / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "Meta_Demo" in text or "Jigyasa" in text:
            hits.append(str(path.relative_to(ROOT)))
    if hits:
        fail(f"forbidden repo references: {hits}")
    else:
        ok("backend Python does not reference Meta_Demo or Jigyasa")


def main() -> int:
    check_files()
    check_high_flight()
    check_rocket_bank_regression()
    check_foreign()
    if errors:
        print(f"\nCadence 3 FAILED ({len(errors)} errors, {len(oks)} ok)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"\nCadence 3 PASSED ({len(oks)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
