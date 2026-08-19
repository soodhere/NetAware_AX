#!/usr/bin/env python3
"""Hosted smoke test for NetAware AX Cadence 17. Usage: python smoke_hosted.py https://host [user:pass]"""
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
HF_SWAP = {
    "intent": "ensure_baggage_connection",
    "subject": {"bagId": "HF123456", "connectingFlight": "HF281"},
    "context": {"priority": "high", "hfVariant": "scanner-unreachable"},
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


def _nv(variant: str, access: str) -> dict:
    return {
        "intent": "verify_mobile_number",
        "subject": {"phoneNumber": "+1••••••0198"},
        "context": {
            "nvVariant": variant,
            "accessType": access,
            "claimedMsisdn": True,
            "businessEvent": "CUSTOMER_SIGNING_IN",
        },
    }


def _ota(wave: str) -> dict:
    return {
        "intent": "prepare_ota_cohort",
        "subject": {"campaignId": "ACME-FW-8-4-CRITICAL", "applicationId": "acme-device-fleet"},
        "context": {"otaWave": wave, "campaignPriority": "CRITICAL"},
    }


def _credentials() -> tuple[tuple[str, str] | None, str]:
    user = (os.getenv("BASIC_AUTH_USERNAME") or os.getenv("DEMO_USERNAME") or "").strip()
    password = (os.getenv("BASIC_AUTH_PASSWORD") or os.getenv("DEMO_PASSWORD") or "").strip()
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

    open_health = httpx.get(f"{base}/health", timeout=60.0)
    check(open_health.status_code == 200, "/health unauthenticated for hosting checks")

    if basic:
        denied = httpx.get(f"{base}/demo", timeout=30.0)
        check(denied.status_code == 401, "unauthenticated access rejected")

    with httpx.Client(base_url=base, auth=basic, timeout=120.0, follow_redirects=True) as client:
        health = client.get("/health")
        check(health.status_code == 200, "/health")
        h = health.json()
        check(h.get("cadence") == 6, f"product cadence {h.get('cadence')}")
        check(h.get("modelCadence") == 7, f"modelCadence {h.get('modelCadence')}")
        check(h.get("uiCadence") == 17, f"uiCadence {h.get('uiCadence')}")
        check(h.get("version") == "0.6.1-ax6.1", f"version {h.get('version')}")
        check(h.get("productBehaviorFrozen") is True, "product frozen")
        check(h.get("meetingPresentation") is True, "C16 Meeting Mode flag")
        check(h.get("visualIntelligence") is True, "C17 visual intelligence flag")
        home = client.get("/")
        html = home.text if home.status_code == 200 else ""
        check(home.status_code == 200 and "html" in home.headers.get("content-type", "").lower(), "frontend /")
        check("Cadence 17" in html or "index-" in html, "frontend bundle present")
        check(client.get("/explore").status_code == 200, "explorer")
        apis = client.get("/catalog/apis").json()
        check(len(apis.get("apis") or []) == 13, "13 catalog families")
        check(len(client.get("/catalog/checkSimSwap").json().get("intents") or []) >= 1, "SIM Swap reverse")
        check(len(client.get("/catalog/createSession").json().get("domains") or []) >= 1, "QoD reverse")

        pre = client.get("/preflight").json()
        check(pre.get("label") == "DEMO READY", f"preflight {pre.get('label')}")
        check(pre.get("catalogFamilies") == 13, f"preflight families {pre.get('catalogFamilies')}")
        check(pre.get("portfolioUseCases") == 17, f"preflight use cases {pre.get('portfolioUseCases')}")
        check(pre.get("uiCadence") == 17, f"preflight uiCadence {pre.get('uiCadence')}")

        mapped = client.get("/map").json()
        check(len(mapped.get("useCases") or []) == 17, "map 17 use cases")
        check(len((mapped.get("matrix") or {}).get("columns") or []) == 13, "map 13 families")
        check(len((mapped.get("matrix") or {}).get("cells") or []) >= 1, "map cells derived")

        start = client.get("/start").json()
        check(bool(start.get("audiences")), "stakeholder entry")
        meet = client.get("/meet").json()
        paths = meet.get("paths") or {}
        for audience in ("enterprise", "operator", "aggregator"):
            for depth in ("exec", "sales", "tech"):
                steps = ((paths.get(audience) or {}).get(depth) or {}).get("steps") or []
                hrefs = [s.get("href") for s in steps if s.get("href")]
                check(len(hrefs) == len(steps) and steps, f"meeting {audience}/{depth} CTAs")

        client.post("/executions/reset")
        hf = client.post("/intents", json=HF).json()
        check(hf.get("outcome", {}).get("outcome") == "CONTINUE", "High Flight CONTINUE")
        swap = client.post("/intents", json=HF_SWAP).json()
        check(swap.get("outcome", {}).get("outcome") == "SWAP_DEVICE", "High Flight SWAP_DEVICE")
        rb = client.post("/intents", json=RB).json()
        check(rb.get("outcome", {}).get("outcome") == "STEP_UP", "Rocket Bank STEP_UP")
        nv1 = client.post("/intents", json=_nv("cellular-nv1", "CELLULAR")).json()
        check(nv1.get("outcome", {}).get("outcome") == "VERIFIED", "NV cellular VERIFIED")
        check((nv1.get("pathSelection") or {}).get("selectedPath") == "NV1_NETWORK_BASED", "NV1 path")
        nv2 = client.post("/intents", json=_nv("wifi-nv2", "WIFI")).json()
        check(nv2.get("outcome", {}).get("outcome") == "VERIFIED", "NV Wi-Fi VERIFIED")
        gap = client.post("/intents", json=_nv("wifi-ecs-gap", "WIFI")).json()
        check(gap.get("outcome", {}).get("outcome") == "CAPABILITY_UNAVAILABLE", "NV ECS gap")
        acme = client.post("/intents", json=ACME).json()
        check(acme.get("outcome", {}).get("outcome") == "ASSURED", "Acme ASSURED")
        ota = client.post("/intents", json=_ota("prepare")).json()
        check(ota.get("outcome", {}).get("outcome") == "NETWORK_QUALIFIED_COHORT", "OTA prepare")
        funnel = {row["id"]: row["count"] for row in (ota.get("otaVisual") or {}).get("funnel") or []}
        check(funnel.get("campaign") == 10000 and funnel.get("eligible") == 8400, "OTA funnel 10000/8400")
        reassess = client.post("/intents", json=_ota("reassess")).json()
        check(reassess.get("outcome", {}).get("outcome") == "COHORT_EXPANDED", "OTA reassess")
        cc = client.post("/intents", json=CC).json()
        check(cc.get("outcome", {}).get("outcome") == "ELIGIBLE", "CityCare ELIGIBLE")
        rec = client.post("/intents", json=RECOVERY).json()
        check(rec.get("outcome", {}).get("outcome") == "CONTINUITY_ALIGNED", "evidence reuse outcome")
        check(not rec.get("invocations"), "evidence reuse no invocations")
        client.post("/executions/reset")
        check(client.get("/explore/evidence-store").json().get("evidence") == [], "reset clears evidence")
        rb2 = client.post("/intents", json=RB).json()
        check(rb2.get("outcome", {}).get("outcome") == "STEP_UP", "replay RB")
        print(json.dumps({"build": h.get("build"), "basicAuth": h.get("basicAuthConfigured"), "uiCadence": h.get("uiCadence")}, indent=2))

    if failures:
        print("\n".join(failures))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
