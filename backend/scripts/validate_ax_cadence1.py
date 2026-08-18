#!/usr/bin/env python3
"""AX Cadence 1 validation. Explore/demo reads only. No execution engine."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app, registry, store  # noqa: E402

errors: list[str] = []
oks: list[str] = []


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK — {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL — {msg}")


def check_frontend_files() -> None:
    needed = [
        FRONTEND / "src" / "pages" / "Home.jsx",
        FRONTEND / "src" / "pages" / "DemoPick.jsx",
        FRONTEND / "src" / "pages" / "Briefing.jsx",
        FRONTEND / "src" / "pages" / "Explore.jsx",
        FRONTEND / "src" / "App.jsx",
        FRONTEND / "src" / "styles.css",
    ]
    missing = [str(p.relative_to(ROOT)) for p in needed if not p.exists()]
    if missing:
        fail(f"missing frontend files: {missing}")
    else:
        ok("Home, Demo, Briefing and Explore views exist")
    text = (FRONTEND / "src" / "App.jsx").read_text(encoding="utf-8")
    if "TRUST" in text or "EXPAND" in text or "ASSURE" in text:
        fail("Cadence 1 navigation cloned TRUST/EXPAND/ASSURE")
    else:
        ok("navigation is Home / Demo / Explore, not TRUST/EXPAND/ASSURE")


def check_no_post_intents() -> None:
    with TestClient(app) as client:
        post = client.post("/intents", json={"intent": "locate_baggage"})
        if post.status_code in {200, 201, 202}:
            fail("non-executable locate_baggage intent must not run")
        else:
            ok("non-executable intents are rejected")


def check_http() -> None:
    with TestClient(app) as client:
        health = client.get("/health").json()
        if health.get("cadence") not in {1, 2, 3, 4, 5, 6}:
            fail(f"expected cadence 1+, got {health.get('cadence')} / {health.get('cadencePatch')}")
        else:
            ok(f"GET /health cadence {health.get('cadence')}")
        if not health.get("demoUi"):
            fail("demoUi should be true")
        else:
            ok("demo UI on")
        if health.get("catalog", {}).get("businessFamilies") != 13:
            fail("catalog is not 13 business families")
        else:
            ok("health reports 13 business families")

        demo = client.get("/demo")
        if demo.status_code != 200:
            fail("GET /demo failed")
            return
        featured = demo.json().get("featured") or []
        labels = {(row.get("enterprise") or {}).get("id") for row in featured}
        if not {"rocket-bank", "high-flight-airlines", "acme-manufacturing", "citycare-health"} <= labels:
            fail(f"featured enterprises incomplete: {labels}")
        else:
            ok("Start Demo offers Rocket Bank, High Flight, Acme, CityCare")

        hf = client.get("/demo/high-flight-airlines/baggage-connection")
        if hf.status_code != 200:
            fail("High Flight briefing missing")
            return
        body = hf.json()
        systems = set(body.get("existingSystems") or [])
        apis = {a.get("name") for a in body.get("existingApis") or []}
        if not {"Baggage Operations", "Flight Operations", "Ground Operations"} <= systems:
            fail(f"High Flight systems incomplete: {systems}")
        else:
            ok("High Flight shows existing airline systems")
        if not {"Baggage Journey", "Flight Status", "Ground Operations"} <= apis:
            fail(f"High Flight existing APIs incomplete: {apis}")
        else:
            ok("High Flight shows existing airline APIs")
        cap_labels = [c.get("label", "").lower() for c in body.get("capabilities") or []]
        joined = " ".join(cap_labels)
        if "location" not in joined or "reachability" not in joined:
            fail("High Flight complementary capabilities missing")
        else:
            ok("High Flight shows complementary network capabilities")
        cadence = health.get("cadence", 0)
        if cadence >= 2 and body.get("runnable"):
            if not body.get("executionEngine"):
                fail("runnable briefing should expose executionEngine at cadence 2+")
            else:
                ok("runnable briefing exposes execution engine")
        elif body.get("executionEngine") or not body.get("runtimeNotExecuted"):
            fail("briefing implies runtime execution")
        else:
            ok("briefing states runtime was not executed")
        if (body.get("intent") or {}).get("plain") != "Ensure bag HF123456 makes connecting flight HF281.":
            fail(f"intent plain language unexpected: {(body.get('intent') or {}).get('plain')}")
        else:
            ok("Intent is a concrete outcome sentence")
        req = (body.get("intent") or {}).get("request") or {}
        if req.get("intent") != "ensure_baggage_connection" or "bagId" not in (req.get("subject") or {}):
            fail("minimal POST /intents example missing")
        else:
            ok("minimal structured intent request is shown, not executed")
        known = body.get("knownFromOnboarding") or {}
        runtime = body.get("runtimeRequest") or {}
        if "ONBOARDING" not in str(known.get("source")) or "RUNTIME" not in str(runtime.get("source")):
            fail("onboarding vs runtime request not labelled")
        else:
            ok("configured knowledge is separate from the runtime request")
        agent = body.get("agent") or {}
        appn = body.get("application") or {}
        if agent.get("id") == appn.get("id") or agent.get("kind") != "AUTHORIZED_AGENT":
            fail("agent is not distinct from application")
        else:
            ok("Authorized Agent is distinct from Application")
        if not body.get("policyPreview") or not body.get("autonomyPreview"):
            fail("policy/autonomy preview missing")
        else:
            ok("policy and autonomy are visible as configuration")
        if cadence >= 2 and body.get("runnable"):
            ok("runnable briefing may describe live execution path")
        elif (body.get("relevance") or {}).get("actuallyInvoked") is not False:
            fail("briefing must not claim APIs were invoked")
        else:
            ok("mapping is POTENTIALLY RELEVANT, not actually invoked")
        chain = body.get("chain") or {}
        if not chain.get("intentId") or not chain.get("catalogFamilies"):
            fail("domain→catalog chain missing")
        else:
            ok("Domain → Use case → Intent → Capability → Catalog chain present")

        rb = client.get("/demo/rocket-bank/high-value-payment-protection")
        acme = client.get("/demo/acme-manufacturing/critical-inspection-camera")
        if rb.status_code != 200 or acme.status_code != 200:
            fail("Rocket Bank or Acme briefing missing")
        else:
            ok("Rocket Bank and Acme briefings load")
            if "Payments" not in (rb.json().get("existingSystems") or []):
                fail("Rocket Bank existing systems missing")
            if "MES" not in " ".join(acme.json().get("existingSystems") or []):
                fail("Acme existing systems missing")

        catalog = client.get("/catalog/apis")
        families = catalog.json().get("apis") or []
        if len(families) != 13:
            fail(f"Explorer catalog is {len(families)} families, expected 13")
        else:
            ok("API Catalog presents 13 business families")
        ident = next((row for row in families if (row.get("api") or {}).get("id") == "device-identifier"), None)
        if not ident:
            fail("Device Identifier family missing from catalog")
        elif ident.get("businessStatus") != "CURRENT_FOCUS" or "experimental" not in (ident.get("specMaturity") or []):
            fail("Device Identifier must show CURRENT_FOCUS and experimental maturity")
        else:
            ok("Device Identifier: CURRENT FOCUS + experimental CAMARA maturity")
        ops = ident.get("operations") or []
        op_ids = {o.get("operation_id") for o in ops}
        if not {"retrieveIdentifier", "retrieveType", "retrievePPID"} <= op_ids:
            fail("Device Identifier technical operations incomplete")
        else:
            ok("technical drill-down uses actual operationIds")

        sim = client.get("/catalog/apis/sim-swap")
        if sim.status_code != 200:
            fail("SIM Swap reverse missing")
        else:
            domains = [d.get("id") for d in sim.json().get("domains") or []]
            use_cases = [u.get("id") for u in sim.json().get("useCases") or []]
            if not {"financial", "retail", "insurance"} <= set(domains):
                fail(f"SIM Swap reverse domains incomplete: {domains}")
            elif "high-value-payment-protection" not in use_cases:
                fail("SIM Swap does not reverse to transaction trust")
            else:
                ok("SIM Swap → SIM continuity → trust intents → financial/retail/insurance")

        qod = client.get("/catalog/apis/quality-on-demand")
        qod_domains = {d.get("id") for d in (qod.json().get("domains") or [])}
        if len(qod_domains) < 5:
            fail(f"QoD reverse too narrow: {qod_domains}")
        else:
            ok(f"QoD reverse spans {len(qod_domains)} industries")

        post = client.post("/intents", json={"intent": "locate_baggage"})
        if post.status_code in {200, 201, 202}:
            fail("POST /intents executed non-executable intent")
        else:
            ok(f"non-executable POST /intents rejected ({post.status_code})")


def check_foreign() -> None:
    hits = []
    for path in (BACKEND / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "Meta_Demo" in text or "Jigyasa" in text:
            hits.append(str(path.relative_to(ROOT)))
    if hits:
        fail(f"backend references forbidden repos: {hits}")
    else:
        ok("backend Python does not reference Meta_Demo or Jigyasa")


def main() -> int:
    check_frontend_files()
    check_no_post_intents()
    check_http()
    check_foreign()
    if errors:
        print(f"\nCadence 1 FAILED ({len(errors)} errors, {len(oks)} ok)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"\nCadence 1 PASSED ({len(oks)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
