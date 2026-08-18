#!/usr/bin/env python3
"""AX Cadence 5 validation. Explorer product surface + evidence reuse + regression."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app, registry  # noqa: E402

RB = {
    "intent": "assess_network_trust",
    "subject": {"transactionId": "RB-78421", "phoneNumber": "+1••••••0198"},
    "context": {"amount": 25000, "currency": "USD"},
}
RECOVERY = {
    "intent": "assess_recovery_continuity",
    "subject": {"recoveryId": "RB-REC-19", "phoneNumber": "+1••••••0198"},
    "context": {"channel": "web"},
}
HF = {
    "intent": "ensure_baggage_connection",
    "subject": {"bagId": "HF123456", "connectingFlight": "HF281"},
    "context": {"priority": "high"},
}
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

errors: list[str] = []
oks: list[str] = []


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK — {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL — {msg}")


def check_health() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if h.get("cadence") not in {5, 6}:
            fail(f"cadence not 5/6: {h.get('cadence')}")
        else:
            ok(f"health cadence {h.get('cadence')}")
        if not h.get("explorerProductSurface"):
            fail("explorerProductSurface flag missing")
        else:
            ok("explorer product surface flag")
        if len(h.get("executableIntents") or []) != 5:
            fail(f"expected 5 executable intents: {h.get('executableIntents')}")
        else:
            ok("five executable intents")


def check_explorer_nav() -> None:
    with TestClient(app) as client:
        body = client.get("/explore").json()
        nav_ids = [n["id"] if isinstance(n, dict) else n for n in body.get("nav") or []]
        expected = [
            "domains",
            "use-cases",
            "intents",
            "agents",
            "my-context",
            "purposes",
            "policies",
            "autonomy",
            "capabilities",
            "catalog",
            "providers",
        ]
        if nav_ids != expected:
            fail(f"explorer nav mismatch: {nav_ids}")
        else:
            ok("explorer nav all 11 entities")
        if body.get("businessFamilies") != 13:
            fail(f"expected 13 families, got {body.get('businessFamilies')}")
        else:
            ok("13 active catalog families in explore summary")


def check_explorer_entities() -> None:
    with TestClient(app) as client:
        for path in [
            "/explore/agents",
            "/explore/purposes",
            "/explore/policies",
            "/explore/autonomy",
            "/explore/providers",
            "/explore/my-context",
        ]:
            r = client.get(path)
            if r.status_code != 200:
                fail(f"{path} -> {r.status_code}")
            else:
                ok(f"{path} resolves")

        agent = client.get("/explore/agents/payments-protection-agent").json()
        if agent.get("identityModel") != "SIMULATED FOR PROTOTYPE":
            fail("agent identity model label missing")
        else:
            ok("agent Explorer with simulated identity label")

        ctx = client.get("/explore/my-context/rocket-bank").json()
        if not ctx.get("knownFromConfiguration") or not ctx.get("runtimeRequestExample"):
            fail("my context missing configured vs runtime split")
        else:
            ok("My Context configured vs runtime")

        intent = client.get("/intents/assess_network_trust").json()
        if not intent.get("runtimeRequest") or not intent.get("knownFromConfiguration"):
            fail("intent detail missing caller vs known split")
        else:
            ok("intent caller vs configured knowledge")

        cap = client.get("/capabilities/sim_continuity").json()
        if not cap.get("liveBehavior"):
            fail("capability live behavior missing")
        else:
            ok("capability live behavior links")

        pol = client.get("/explore/policies/rocket-bank-trust-policy").json()
        if not pol.get("exercisedEffects"):
            fail("policy exercised effects missing")
        else:
            ok("policy runtime effect links")


def check_traversal() -> None:
    with TestClient(app) as client:
        op = client.get("/catalog/checkSimSwap").json()
        if not op.get("intents"):
            fail("reverse traversal checkSimSwap -> intents failed")
        else:
            ok("reverse: operation -> intents")
        dom = client.get("/domains/financial").json()
        if not dom.get("networkFamilies") and not dom.get("useCaseRows"):
            fail("forward domain enrichment weak")
        else:
            ok("forward: domain -> use cases / families")
        api = client.get("/catalog/apis/sim-swap").json()
        if not api.get("liveReferences") and not api.get("operations"):
            fail("catalog api enrichment failed")
        else:
            ok("catalog family enrichment")


def check_evidence_reuse() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        rec = client.post("/intents", json=RECOVERY)
        if rec.status_code == 200 and len(rec.json().get("invocations") or []) == 0:
            ok("recovery without prior trust may reuse zero or invoke fresh")
        trust = client.post("/intents", json=RB)
        if trust.status_code != 200:
            fail(f"trust POST failed: {trust.status_code}")
            return
        ok("trust execution generates evidence")
        store_after = client.get("/explore/evidence-store").json()
        if not store_after.get("evidence"):
            fail("evidence store empty after trust")
        else:
            ok("evidence persisted to canonical store")

        rec2 = client.post("/intents", json=RECOVERY)
        if rec2.status_code != 200:
            fail(f"recovery POST failed: {rec2.status_code}")
            return
        trace = rec2.json()
        reused = [d for d in trace.get("decisions") or [] if d.get("state") == "EVIDENCE_REUSED"]
        if len(reused) < 3:
            fail(f"expected 3 EVIDENCE_REUSED decisions, got {len(reused)}")
        else:
            ok("EVIDENCE_REUSED decisions for sim/device/roaming")
        if trace.get("invocations"):
            fail(f"recovery should skip API calls when reusing: {trace.get('invocations')}")
        else:
            ok("no duplicate API invocations on reuse")
        src = (trace.get("evidence") or [{}])[0].get("sourceExecutionId")
        if src != "ax-rb-trust-001":
            fail(f"source execution link wrong: {src}")
        else:
            ok("reuse links source execution ax-rb-trust-001")
        audit = (trace.get("evidence") or [{}])[0].get("reuseAudit") or {}
        checks = audit.get("checks") or {}
        if not checks.get("fresh") or not checks.get("purposeCompatibility"):
            fail(f"reuse eligibility checks incomplete: {checks}")
        else:
            ok("TTL/purpose/subject reuse checks recorded")


def check_hero_regression() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        rb = client.post("/intents", json=RB).json()
        if rb.get("outcome", {}).get("outcome") != "STEP_UP":
            fail(f"Rocket Bank regression: {rb.get('outcome')}")
        else:
            ok("Rocket Bank STEP_UP unchanged")
        hf = client.post("/intents", json=HF).json()
        if hf.get("outcome", {}).get("outcome") != "AT_RISK":
            fail(f"High Flight regression: {hf.get('outcome')}")
        else:
            ok("High Flight AT_RISK unchanged")
        acme = client.post("/intents", json=ACME).json()
        o = acme.get("outcome") or {}
        if o.get("outcome") != "ASSURED" or o.get("verification") != "PASSED":
            fail(f"Acme regression: {o}")
        else:
            ok("Acme ASSURED unchanged")
        cc = client.post("/intents", json=CITYCARE).json()
        co = cc.get("outcome") or {}
        if co.get("outcome") != "ELIGIBLE" or co.get("broaderKycUsed") is not False:
            fail(f"CityCare regression: {co}")
        else:
            ok("CityCare ELIGIBLE unchanged")


def check_frontend_build() -> None:
    if not (FRONTEND / "package.json").exists():
        ok("frontend skipped")
        return
    proc = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        shell=True,
    )
    if proc.returncode != 0:
        fail(f"frontend build failed:\n{proc.stdout}\n{proc.stderr}")
    else:
        ok("frontend build")


def main() -> int:
    print("=== AX Cadence 5 validation ===\n")
    check_health()
    check_explorer_nav()
    check_explorer_entities()
    check_traversal()
    check_evidence_reuse()
    check_hero_regression()
    check_frontend_build()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  • {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
