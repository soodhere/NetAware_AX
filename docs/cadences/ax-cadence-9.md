# AX Cadence 9 — Number Verification path selection

**Status:** Complete  
**UI cadence:** 9  
**Model cadence:** 7 (NV path model now executed; catalog unchanged)  
**Live demo baseline:** `0.6.1-ax6.1` (unchanged)  
**Product behavior:** Frozen live outcomes for Rocket Bank trust, Acme, CityCare, High Flight, and evidence reuse.

**STOP. Do not start Cadence 10.** No OTA, fleet visualization, Demand Map, Meeting Mode, SalesScenarioProfile loader, High Flight rewrite, real TS.43, real OIDC/CIBA, or revenue.

---

## 1. Number Verification business story

Rocket Bank **Digital Identity / IAM** is an adjacent application to Payments Risk.

- Business event: **customer signing in**
- Intent: **verify this mobile number** (`verify_mobile_number`)
- The application does **not** request NV1, NV2, TS.43, ECS, operator token, or a CAMARA `operationId`
- NetAware discovers the feasible fulfillment from access type, operator, API availability, NV path support, Entitlement Server readiness, and technical prerequisites

Payments Risk continues to use `assess_network_trust`. Catalog reuse: one enterprise, two use cases.

## 2. Three scenario variants

One runner (`backend/app/nv_runtime.py`), one application (`rocket-bank-iam`), one agent, one Intent. Deterministic seeds:

| Control | Access | Provider | Path | Outcome |
| --- | --- | --- | --- | --- |
| CELLULAR | CELLULAR | Network Provider A | `NV1_NETWORK_BASED` | VERIFIED |
| WI-FI — READY | WIFI | Network Provider A | `NV2_OPERATOR_TOKEN` | VERIFIED |
| WI-FI — ECS GAP | WIFI | Network Provider B | none | CAPABILITY_UNAVAILABLE |

## 3. Same-Intent visual behavior

Runtime page `rocket-bank/passwordless-mobile-sign-in` pins **Verify this mobile number** at the top. The ACCESS / PROVIDER SCENARIO control re-runs the **same Intent** with a different seed. Lens switch still does not rerun.

## 4. NV1 selection

Cellular + operator NV1 support → simplest feasible path `NV1_NETWORK_BASED`. NV2 may be available and is marked `NOT_REQUIRED`. ECS is not required. Claimed MSISDN → `phoneNumberVerify`.

## 5. NV2 selection

Wi-Fi filters NV1 with `ACCESS_TYPE_INCOMPATIBLE`. NV2 is supported, Entitlement Server AVAILABLE, TS.43 client and SIM available → `NV2_OPERATOR_TOKEN`. Operation remains `phoneNumberVerify` because the claimed number is present. Share is not NV2.

## 6. ECS failure behavior

Wi-Fi + Provider B: Number Verification API **available**, NV2 in the product profile, Entitlement Server **UNAVAILABLE** → `ENTITLEMENT_SERVER_UNAVAILABLE`. No fake NV1 over Wi-Fi. No SMS OTP. Outcome `CAPABILITY_UNAVAILABLE`. Enterprise owns any alternate IAM path.

## 7. Path vs operation distinction

Advanced explains two dimensions:

- **Fulfillment path** — how the subscriber is authenticated / bound (`NV1_NETWORK_BASED` or `NV2_OPERATOR_TOKEN`)
- **CAMARA operation** — what Number Verification is asked to do (`phoneNumberVerify` or `phoneNumberShare`)

Do not label verify = NV1 or share = NV2.

## 8. Discovery visualization

Cadence 8 grammar, NV Basic story:

1. Business need — verify customer's mobile number  
2. What network could add — silent number possession verification  
3. Eligible — permitted / subscribed / entitled  
4. Deliverable now — access type, operator, NV availability, NV path, operator readiness  
5. Selected — NV1 or NV2 or UNAVAILABLE  

OIDC/CIBA stays out of Basic. Path cards and the ECS break node carry the sales picture.

## 9. Telco Finder contribution

MSISDN → Telco Finder → Network Provider A or B. Answers **which operator applies**. Does **not** determine Wi-Fi vs cellular. Access type is `RUNTIME_CLIENT_CONTEXT` (labelled SIMULATED ACCESS CONTEXT).

## 10. API Finder contribution

Answers **does this provider offer Number Verification?** Kept separate from NV1/NV2 path support and ECS readiness.

## 11. Operator readiness visualization

Configured operator readiness (not a CAMARA ECS API). ECS AVAILABLE vs UNAVAILABLE is a visible node on the NV2 path. Wi-Fi ECS gap breaks the path toward CAPABILITY UNAVAILABLE.

## 12. Enterprise Value panel

"My application asked to verify a number. I did not code separate cellular and Wi-Fi Network API flows. NetAware selected the feasible network path."

## 13. Network Opportunity panel

After the result, compact supply-side view (not the full stakeholder lens):

- Success: qualified YES, fulfilled YES, path NV1 or NV2, 1 Number Verification invocation  
- ECS failure: qualified YES, NV API available, fulfilled NO, blocking gap Entitlement Server unavailable, **unfulfilled qualified demand**  

No revenue. No “lost revenue.”

## 14. Basic UI

Pinned Intent, three-variant selector, path flow, NV1/NV2 cards, finder strip, outcome, Network Opportunity, scenario close. Default lens remains BASIC.

## 15. Advanced UI

Activates previously empty columns: access type, operator NV1/NV2 support, Entitlement Server, TS.43 client, SIM, token path, path result, operation result. Compact conceptual NV2 chain labelled SIMULATED / CONCEPTUAL PATH.

## 16. Tests

`backend/scripts/validate_ax_cadence9.py` covers the Cadence 9 contract and runs Cadence 8 (which includes 0–7).

## 17. Known realism gaps

- Access type is a simulated client-context seed, not detected from the radio  
- ECS readiness is configured operator data, not a standardized CAMARA discovery API  
- TS.43 token acquisition, CIBA, and JWT bearer exchange are conceptual  
- Operator responses are simulated  
- No live provider calls  

Honesty labels: SIMULATED ACCESS CONTEXT · CONFIGURED OPERATOR READINESS · SIMULATED OPERATOR RESPONSE.

## 18. Cadence 10+ not started

OTA, fleet visualization, Demand Map, full Enterprise/Operator/Aggregator lens, SalesScenarioProfile loader, Meeting Mode, and High Flight rewrite were **not** started.

---

**STOP. Do not start Cadence 10.**
