#!/usr/bin/env python3
"""AX Cadence 14 validation — Demand Map + commercial opportunity. Do not start Cadence 15."""
from __future__ import annotations

import json
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

from app.config import MODEL_CADENCE, SCHEMAS_DIR, UI_CADENCE  # noqa: E402
from app.demand import DEMAND_STATES, public_demand, validate_demand_schema  # noqa: E402
from app.main import app, graph, registry, store  # noqa: E402
from app.portfolio import visible_rows  # noqa: E402

errors: list[str] = []
oks: list[str] = []

HEROES = [
    ("STEP_UP", {"intent": "assess_network_trust", "subject": {"transactionId": "RB-78421", "phoneNumber": "+1••••••0198"}, "context": {"amount": 25000, "currency": "USD"}}),
    ("VERIFIED", {"intent": "verify_mobile_number", "subject": {"phoneNumber": "+1••••••0198"}, "context": {"nvVariant": "cellular-nv1", "accessType": "CELLULAR", "claimedMsisdn": True, "businessEvent": "CUSTOMER_SIGNING_IN"}}),
    ("CONTINUE", {"intent": "ensure_baggage_connection", "subject": {"bagId": "HF123456", "connectingFlight": "HF281"}, "context": {"priority": "high"}}),
    ("ASSURED", {"intent": "maintain_inspection_experience", "subject": {"cameraId": "ACME-CAM-14", "lineId": "LINE-B"}, "context": {"sloMs": 40}}),
    ("ELIGIBLE", {"intent": "verify_pharmacy_age_gate", "subject": {"transactionId": "RX-10442", "phoneNumber": "+1••••••8843"}, "context": {"ageThreshold": 18}}),
]
REAL_OPS = ("Verizon", "T-Mobile", "Vodafone", "Deutsche Telekom", "Singtel", "AT&T")


def ok(msg: str) -> None:
    oks.append(msg)
    print(f"OK - {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL - {msg}")


def check_health() -> None:
    with TestClient(app) as client:
        h = client.get("/health").json()
        if UI_CADENCE not in {14, 15, 16, 17} or h.get("uiCadence") not in {14, 15, 16, 17}:
            fail(f"uiCadence {h.get('uiCadence')} / {UI_CADENCE}")
        else:
            ok("uiCadence 14")
        if h.get("modelCadence") != 7 or MODEL_CADENCE != 7:
            fail("modelCadence")
        else:
            ok("modelCadence 7")
        if h.get("version") != "0.6.1-ax6.1":
            fail(f"version {h.get('version')}")
        else:
            ok("live version 0.6.1-ax6.1")
        if len(registry.families) != 13:
            fail("catalog expanded")
        else:
            ok("13 API families preserved")


def check_schema() -> None:
    path = SCHEMAS_DIR / "demand-record.json"
    if not path.exists():
        fail("missing demand-record.json")
        return
    ok("demand schema exists")
    body = json.loads(path.read_text(encoding="utf-8"))
    props = body.get("properties") or {}
    if any(k in props for k in ("revenue", "price", "ARR", "tam", "opportunityScore")):
        fail("demand schema has financial fields")
    else:
        ok("no invented revenue/TAM on demand schema")


