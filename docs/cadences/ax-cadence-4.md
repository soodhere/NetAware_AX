# AX Cadence 4 — Closed-loop + Governed Minimization

**Status:** Implemented and validated.  
**Cadence:** 4  
**Executable intents:** four live runs  
**Cadence 5:** not started  

---

## ACME MANUFACTURING

### Runtime request

```json
POST /intents
{
  "intent": "maintain_inspection_experience",
  "subject": { "cameraId": "ACME-CAM-14", "lineId": "LINE-B" },
  "context": { "sloMs": 40 }
}
```

### Configured context

Enterprise, Quality Inspection application, Inspection Experience Agent, plant environment, SLO defaults, subscriptions, QoD ACT authorization, MES/QMS/camera integrations, purpose **Quality assurance** from configured intent profile.

### Plan v1 → breach → Plan v2

**Plan v1:** Observe connectivity → application profile → consider edge → consider QoD → evaluate objective (**SATISFIED**, QoD **NOT_REQUIRED**).

**OBJECTIVE_BREACH:** Latency 78ms exceeds SLO 40ms.

**Plan v2:** Observe degraded state → select QoS profile → create QoD session → post-action observe → verify session.

### APIs invoked

`checkNetworkQuality` (initial + verify), `createApplicationProfile`, `retrieveQoSProfiles`, `createSession`, `getSession`.

### Not invoked

Edge discovery — NOT_REQUIRED. QoD initially NOT_REQUIRED until breach.

### Autonomy

Observe ACT · QoD ACT (no approval) · MES routing NOT_AUTHORIZED.

### Verification

Post-action `checkNetworkQuality` + `getSession` → **PASSED**. Outcome **ASSURED** (HTTP 201 alone is not success).

### Run

`#/demo/acme-manufacturing/critical-inspection-camera/run`

---

## CITYCARE HEALTH

### Runtime request

```json
POST /intents
{
  "intent": "verify_pharmacy_age_gate",
  "subject": { "transactionId": "RX-10442", "phoneNumber": "+1••••••8843" },
  "context": { "ageThreshold": 18 }
}
```

### Configured context

CityCare Health, Pharmacy Eligibility, Pharmacy Eligibility Agent, purpose **Age assertion**, agreement permits age assertion only — broader KYC Match blocked for this intent.

### Capability selection

| Capability | Result |
|------------|--------|
| Age Verification (`verifyAge`) | SELECTED — minimum sufficient |
| KYC Match (`KYC_Match`) | BLOCKED_BY_POLICY — broader than required |

### APIs invoked

`verifyAge` only.

### Final response

`ELIGIBLE`, `ageVerified: true`, `dataUsed: AGE_ASSERTION_ONLY`, `broaderKycUsed: false`. Pharmacist owns dispensing.

### Run

`#/demo/citycare-health/pharmacy-age-gate/run`

---

## Four-scenario comparison

| | Rocket Bank | High Flight | Acme | CityCare |
|---|-------------|-------------|------|----------|
| **AX behavior** | Selective evidence + recommendation | Cross-domain + genuine replan | Closed-loop autonomous action + verify | Governed minimum capability |
| **Intent** | `assess_network_trust` | `ensure_baggage_connection` | `maintain_inspection_experience` | `verify_pharmacy_age_gate` |
| **Domain APIs** | None invoked | Baggage Journey, Flight Status, Ground Ops | None (MES/QMS context from config) | None |
| **Network APIs** | 5 identity/trust ops | Reachability, Connectivity | Insights, Profiles, QoD family | verifyAge only |
| **Policy** | Location blocked | Location blocked | QoD permitted when needed | KYC Match blocked |
| **Autonomy** | RECOMMEND step-up | ACT_WITH_APPROVAL expedite | ACT QoD | ACT assertion; NOT dispense |
| **Replan** | Weak (continue) | Material (ground ops) | Material (QoD after breach) | N/A (selection at plan) |
| **Outcome** | STEP_UP | AT_RISK | ASSURED | ELIGIBLE |

---

## Tests

```powershell
python scripts/validate_ax_cadence4.py   # 28 checks
python scripts/validate_ax_cadence0.py   # 38
python scripts/validate_ax_cadence1.py   # 26
python scripts/validate_ax_cadence2.py   # 30
python scripts/validate_ax_cadence3.py   # 39
```

---

## Known gaps

- Simulated operators and domain context only  
- In-memory execution store  
- CityCare added as fourth featured enterprise; other healthcare intents remain Explore-only  

**STOP.** Cadence 5 not started.
