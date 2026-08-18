#!/usr/bin/env python3
"""AX Cadence 6.1 validation — presentation clarity patch only."""
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
        if h.get("cadence") != 6:
            fail(f"cadence must stay 6: {h.get('cadence')}")
        elif h.get("cadencePatch") != "6.1":
            fail(f"cadencePatch not 6.1: {h.get('cadencePatch')}")
        else:
            ok("health cadence 6 / patch 6.1")
        if h.get("version") != "0.6.1-ax6.1":
            fail(f"version {h.get('version')}")
        else:
            ok("version 0.6.1-ax6.1")
        if not h.get("productBehaviorFrozen"):
            fail("product must remain frozen")
        else:
            ok("product behavior frozen")


def check_briefing_clarity() -> None:
    with TestClient(app) as client:
        cases = [
            ("high-flight-airlines", "baggage-connection", "myWorld", "networkAdds"),
            ("rocket-bank", "high-value-payment-protection", "myWorld", "networkAdds"),
            ("acme-manufacturing", "critical-inspection-camera", "headline"),
            ("citycare-health", "pharmacy-age-gate", "zeroContextAnswer"),
        ]
        for ent, uc, *fields in cases:
            body = client.get(f"/demo/{ent}/{uc}").json()
            vc = body.get("valueClarity") or {}
            if not body.get("networkValueFraming"):
                fail(f"{ent} missing networkValueFraming")
                continue
            missing = [f for f in fields if not vc.get(f)]
            if missing:
                fail(f"{ent}/{uc} valueClarity missing {missing}")
            else:
                ok(f"{ent} briefing value clarity")
            caps = body.get("capabilities") or []
            if caps and not any(c.get("networkRole") for c in caps):
                fail(f"{ent} capabilities missing networkRole labels")
            elif caps:
                ok(f"{ent} capability network roles")


def check_catalog_presentation() -> None:
    with TestClient(app) as client:
        apis = client.get("/catalog/apis").json().get("apis") or []
        if len(apis) != 13:
            fail(f"catalog families {len(apis)}")
        else:
            ok("13 catalog families")
        with_role = sum(1 for row in apis if (row.get("api") or {}).get("networkRole"))
        if with_role < 10:
            fail(f"too few families with networkRole: {with_role}")
        else:
            ok(f"{with_role} families labelled Observe/Verify/Act")
        detail = client.get("/catalog/apis/sim-swap").json()
        if not (detail.get("api") or {}).get("applicationValue"):
            fail("sim-swap missing applicationValue")
        else:
            ok("catalog family application value")


def check_camara_label_separation() -> None:
    from app.presentation import audit_family_camara_labels  # noqa: WPS433
    from app.registry import load_registry  # noqa: WPS433

    registry = load_registry()
    label_errors: list[str] = []
    for fam in registry.families:
        label_errors.extend(audit_family_camara_labels(fam))
    if label_errors:
        fail(f"CAMARA label audit: {label_errors[:5]}")
    else:
        ok("13 families: NetAware status, API version maturity, and project lifecycle separated")

    with TestClient(app) as client:
        sim = client.get("/catalog/apis/sim-swap").json()
        api = sim.get("api") or {}
        if api.get("apiVersionMaturity") != "STABLE PUBLIC":
            fail(f"SIM Swap apiVersionMaturity: {api.get('apiVersionMaturity')}")
        elif sim.get("camaraProjectLifecycle") != "Incubating":
            fail(f"SIM Swap project lifecycle should be technical-only Incubating: {sim.get('camaraProjectLifecycle')}")
        else:
            ok("SIM Swap: STABLE PUBLIC version, Incubating project lifecycle separated")

        ident = client.get("/catalog/apis/device-identifier").json()
        ident_api = ident.get("api") or {}
        if ident_api.get("apiVersionMaturity") != "INITIAL / PRE-STABLE":
            fail(f"Device Identifier apiVersionMaturity: {ident_api.get('apiVersionMaturity')}")
        elif "experimental" not in (ident.get("specMaturity") or []):
            fail("Device Identifier internal specMaturity must remain experimental")
        else:
            ok("Device Identifier: honest initial/pre-stable version label")

        detail = client.get("/catalog/retrieveIdentifier").json()
        variant = (detail.get("catalogVariants") or [{}])[0]
        if not variant.get("apiVersionMaturity"):
            fail("operation drill-down missing apiVersionMaturity")
        else:
            ok("operation drill-down exposes API version maturity")


def check_regression_import() -> None:
    import validate_ax_cadence6  # noqa: WPS433

    code = validate_ax_cadence6.main()
    if code != 0:
        fail("cadence 6 regression failed")
    else:
        ok("cadence 6 regression still passes")


def check_frontend_build() -> None:
    proc = subprocess.run(["npm", "run", "build"], cwd=FRONTEND, capture_output=True, text=True, shell=True)
    if proc.returncode != 0:
        fail(f"frontend build:\n{proc.stderr}")
    else:
        ok("frontend build")


def main() -> int:
    print("=== AX Cadence 6.1 validation ===\n")
    if not (DOCS / "cadences" / "ax-cadence-6.1.md").exists():
        fail("missing ax-cadence-6.1.md")
    else:
        ok("doc cadences/ax-cadence-6.1.md")
    check_health()
    check_briefing_clarity()
    check_catalog_presentation()
    check_camara_label_separation()
    check_regression_import()
    check_frontend_build()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  • {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