def check_demand_api() -> None:
    with TestClient(app) as client:
        res = client.get("/demand")
        if res.status_code >= 400:
            fail(f"/demand {res.status_code}")
            return
        payload = res.json()
        records = payload.get("records") or []
        if not records:
            fail("no demand records")
            return
        ok(f"{len(records)} demand records")
        for rec in records:
            try:
                validate_demand_schema(rec)
            except Exception as exc:
                fail(f"schema {rec.get('demandId')}: {exc}")
                return
        ok("demand derived records match schema")
        financial_keys = {"revenue", "price", "ARR", "tam", "opportunityScore", "lostRevenue"}
        if any(key in rec for rec in records for key in financial_keys):
            fail("financial scoring leaked onto demand records")
        elif any(key in (payload.get("summary") or {}) for key in financial_keys):
            fail("financial scoring leaked onto demand summary")
        elif payload.get("notRevenue") is not True or payload.get("notTam") is not True:
            fail("demand payload not labelled as non-financial")
        else:
            ok("no invented revenue / TAM / financial scoring")
        if any(name in json.dumps(payload) for name in REAL_OPS):
            fail("real operator names")
        else:
            ok("no real operator claims")
        if not payload.get("consumesCoverage"):
            fail("C13 not declared as coverage source")
        else:
            ok("C13 remains fulfillment source")
        ent = client.get("/demand/enterprises/rocket-bank")
        if ent.status_code >= 400 or not (ent.json().get("records") or []):
            fail("demand-side entry missing")
        else:
            ok("demand-side enterprise entry works")
        sup = client.get("/demand/providers/simulated-operator-a")
        if sup.status_code >= 400 or not (sup.json().get("records") or []):
            fail("supply-side entry missing")
        else:
            ok("direct provider traversal works")
        agg = client.get("/demand/providers/simulated-aggregator-b")
        note = json.dumps(agg.json()).lower()
        if agg.status_code >= 400:
            fail("aggregator traversal missing")
        elif "does not own" not in note and "doesnotownapis" not in note:
            fail("aggregator ownership wording missing")
        else:
            ok("aggregator traversal does not claim API ownership")
        cap = client.get("/demand/capabilities/device_reachability")
        if cap.status_code >= 400 or not (cap.json().get("records") or []):
            fail("capability → intents reverse mapping missing")
        else:
            ok("capability → intents reverse mapping")
        intent = client.get("/demand/intents/prepare_ota_cohort")
        if intent.status_code >= 400 or not (intent.json().get("records") or []):
            fail("intent → supply forward mapping missing")
        else:
            ok("intent → supply forward mapping")


