# AX Cadence 2 — First live Agentic Experience

**Status:** Implemented and validated.  
**Cadence:** 2  
**Executable intent:** `assess_network_trust` only  
**Demo UI:** Home + Explore + Rocket Bank live run  

Cadence 3 adds High Flight `ensure_baggage_connection`. Cadence 4 is not started.

---

## 1. Exact runtime request

```json
POST /intents
{
  "intent": "assess_network_trust",
  "subject": {
    "transactionId": "RB-78421",
    "phoneNumber": "+1••••••0198"
  },
  "context": {
    "amount": 25000,
    "currency": "USD"
  }
}
```

Phone number is masked. Configured context is not sent.

---

## 2. Full execution sequence

1. Agent authenticated — Payments Risk Agent acts for Payments Risk  
2. Intent received  
3. Context resolved from onboarding  
4. Agent authorization checked (`allowedIntents`)  
5. Purpose resolved from configuration: **Fraud Prevention / Transaction Security**  
6. Intent → use case: high-value transaction protection  
7. Capabilities resolved from the Cadence 0.2 graph  
8. Capabilities → AX_ACTIVE_CATALOG operationIds  
9. Telco Finder: masked MSISDN → **Network Provider A**  
10. API Finder: available APIs on that network  
11. Route: **DIRECT** NetAware → Network Provider A  
12. Plan created (minimum sufficient evidence)  
13. Selective invocation  
14. Location **BLOCKED_BY_POLICY** → continue/replan  
15. Number recycling **NOT_REQUIRED**  
16. Evidence combined  
17. Autonomy: recommend STEP_UP; decline not authorized  
18. Business outcome returned  

---

## 3. Candidate APIs / capabilities

Mapped from configuration:

| Capability | Role | Catalog family | Primary operationId |
|------------|------|----------------|---------------------|
| Number possession | required | Number Verification | `phoneNumberVerify` |
| SIM continuity | required | SIM Swap | `checkSimSwap` |
| Device continuity | required | Device Swap | `checkDeviceSwap` |
| Device identifier | required | Device Identifier | `retrieveIdentifier` |
| Roaming status | required | Roaming Status | `getRoamingStatus` |
| Number recycling | considered | Number Recycling | `checkNumberRecycling` |
| Location verification | considered | Location | `verifyLocation` |

QoD is **not mapped** to this intent; shown as NOT_REQUIRED / not relevant.

---

## 4. Invoked APIs

| operationId | Family | Maturity | HTTP | Evidence |
|-------------|--------|----------|------|----------|
| `phoneNumberVerify` | Number Verification | incubating | 200 | NUMBER_POSSESSION verified |
| `checkSimSwap` | SIM Swap | incubating | 200 | SIM_CONTINUITY disrupted, 4 hours |
| `checkDeviceSwap` | Device Swap | incubating | 200 | DEVICE_CONTINUITY new_device |
| `retrieveIdentifier` | Device Identifier | **experimental** | 200 | DEVICE_IDENTITY changed |
| `getRoamingStatus` | Roaming Status | incubating | 200 | ROAMING false |

All operationIds are from AX_ACTIVE_CATALOG. Route: DIRECT to Network Provider A.

---

## 5. Considered / not required

- **Number Recycling** (`checkNumberRecycling`) — mapped as considered; not invoked (API economy).  
- **Quality on Demand** (`createSession`) — not relevant to transaction trust.

---

## 6. Blocked APIs

**Location Verification** (`verifyLocation`)

- Relevant: yes  
- Available: yes  
- Subscribed: yes  
- Purpose: permitted  
- Consent: required, **not available**  
- Result: **BLOCKED_BY_POLICY** (configured demo policy, not a universal legal rule)  
- Not invoked. NetAware continues with other evidence.

---

## 7. Telco Finder

Needed because the subject is a phone number.

Result: **Network Provider A** (simulated home network, region CA).

---

## 8. API Finder

After capabilities are known, Finder lists available operation/provider pairs on Network Provider A, including SIM Swap, Device Swap, Device Identifier, Location (available, later blocked), Recycling (available, later not required).

Availability is simulated/configured.

---

## 9. Selected route

**DIRECT:** NetAware → Network Provider A  

Not a commercial or hosting claim.

---

## 10. Evidence produced

Only from successful invocations:

- NUMBER_POSSESSION: verified  
- SIM_CONTINUITY: disrupted, changed within 4 hours  
- DEVICE_CONTINUITY: new_device  
- DEVICE_IDENTITY: changed  
- ROAMING: false  

---

## 11. Policy decisions

Three stages, source **CONFIGURED POLICY**:

1. **Actor / Intent** — agent authorized; intent allowed; purpose from configuration  
2. **Capability / API** — subscription, purpose, consent, agreement; location blocked  
3. **Autonomy / Action** — gather ACT; recommend STEP_UP; decline NOT_AUTHORIZED  

---

## 12. Autonomy

| Action | Level |
|--------|-------|
| Gather network evidence | ACT |
| Produce assessment | ACT |
| Recommend step-up | RECOMMEND |
| Decline transaction | NOT_AUTHORIZED |

---

## 13. Final response JSON

```json
{
  "outcome": "STEP_UP",
  "networkTrust": "DISRUPTED",
  "confidence": 0.94,
  "recommendedAction": "ADDITIONAL_VERIFICATION",
  "decisionOwner": "ENTERPRISE",
  "reasonCodes": ["RECENT_SIM_CHANGE", "DEVICE_IDENTITY_CHANGE"],
  "summary": "Network trust disrupted. Require additional verification. Rocket Bank owns the financial decision."
}
```

Not: fraud detected. Not: HTTP 200 as the product result.

---

## 14. Screens / views

All derived from one execution trace (`executionId: ax-rb-trust-001`):

| View | Content |
|------|---------|
| Your World | Existing systems + RUN INTENT |
| Overview | Small request vs configured knowledge, stage, outcome |
| Live Flow | Who called whom (agent, NetAware, policy, finders, provider) |
| Decisions | INVOKED / BLOCKED_BY_POLICY / NOT_REQUIRED |
| APIs | Real operationIds, maturity, route, simulated response |
| Policy | Three governance stages |

Controls: Run Intent, Replay, Reset. Animation timing is deterministic (`beats[].tMs`).

---

## 15. Tests

```powershell
python backend/scripts/validate_ax_cadence0.py
python backend/scripts/validate_ax_cadence1.py
python backend/scripts/validate_ax_cadence2.py
```

Cadence 0 catalog/graph checks remain. Cadence 1 Explore remains. Cadence 2 covers POST /intents, authorization, purpose source, catalog-backed operationIds, finders, route, selective invoke, consent block, evidence, STEP_UP, autonomy, replay.

Meta_Demo unchanged. Jigyasa untouched.

---

## 16. Known gaps

- Only one executable intent  
- Simulation, not live operators  
- No streaming/step API (full trace returned; UI animates beats)  
- Identity/delegation still `simulated_placeholder`  
- No Cadence 3 airline consent-replan as a second live scenario  
- High Flight / Acme Your World pages remain configuration-only  

---

**STOP.** Do not start Cadence 3 until explicitly approved.
