#!/usr/bin/env python3
"""AX Cadence 2 validation. Rocket Bank live run only."""
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

CANONICAL = {
    "intent": "assess_network_trust",
    "subject": {"transactionId": "RB-78421", "phoneNumber": "+1••••••0198"},
    "context": {"amount": 25000, "currency": "USD"},
}

INVOKED = {
    "phoneNumberVerify",
    "checkSimSwap",
    "checkDeviceSwap",
    "retrieveIdentifier",
    "getRoamingStatus",
}

errors: list[str] = []
oks: list[str] = []


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK — {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL — {msg}")


def check_files() -> None:
    path = FRONTEND / "src" / "pages" / "Runtime.jsx"
    if not path.exists():
        fail("Runtime.jsx missing")
    else:
        ok("live runtime view exists")
    text = (FRONTEND / "src" / "App.jsx").read_text(encoding="utf-8")
    if "TRUST" in text or "EXPAND" in text or "ASSURE" in text:
        fail("App navigation cloned TRUST/EXPAND/ASSURE")
    else:
        ok("product nav remains Demo / Explore")


def check_runtime() -> None:
    with TestClient(app) as client:
        health = client.get("/health").json()
        if health.get("cadence") not in {4, 5, 6} or not health.get("executionEngine"):
            fail(f"health cadence/engine unexpected: {health.get('cadence')} {health.get('executionEngine')}")
        else:
            ok(f"GET /health cadence {health.get('cadence')}, execution engine on")
        executable = set(health.get("executableIntents") or [])
        if "assess_network_trust" not in executable:
            fail(f"assess_network_trust not executable: {executable}")
        else:
            ok("assess_network_trust remains executable")

        bad = client.post("/intents", json={})
        if bad.status_code != 400:
            fail(f"empty intent should be 400, got {bad.status_code}")
        else:
            ok("invalid request rejected")

        unknown = client.post("/intents", json={"intent": "not_a_real_intent"})
        if unknown.status_code not in {400, 403, 409}:
            fail(f"unknown intent status {unknown.status_code}")
        else:
            ok("unknown intent rejected")

        unauth = client.post(
            "/intents",
            json={**CANONICAL, "agentId": "baggage-operations-agent"},
        )
        if unauth.status_code != 403:
            fail(f"unauthorized agent status {unauth.status_code}")
        else:
            ok("agent authorization is enforced")

        other = client.post("/intents", json={"intent": "locate_baggage"})
        if other.status_code in {200, 201, 202}:
            fail("Acme intent executed when not configured")
        else:
            ok("non-executable intents remain rejected")

        first = client.post("/intents", json=CANONICAL)
        if first.status_code != 200:
            fail(f"canonical POST failed: {first.status_code} {first.text}")
            return
        trace = first.json()
        ok("valid POST /intents returns a trace")

        if (trace.get("purpose") or {}).get("source") != "RESOLVED FROM CONFIGURATION":
            fail("purpose was not resolved from configuration")
        else:
            ok("Purpose comes from configuration")

        if (trace.get("actor") or {}).get("agent", {}).get("id") != "payments-protection-agent":
            fail("agent not resolved")
        else:
            ok("Payments Risk Agent resolved")

        mapped_caps = {d.get("capabilityId") for d in trace.get("decisions") or [] if d.get("relevant")}
        if "sim_continuity" not in mapped_caps or "location_verification" not in mapped_caps:
            fail(f"candidate capabilities missing: {mapped_caps}")
        else:
            ok("candidate capabilities come from the mapping graph")

        invoked = [i.get("operationId") for i in trace.get("invocations") or []]
        if set(invoked) != INVOKED:
            fail(f"invoked set unexpected: {invoked}")
        else:
            ok("only selected APIs invoked")
        for op in invoked:
            if not registry.has_operation(op):
                fail(f"invoked operation not in catalog: {op}")
        else:
            ok("invoked operationIds exist in AX_ACTIVE_CATALOG")

        if "verifyLocation" in invoked or "checkNumberRecycling" in invoked or "createSession" in invoked:
            fail("blocked or not-required API was invoked")
        else:
            ok("blocked/not-required APIs were not invoked")

        loc = next((d for d in trace.get("decisions") or [] if d.get("capabilityId") == "location_verification"), None)
        if not loc or loc.get("state") != "BLOCKED_BY_POLICY":
            fail(f"location decision unexpected: {loc}")
        else:
            ok("location is BLOCKED_BY_POLICY (configured consent)")

        rec = next((d for d in trace.get("decisions") or [] if d.get("capabilityId") == "number_recycling"), None)
        if not rec or rec.get("state") != "NOT_REQUIRED":
            fail(f"recycling decision unexpected: {rec}")
        else:
            ok("number recycling considered and not required")

        telco = trace.get("telcoFinder") or {}
        if "Network Provider A" not in json.dumps(telco):
            fail("Telco Finder missing Network Provider A")
        else:
            ok("Telco Finder represented")

        finder = trace.get("apiFinder") or {}
        ops = {r.get("operationId") for r in finder.get("results") or []}
        if "checkSimSwap" not in ops or "verifyLocation" not in ops:
            fail(f"API Finder incomplete: {ops}")
        else:
            ok("API Finder represented")

        route = trace.get("route") or {}
        if route.get("type") != "DIRECT" or "Network Provider A" not in str(route.get("display")):
            fail(f"route unexpected: {route}")
        else:
            ok("configured DIRECT route to Network Provider A")

        ev_ops = {e.get("operationId") for e in trace.get("evidence") or []}
        if ev_ops != set(invoked):
            fail(f"evidence ops {ev_ops} != invoked {invoked}")
        else:
            ok("evidence generated only from successful invocations")

        outcome = trace.get("outcome") or {}
        if outcome.get("outcome") != "STEP_UP" or outcome.get("decisionOwner") != "ENTERPRISE":
            fail(f"outcome unexpected: {outcome}")
        else:
            ok("deterministic STEP_UP; enterprise owns the financial decision")
        if outcome.get("networkTrust") != "DISRUPTED":
            fail("network trust not DISRUPTED")
        else:
            ok("network trust DISRUPTED (not a fraud verdict)")

        auto = trace.get("autonomy") or {}
        if auto.get("decline_transaction") != "NOT_AUTHORIZED" or auto.get("recommend_step_up") != "RECOMMEND":
            fail(f"autonomy unexpected: {auto}")
        else:
            ok("autonomy prevents declining the payment")

        stages = {p.get("stage") for p in trace.get("policyEvaluations") or []}
        if stages != {"ACTOR_INTENT", "CAPABILITY_API", "AUTONOMY_ACTION"}:
            fail(f"policy stages unexpected: {stages}")
        else:
            ok("policy has actor, capability, and autonomy stages")

        views = trace.get("views") or {}
        if views.get("derivedFrom") != trace.get("executionId"):
            fail("views are not derived from the canonical trace")
        else:
            ok("all UI views derive from the same execution trace")

        second = client.post("/intents", json=CANONICAL).json()
        if second.get("outcome") != outcome or second.get("executionId") != trace.get("executionId"):
            fail("replay/second run is not deterministic")
        else:
            ok("replay produces the same outcome")

        latest = client.get("/executions/latest")
        if latest.status_code != 200 or latest.json().get("executionId") != trace.get("executionId"):
            fail("GET /executions/latest mismatch")
        else:
            ok("GET /executions/latest returns the same trace")

        if "FRAUD" in json.dumps(outcome).upper() and "FRAUD DETECTED" in json.dumps(outcome).upper():
            fail("outcome claims fraud detected")
        else:
            ok("outcome does not claim fraud detected")


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
    check_runtime()
    check_foreign()
    if errors:
        print(f"\nCadence 2 FAILED ({len(errors)} errors, {len(oks)} ok)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"\nCadence 2 PASSED ({len(oks)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