def check_semantics() -> None:
    payload = public_demand(store, graph, registry)
    records = payload.get("records") or []
    states = {r.get("demandState") for r in records}
    if not {"POTENTIAL", "FULFILLED", "UNFULFILLED", "NOT_REQUIRED"} <= states:
        fail(f"demand states {states}")
    else:
        ok("demand states populated")
    if any(r.get("potential") and r.get("qualified") for r in records):
        fail("potential == qualified")
    else:
        ok("potential != qualified")
    if any(r.get("invoked") for r in records):
        fail("demand treated as invocation")
    else:
        ok("qualified != invocation")
    explore_q = [r for r in records if r.get("maturity") == "EXPLORE" and r.get("qualified")]
    if explore_q:
        fail("EXPLORE became fake qualified demand")
    else:
        ok("EXPLORE does not become fake qualified demand")
    unfulfilled = [r for r in records if r.get("demandState") == "UNFULFILLED"]
    if any(r.get("maturity") == "EXPLORE" for r in unfulfilled):
        fail("unfulfilled without genuine configured demand")
    else:
        ok("unfulfilled demand requires genuine configured demand")
    nv_b = next((r for r in records if r.get("coverageRecordId") == "nv-wifi-provider-b" and r.get("capability") == "number_possession_verification"), None)
    if not nv_b or nv_b.get("demandState") != "UNFULFILLED" or nv_b.get("blockingGap") != "ENTITLEMENT_SERVER_UNAVAILABLE":
        fail(f"NV ECS gap {nv_b}")
    else:
        ok("NV ECS gap represented as unfulfilled qualified demand")
    ota = next((r for r in records if r.get("coverageRecordId") == "ota-provider-c" and r.get("capability") == "roaming_status"), None)
    if not ota or ota.get("demandState") != "PARTIALLY_FULFILLED" or ota.get("affectedUnits") != 500:
        fail(f"OTA C {ota}")
    else:
        ok("OTA Provider C gap represented with 500 simulated units")
    hf = next((r for r in records if r.get("intentId") == "ensure_baggage_connection" and r.get("capability") == "device_reachability"), None)
    if not hf or hf.get("demandState") != "FULFILLED" or not hf.get("fulfillmentVsOutcome"):
        fail(f"High Flight {hf}")
    else:
        ok("High Flight unreachable is fulfilled demand")
    qod = next((r for r in records if r.get("intentId") == "maintain_inspection_experience" and r.get("capability") == "quality_on_demand"), None)
    if not qod or qod.get("demandState") != "NOT_REQUIRED" or not qod.get("contextualDemand"):
        fail(f"Acme QoD {qod}")
    else:
        ok("Acme QoD demand becomes contextual after SLO breach")
    kyc = next((r for r in records if r.get("intentId") == "verify_pharmacy_age_gate" and r.get("capability") == "kyc_match"), None)
    age = next((r for r in records if r.get("intentId") == "verify_pharmacy_age_gate" and r.get("capability") == "age_verification"), None)
    if not kyc or kyc.get("demandState") != "NOT_REQUIRED" or not age or age.get("demandState") != "FULFILLED":
        fail(f"CityCare {kyc} {age}")
    else:
        ok("CityCare minimum-capability selection represented")
    units_intents = {r.get("intentId") for r in records if r.get("affectedUnits")}
    if units_intents - {"prepare_ota_cohort"}:
        fail(f"invented affectedUnits {units_intents}")
    else:
        ok("affectedUnits only where simulated fleet exists")
    if not any((r.get("provenance") or []) for r in records):
        fail("provenance missing")
    else:
        ok("provenance exists")
    enable = payload.get("enablement") or []
    if not any(e.get("gap") == "ENTITLEMENT_SERVER_UNAVAILABLE" for e in enable):
        fail("ECS enablement impact missing")
    else:
        ok("supply-gap → demand impact for ECS")
    if len(visible_rows(store)) != 17:
        fail("portfolio size")
    else:
        ok("17-use-case portfolio preserved")
    if "QUALIFIED" not in DEMAND_STATES:
        fail("qualified state missing")
    else:
        ok("qualified-demand definition encoded")


def check_live() -> None:
    with TestClient(app) as client:
        client.post("/executions/reset")
        for expected, body in HEROES:
            res = client.post("/intents", json=body)
            got = (res.json().get("outcome") or {}).get("outcome")
            if got != expected:
                fail(f"{body['intent']} {got} != {expected}")
            else:
                ok(f"{body['intent']} unchanged {expected}")
        wifi = client.post(
            "/intents",
            json={
                "intent": "verify_mobile_number",
                "subject": {"phoneNumber": "+1••••••0198"},
                "context": {"nvVariant": "wifi-ecs-gap", "accessType": "WIFI", "claimedMsisdn": True, "businessEvent": "CUSTOMER_SIGNING_IN"},
            },
        )
        if (wifi.json().get("outcome") or {}).get("outcome") != "CAPABILITY_UNAVAILABLE":
            fail("NV wifi ECS live outcome changed")
        else:
            ok("NV behavior unchanged")
        ota = client.post(
            "/intents",
            json={"intent": "prepare_ota_cohort", "subject": {"campaignId": "ACME-FW-8-4-CRITICAL", "applicationId": "acme-device-fleet"}, "context": {"otaWave": "prepare", "campaignPriority": "CRITICAL"}},
        )
        if (ota.json().get("outcome") or {}).get("outcome") != "NETWORK_QUALIFIED_COHORT":
            fail("OTA live outcome changed")
        else:
            ok("OTA behavior unchanged")
        rec = client.post("/intents", json={"intent": "assess_recovery_continuity", "subject": {"recoveryId": "RB-REC-19", "phoneNumber": "+1••••••0198"}, "context": {"channel": "web"}})
        if (rec.json().get("outcome") or {}).get("outcome") != "CONTINUITY_ALIGNED":
            fail("recovery changed")
        else:
            ok("CityCare / recovery live outcomes unchanged")


