#!/usr/bin/env python3
"""AX Cadence 6 validation. Presentation freeze + regression."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
DOCS = ROOT / "docs"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

HF = {
    "intent": "ensure_baggage_connection",
    "subject": {"bagId": "HF123456", "connectingFlight": "HF281"},
    "context": {"priority": "high"},
}
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
ACME = {
    "intent": "maintain_inspection_experience",
    "subject": {"cameraId": "ACME-CAM-14", "lineId": "LINE-B"},
    "context": {"sloMs": 40},
}
CC = {
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


def check_health_and_demo_order() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if h.get("cadence") != 6:
            fail(f"cadence not 6: {h.get('cadence')}")
        else:
            ok("health cadence 6")
        demo = client.get("/demo").json()
        product = demo.get("product") or {}
        if "Agentic Experience" not in (product.get("line") or ""):
            fail("product line missing DX→AX")
        else:
            ok("product DX→AX line")
        if not product.get("axLoop"):
            fail("axLoop missing from product")
        else:
            ok("AX loop in product config")
        featured = demo.get("featured") or []
        if not featured:
            fail("no featured enterprises")
            return
        first = featured[0].get("enterprise", {}).get("id")
        if first != "high-flight-airlines":
            fail(f"High Flight should be first, got {first}")
        else:
            ok("High Flight first in demo order")
        for row in featured[:4]:
            card = row.get("heroCard") or {}
            if not card.get("proves") or not card.get("intentId"):
                fail(f"hero card incomplete for {row.get('enterprise', {}).get('id')}")
            else:
                ok(f"hero card metadata {row.get('enterprise', {}).get('id')}")


def check_presenter_docs() -> None:
    for name in ["AX-DEMO-SCRIPT.md", "AX-DEMO-RUNBOOK.md", "AX-FAQ.md", "cadences/ax-cadence-6.md"]:
        path = DOCS / name
        if not path.exists():
            fail(f"missing doc {name}")
        else:
            ok(f"doc {name}")


def check_explore_routes() -> None:
    with TestClient(app) as client:
        for path in [
            "/explore",
            "/explore/agents",
            "/explore/autonomy",
            "/explore/my-context/rocket-bank",
            "/explore/policies",
            "/catalog/apis",
            "/catalog/checkSimSwap",
            "/catalog/createSession",
            "/catalog/verifyLocation",
        ]:
            r = client.get(path)
            if r.status_code != 200:
                fail(f"{path} -> {r.status_code}")
            else:
                ok(f"{path} resolves")


def check_hero_reset_replay() -> None:
    with TestClient(app) as client:
        for body, label, outcome in [
            (HF, "High Flight", "AT_RISK"),
            (RB, "Rocket Bank", "STEP_UP"),
            (ACME, "Acme", "ASSURED"),
            (CC, "CityCare", "ELIGIBLE"),
        ]:
            client.post("/executions/reset")
            t1 = client.post("/intents", json=body).json()
            t2 = client.post("/intents", json=body).json()
            if t1.get("outcome", {}).get("outcome") != outcome:
                fail(f"{label} outcome {t1.get('outcome')}")
            elif t1.get("outcome", {}).get("outcome") != t2.get("outcome", {}).get("outcome"):
                fail(f"{label} replay outcome drift")
            else:
                ok(f"{label} deterministic replay")


def check_evidence_reuse_reset() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        client.post("/intents", json=RB)
        rec = client.post("/intents", json=RECOVERY).json()
        if rec.get("invocations"):
            fail("recovery should reuse without invocations")
        else:
            ok("evidence reuse after trust")
        client.post("/executions/reset")
        store = client.get("/explore/evidence-store").json()
        if store.get("evidence"):
            fail("evidence store not cleared on reset")
        else:
            ok("evidence store reset")


def check_frontend_files() -> None:
    for rel in ["src/pages/Close.jsx", "src/components/AxLoop.jsx", "src/pages/Home.jsx"]:
        if not (FRONTEND / rel).exists():
            fail(f"missing frontend {rel}")
        else:
            ok(f"frontend {rel}")


def check_frontend_build() -> None:
    proc = subprocess.run(["npm", "run", "build"], cwd=FRONTEND, capture_output=True, text=True, shell=True)
    if proc.returncode != 0:
        fail(f"frontend build:\n{proc.stderr}")
    else:
        ok("frontend build")


def main() -> int:
    print("=== AX Cadence 6 validation ===\n")
    check_health_and_demo_order()
    check_presenter_docs()
    check_explore_routes()
    check_hero_reset_replay()
    check_evidence_reuse_reset()
    check_frontend_files()
    check_frontend_build()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  • {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
