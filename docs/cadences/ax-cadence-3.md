# AX Cadence 3 — Second live Agentic Experience (High Flight)

**Status:** Implemented and validated.  
**Cadence:** 3  
**Executable intents:** `assess_network_trust`, `ensure_baggage_connection`  
**Demo UI:** Home + Explore + Rocket Bank + High Flight live runs  

Cadence 4 is not started.

---

## 1. Runtime request

```json
POST /intents
{
  "intent": "ensure_baggage_connection",
  "subject": {
    "bagId": "HF123456",
    "connectingFlight": "HF281"
  },
  "context": {
    "priority": "high"
  }
}
```

---

## 2. What NetAware already knew

From onboarding/configuration (not in the POST body):

- Enterprise: High Flight Airlines  
- Application: Baggage Operations  
- Agent: Baggage Operations Agent  
- Use case: Baggage connection  
- Purpose: **Service Delivery** (CONFIGURED APPLICATION / INTENT PROFILE)  
- Subscriptions, entitlements, policy, consent, DPA, region, providers, autonomy  
- Network subject: Bag HF123456 → handler device HF-HDL-0192 → `+1••••••7712`

---

## 3. Plan v1

1. Get baggage journey state (`getBaggageJourney` — DOMAIN)  
2. Get connecting flight status (`getFlightStatus` — DOMAIN)  
3. Verify baggage/handler location (`verifyLocation` — NETWORK)  
4. Check device reachability (`getReachabilityStatus` — NETWORK)  
5. Check connectivity if useful (`checkNetworkQuality` — NETWORK)  
6. Consider QoD if network limiting (`createSession` — considered)  
7. Assess connection risk  
8. Recommend or trigger permitted action  

---

## 4. Policy block

**Location Verification**

| Check | Result |
|-------|--------|
| Relevant | YES |
| Available | YES |
| Subscribed | YES |
| Purpose | PERMITTED |
| Agreement / DPA | PERMITTED |
| Consent | REQUIRED |
| Consent state | NOT AVAILABLE |

**Result:** `BLOCKED_BY_POLICY` — **CONFIGURED DEMO POLICY** (not a universal airline/legal rule)

---

## 5. Replan trigger

Location was planned for baggage position/proximity. When blocked, NetAware **materially revises** the evidence strategy:

- Cannot invoke `verifyLocation`  
- Cannot fabricate network location  
- Must use airline operational evidence instead  

---

## 6. Plan v2

1. ✓ Baggage journey (scan/event location from airline)  
2. ✓ Flight status  
3. ✗ Location Verification — **blocked**  
4. **+ Ground Operations transfer ETA** (`getGroundTransferETA` — ENTERPRISE)  
5. ✓ Device reachability  
6. ✓ Connectivity insights  
7. — QoD considered, not required  
8. Assess connection risk  
9. Recommend expedite transfer  

Narrative: *"We cannot verify network location. Use airline operational evidence instead."*

---

## 7. Domain APIs invoked

| Operation | Kind | Label |
|-----------|------|-------|
| `getBaggageJourney` | DOMAIN | Baggage Journey |
| `getFlightStatus` | DOMAIN | Flight Status |

All labelled **SIMULATED DOMAIN API** in the trace.

---

## 8. Network APIs invoked

| Operation | Route | Provider |
|-----------|-------|----------|
| `getReachabilityStatus` | DIRECT | Network Provider A |
| `checkNetworkQuality` | AGGREGATED | Aggregator A → Network Provider A |

---

## 9. APIs not invoked and why

| API | Why |
|-----|-----|
| `verifyLocation` | BLOCKED_BY_POLICY — consent not available |
| `createSession` (QoD) | NOT_REQUIRED — physical transfer time is limiting factor, not network quality |

---

## 10. Telco Finder

Bag HF123456 → tracked by handler device HF-HDL-0192 → network identifier `+1••••••7712` → **Network Provider A**

---

## 11. API Finder

Resolves availability for mapped network capabilities on the resolved network:

- Location Verification: available (then blocked by policy)  
- Reachability: available  
- Connectivity Insights: available  
- QoD: available (not invoked)  

---

## 12. Provider / routes

**HYBRID topology** (different from Rocket Bank DIRECT-only):

- Reachability: NetAware → Network Provider A (DIRECT)  
- Connectivity: NetAware → Aggregator A → Network Provider A (AGGREGATED)  
- Location: would have been AGGREGATED but blocked  

---

## 13. Evidence

- **Baggage journey:** in transit, last scan T-B-SORT-12 (airline scan — not network location)  
- **Flight status:** HF281 gate B22, boarding closes in 28 min  
- **Ground transfer ETA:** 22 min vs 15 min safe margin  
- **Reachability:** handler device online (not physical location)  
- **Connectivity:** adequate — network not limiting  

No synthetic location evidence generated.

---

## 14. Autonomy

| Action | Level |
|--------|-------|
| Observe / assess | ACT |
| Recommend expedite transfer | ACT_WITH_APPROVAL |
| Change flight plan | NOT_AUTHORIZED |

**Result:** `EXPEDITE_TRANSFER` recommended, **approval required**.

---

## 15. Final response

```json
{
  "outcome": "AT_RISK",
  "confidence": 0.88,
  "recommendedAction": "EXPEDITE_TRANSFER",
  "approvalRequired": true,
  "limitingFactor": "PHYSICAL_TRANSFER_TIME",
  "networkConstraint": false,
  "reasonCodes": [
    "TIGHT_CONNECTION_WINDOW",
    "TRANSFER_ETA_EXCEEDS_SAFE_MARGIN"
  ],
  "decisionOwner": "HIGH_FLIGHT_OPERATIONS"
}
```

---

## 16. Shared runtime reuse / generalization

| Component | Status |
|-----------|--------|
| `runtime_models.ExecutionTrace` | Extended (planHistory, replan, routes, apiKind on invocations) |
| Policy evaluation (`evaluate_capability_policy`) | Reused unchanged |
| Catalog resolution (`_op_meta`, `_primary_op`, graph mappings) | Reused unchanged |
| `POST /intents` + execution store | Reused; dispatch by intent |
| Scenario seeds (`data/runtime/*.yaml`) | **Configuration** per enterprise |
| Intent runners (`_INTENT_RUNNERS` registry) | **Generalized** dispatch pattern |
| Rocket Bank runner | Unchanged behavior |
| High Flight runner | New scenario function — no `if intent == ...` in UI |

**Scenario-specific:** beats, simulated responses, network subject mapping, plan steps — all in `high-flight-baggage.yaml` + `run_ensure_baggage_connection`.

---

## 17. Tests

```powershell
cd backend
python scripts/validate_ax_cadence0.py   # 38 checks
python scripts/validate_ax_cadence1.py   # 26 checks
python scripts/validate_ax_cadence2.py   # 30 checks — Rocket Bank regression
python scripts/validate_ax_cadence3.py   # 39 checks — High Flight + regression
```

Frontend build passes.

---

## 18. Known gaps

- Domain/enterprise API invocations are simulated — not live airline integrations  
- In-memory execution store only (demo)  
- Acme Manufacturing remains configuration-only until Cadence 4  
- Briefing page still shows configuration; live run is on `/demo/high-flight-airlines/baggage-connection/run`  
- Identity architecture for agents remains simulated placeholder  

---

**STOP.** Cadence 4 not started.
