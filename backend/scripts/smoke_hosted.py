#!/usr/bin/env python3
"""Hosted smoke test for NetAware AX. Usage: python smoke_hosted.py https://host [user:pass]"""
from __future__ import annotations

import json
import os
import sys

import httpx

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


def _credentials() -> tuple[tuple[str, str] | None, str]:
    user = os.getenv("DEMO_USERNAME", "").strip()
    password = os.getenv("DEMO_PASSWORD", "").strip()
    if len(sys.argv) > 2 and ":" in sys.argv[2]:
        user, _, password = sys.argv[2].partition(":")
    if user and password:
        return (user, password), ""
    return None, ""


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python smoke_hosted.py https://hosted-url [user:pass]")
        return 2
    base = sys.argv[1].rstrip("/")
    basic, _ = _credentials()
    failures: list[str] = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            failures.append(msg)
            print("FAIL", msg)
        else:
            print("PASS", msg)

    if basic:
        denied = httpx.get(f"{base}/demo", timeout=30.0)
        check(denied.status_code == 401, "unauthenticated access rejected")

    with httpx.Client(base_url=base, auth=basic, timeout=120.0, follow_redirects=True) as client:
        health = client.get("/health")
        check(health.status_code == 200, "/health")
        h = health.json()
        check(h.get("cadence") == 6, f"cadence {h.get('cadence')}")
        check(h.get("version") == "0.6.1-ax6.1", f"version {h.get('version')}")
        check(h.get("productBehaviorFrozen") is True, "product frozen")
        home = client.get("/")
        check(home.status_code == 200 and "html" in home.headers.get("content-type", "").lower(), "frontend /")
        check(client.get("/explore").status_code == 200, "explorer")
        apis = client.get("/catalog/apis").json()
        check(len(apis.get("apis") or []) == 13, "13 catalog families")
        check(len(client.get("/catalog/checkSimSwap").json().get("intents") or []) >= 1, "SIM Swap reverse")
        check(len(client.get("/catalog/createSession").json().get("domains") or []) >= 1, "QoD reverse")

        client.post("/executions/reset")
        hf = client.post("/intents", json=HF).json()
        check(hf.get("outcome", {}).get("outcome") == "AT_RISK", "High Flight AT_RISK")
        rb = client.post("/intents", json=RB).json()
        check(rb.get("outcome", {}).get("outcome") == "STEP_UP", "Rocket Bank STEP_UP")
        acme = client.post("/intents", json=ACME).json()
        check(acme.get("outcome", {}).get("outcome") == "ASSURED", "Acme ASSURED")
        cc = client.post("/intents", json=CC).json()
        check(cc.get("outcome", {}).get("outcome") == "ELIGIBLE", "CityCare ELIGIBLE")
        rec = client.post("/intents", json=RECOVERY).json()
        check(rec.get("outcome", {}).get("outcome") == "CONTINUITY_ALIGNED", "evidence reuse outcome")
        check(not rec.get("invocations"), "evidence reuse no invocations")
        client.post("/executions/reset")
        check(client.get("/explore/evidence-store").json().get("evidence") == [], "reset clears evidence")
        rb2 = client.post("/intents", json=RB).json()
        check(rb2.get("outcome", {}).get("outcome") == "STEP_UP", "replay RB")
        print(json.dumps({"build": h.get("build"), "basicAuth": h.get("basicAuthConfigured")}, indent=2))

    if failures:
        print("\n".join(failures))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