def check_ui() -> None:
    demand = (FRONTEND / "src" / "pages" / "Demand.jsx").read_text(encoding="utf-8")
    app_src = (FRONTEND / "src" / "App.jsx").read_text(encoding="utf-8")
    demo = (FRONTEND / "src" / "pages" / "DemoPick.jsx").read_text(encoding="utf-8")
    briefing = (FRONTEND / "src" / "pages" / "Briefing.jsx").read_text(encoding="utf-8")
    coverage = (FRONTEND / "src" / "pages" / "Coverage.jsx").read_text(encoding="utf-8")
    explore = (FRONTEND / "src" / "pages" / "Explore.jsx").read_text(encoding="utf-8")
    runtime = (FRONTEND / "src" / "pages" / "Runtime.jsx").read_text(encoding="utf-8")
    ota = (FRONTEND / "src" / "pages" / "OtaFleet.jsx").read_text(encoding="utf-8")
    if "Demand Map" not in demand or "Why NetAware" not in demand:
        fail("Demand Map / Why NetAware missing")
    else:
        ok("Demand Map and Why NetAware panel present")
    if "See Demand" not in demo or "See Demand" not in briefing or "See Demand" not in coverage:
        fail("portfolio/coverage demand links missing")
    else:
        ok("portfolio and coverage integration")
    if "Open business story" not in demand:
        fail("reverse portfolio link missing")
    else:
        ok("Demand Map opens business story")
    if "See Demand" not in explore or "What does this enable?" not in explore:
        fail("explorer integration missing")
    else:
        ok("explorer See Demand / What does this enable")
    if "Demand Map" in runtime or "Demand Map" in ota:
        fail("Demand Map leaked into Runtime/OTA")
    else:
        ok("Runtime / OTA unchanged")
    if "Meeting Mode" in demand or "opportunity score" in demand.lower():
        fail("Meeting Mode / opportunity score leaked")
    else:
        ok("Cadence 16 not started" if UI_CADENCE >= 15 else "Cadence 15 not started")
    if UI_CADENCE < 15 and "Cadence 14" not in app_src:
        fail("footer cadence")
    elif UI_CADENCE >= 15 and not any(tag in app_src for tag in ("Cadence 14", "Cadence 15", "Cadence 16", "Cadence 17")):
        fail("footer cadence")
    else:
        ok("UI cadence 14 footer")
    if "Technical View" not in demand:
        fail("technical view missing")
    else:
        ok("sales and technical views present")


def check_boundaries() -> None:
    hits = [p.name for p in (BACKEND / "app").rglob("*.py") if "Meta_Demo" in p.read_text(encoding="utf-8") or "Jigyasa" in p.read_text(encoding="utf-8")]
    if hits:
        fail(f"other-repo references {hits}")
    else:
        ok("Meta_Demo and Jigyasa untouched")
    if not (DOCS / "cadences" / "ax-cadence-14.md").exists():
        fail("missing ax-cadence-14.md")
    else:
        ok("cadence 14 report present")


def check_regression() -> None:
    from importlib.machinery import SourceFileLoader

    mod = SourceFileLoader("validate_ax_cadence13", str(BACKEND / "scripts" / "validate_ax_cadence13.py")).load_module()
    code = mod.main()
    if code != 0:
        fail("validate_ax_cadence13.py regression failed")
        return
    ok("Cadence 0-13 regression passed")


def main() -> int:
    print("=== AX Cadence 14 validation (Demand Map + commercial opportunity) ===\n")
    check_health()
    check_schema()
    check_demand_api()
    check_semantics()
    check_live()
    check_ui()
    check_boundaries()
    check_regression()
    print(f"\n=== Summary: {len(oks)} OK, {len(errors)} FAIL ===")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
