# AX Cadence 7 — Model alignment

**Status:** Complete  
**Model cadence:** 7  
**Live demo baseline:** `0.6.1-ax6.1` (unchanged)  
**Product behavior:** Frozen. No Discovery UI, no NV/OTA/High Flight live rewrite, no SalesScenarioProfile loader, no Basic/Advanced lens.

Do **not** start Cadence 8 until explicitly approved.

---

## 1. NV model correction

NV1 and NV2 are **authentication / fulfillment paths**, not CAMARA operations and not catalog families.

| Path | Meaning |
| --- | --- |
| `NV1_NETWORK_BASED` | Network-based Number Verification. Typical access: cellular. |
| `NV2_OPERATOR_TOKEN` | SIM-based / TS.43 Operator Token. Wi-Fi capable. Requires operator ECS. |

Number Verification remains **one** `AX_ACTIVE_CATALOG` family. `productLabel: NV1/NV2` removed from operations.

Encoded in `data/model/nv-paths.yaml` and catalog metadata.

## 2. Operation vs path distinction

| Axis | Values | Selected by |
| --- | --- | --- |
| Path | NV1_NETWORK_BASED, NV2_OPERATOR_TOKEN | Access type + operator NV support + ECS + TS.43 prerequisites |
| Operation | `phoneNumberVerify`, `phoneNumberShare` | Claim shape |

Typical operation selection (not live):

- Claimed MSISDN present → `phoneNumberVerify`
- Network-bound MSISDN needed → `phoneNumberShare`

Do **not** claim NV1 = verify or NV2 = share. Cadence 0 `phoneNumberShare` NEEDS_REVIEW alias is closed: share is SOURCE_BACKED as an operation.

## 3. Operator / ECS readiness model

`data/model/operator-readiness.yaml`

- Access type: `CELLULAR | WIFI | VPN | UNKNOWN` from **RUNTIME_CLIENT_CONTEXT** (not Telco Finder).
- Operator: `nv1Supported`, `nv2Supported`.
- ECS: operator infrastructure, states `AVAILABLE | UNAVAILABLE | UNKNOWN`, source `CONFIGURED_OPERATOR_READINESS`.
- Device/runtime fields reserved: `ts43.clientAvailable`, `simAvailable`, `operatorTokenAvailable` / `tokenPathState`.
- Future eligibility documented (cellular→NV1; Wi-Fi+ECS→NV2; Wi-Fi+ECS down→`ENTITLEMENT_SERVER_UNAVAILABLE`).
- No fake NV1 on Wi-Fi. No SMS OTP AX fallback.
- No live discovery in this cadence.

## 4. DPV migration table

Internal AX `purpose.id` kept as the runtime key. Each purpose now has validated `dpv.*` fields. Context is scenario-specific, not a new DPV term.

| AX purpose | DPV 2.3 | TMF931 overlap | Notes |
| --- | --- | --- | --- |
| `payment_fraud_assist` | `dpv:FraudPreventionAndDetection` | Yes | Rocket Bank trust |
| `identity_continuity_assist` | `dpv:IdentityVerification` | Yes | Recovery |
| `kyc_attribute_match` | `dpv:IdentityVerification` | Yes | **NEEDS_REVIEW** — no KYC-specific DPV term |
| `baggage_connection_assurance` | `dpv:RequestedServiceProvision` | Yes | **NEEDS_REVIEW** — no baggage term; replacement purpose separate |
| `presence_assurance` | `dpv:ServiceProvision` | Yes | **NEEDS_REVIEW** — no geofence/presence term |
| `inspection_video_assurance` | `dpv:ServiceOptimisation` | Yes | Acme |
| `pharmacy_age_eligibility` | `dpv:AgeVerification` | Yes | CityCare |
| `experience_assurance` | `dpv:ServiceOptimisation` | Yes | Explorer QoD-style |
| `age_assertion` | `dpv:AgeVerification` | Yes | Explorer retail |
| Future NV (not live) | `dpv:IdentityAuthentication` | Yes | In nv-paths / C9 |
| Future OTA (not live) | `dpv:ImproveExistingProductsAndServices` | Yes | `ota-device-fleet.yaml` |
| Future ramp-scanner (not live) | `dpv:FulfilmentOfContractualObligation` | Yes | **NEEDS_REVIEW** vs ServiceOptimisation |

Allowlist: `data/schemas/dpv-purpose-allowlist.yaml`. No invented IDs. `dpv:ServiceMonitoring` (2.3-only) not used.

## 5. TMF931 alignment table

`data/model/tmf931-alignment.yaml` — TMF931 is onboarding/order, **not** TMF921.

| Field | Classification |
| --- | --- |
| Enterprise / Application Owner | TMF931_DIRECT |
| Application | TMF931_DIRECT |
| API Product / catalog family | TMF931_DIRECT |
| Subscription / API product order | TMF931_DIRECT |
| Scope | TMF931_DIRECT |
| Purpose | TMF931_DIRECT |
| Legal basis | TMF931_DIRECT |
| Terms / agreement | TMF931_DIRECT |
| Security / grant type | TMF931_DIRECT |
| Region | TMF931_INSPIRED |
| Provider / operator | TMF931_INSPIRED |
| Entitlement | TMF931_INSPIRED |
| Agent | AX_SPECIFIC |
| Intent | AX_SPECIFIC |
| Autonomy | AX_SPECIFIC |
| Capability discovery | AX_SPECIFIC |
| Telco Finder | NETAWARE_SPECIFIC |
| API Finder | NETAWARE_SPECIFIC |
| Evidence / replan | AX_SPECIFIC |
| Access type | RUNTIME_DISCOVERED |
| ECS readiness | RUNTIME_DISCOVERED (demo: configured) |
| NV path | AX_SPECIFIC |
| Sales scenario profile | AX_SPECIFIC |

Agent, Intent, Autonomy, Evidence, Replan are **not** forced into TMF931.

## 6. Subscription vs entitlement correction

Subscription = API product ordered. Entitlement = this application/agent may invoke.

- `subscriptions.yaml` and `entitlements.yaml` are separate.
- Entitlements now carry `enterpriseId`, `applicationId`, `agentId`, and `capabilityFamily` or `capabilityId`.
- Data migrated 1:1 from the previous implicit “subscribed ⇒ entitled” surface so **hero outcomes do not change**.
- Runtime `evaluate_capability_policy` reports them separately and can return `NOT_ENTITLED`.
- Canonical filters: `NOT_SUBSCRIBED`, `NOT_ENTITLED`.

## 7. Discovery-stage model

`data/model/discovery.yaml` — enums only, no UI, no emitter.

- CANDIDATE_GENERATION: catalog, intent mapping, subject/claim type
- CONFIGURED_ELIGIBILITY: agent auth, DPV purpose, policy, DPA, consent, subscription, entitlement
- RUNTIME_FEASIBILITY: region, Telco Finder, API Finder, route, access type, operator/technical prerequisites, evidence, autonomy, usefulness
- SELECT: rank, minimum sufficient, selected

Not every stage runs for every scenario.

## 8. Filter / reason-code enum

`NOT_RELEVANT` · `PURPOSE_NOT_PERMITTED` · `NOT_SUBSCRIBED` · `NOT_ENTITLED` · `CONSENT_MISSING` · `AGREEMENT_GAP` · `REGION_NOT_SUPPORTED` · `PROVIDER_NOT_AVAILABLE` · `OPERATOR_NOT_SUPPORTED` · `ENTITLEMENT_SERVER_UNAVAILABLE` · `ACCESS_TYPE_INCOMPATIBLE` · `TECHNICAL_PREREQUISITE_MISSING` · `EVIDENCE_REUSED` · `NOT_REQUIRED` · `AUTONOMY_FORBIDS` · `SELECTED`

Live traces still use existing states (`PURPOSE_DENIED`, `BLOCKED_BY_POLICY`, …) so Cadence 6.1 presentation is unchanged.

## 9. Existing NetAware vs AX extension map

`data/model/product-alignment.yaml`

**Existing NetAware assets:** onboarding, application, API catalog, subscriptions, policy, security, Telco Finder, API Finder, provider routing, invocation, observability.

**AX extensions:** Intent, agent authorization, capability discovery, autonomy, evidence reuse, plan/replan/verify.

**Customer line:** AX does not replace the catalog, onboarding, subscriptions, Telco Finder, API Finder, routing, or invocation. It decides whether, which, where, and why those assets are used for an Intent.

## 10. High Flight replacement model

`data/model/high-flight-replacement.yaml` — **not executable**.

- Current `ensure_baggage_connection` / baggage-connection: **DEMOTE** (still the live hero until Cadence 11).
- Proposed: ramp-scanner / connected ground-handling assurance.
- Device: ruggedized BRS handheld. Network unique: DATA reachability / roaming / connectivity. **Not** bag location.
- Business actions: swap device, reassign handler, hold/proceed load-close.
- **NEEDS_REVIEW:** Intent ID (`assure_ramp_scan_capability` working), DPV purpose (`FulfilmentOfContractualObligation` vs `ServiceOptimisation`), subject model (bag as domain context beside scanner).

## 11. OTA model

`data/model/ota-device-fleet.yaml` — **not executable**.

- Intent: `rollout_firmware_safely`
- Enterprise already has inventory, twin, firmware, campaign manager, telemetry.
- Network adds Reachability, Roaming, optionally Connectivity.
- QoD / Location / Edge **NOT_REQUIRED** by default.
- Agentic shape: DISCOVER → SEGMENT → PLAN COHORT → ENTERPRISE OTA ACTION → OBSERVE → REPLAN → VERIFY.
- Network does **not** flash firmware. Domain ops: `listDevices`, `getDevice`, `getTwin`, `getPackage`, `createCampaign`, `startWave`, `getCampaignStats`, `latestCheckIn`.
- Application `acme-device-fleet` is **not** created in this cadence.

## 12. SalesScenarioProfile schema

- Schema: `data/schemas/sales-scenario-profile.json`
- Example (not loaded): `data/profiles/examples/operator-cto-de-ota.yaml`
- Runtime does **not** load `data/profiles/`.
- Profiles may only select/label existing model objects. Unknown refs fail closed in Cadence 11.

## 13. Catalog unchanged confirmation

- 13 business families.
- No Connected Network Type, ECS API, OTP SMS, Reachability Subscriptions, eSIM/FOTA.
- Catalog edits limited to NV path ≠ operation metadata.

## 14. Regression tests

```powershell
cd backend
python scripts/validate_ax_cadence7.py
```

Cadence 7 validator checks the model, live hero outcomes, and runs Cadence 0 + 6.1 regression (6.1 includes Cadence 6).

Live outcomes required:

| Intent | Outcome |
| --- | --- |
| `assess_network_trust` | STEP_UP |
| `ensure_baggage_connection` | AT_RISK |
| `maintain_inspection_experience` | ASSURED |
| `verify_pharmacy_age_gate` | ELIGIBLE |
| `assess_recovery_continuity` | CONTINUITY_ALIGNED |

## 15. NEEDS_REVIEW items

1. High Flight replacement Intent ID (`assure_ramp_scan_capability`).
2. High Flight replacement DPV (`FulfilmentOfContractualObligation` vs `ServiceOptimisation` vs `RequestedServiceProvision`).
3. High Flight subject model: bag as domain context vs scanner as network subject.
4. `kyc_attribute_match` → `IdentityVerification` (no KYC DPV term).
5. `presence_assurance` / current `baggage_connection_assurance` broader DPV parents.
6. OTA default industry label (plant vs automotive) — Sales profile, Cadence 10/11.
7. CIBA vs JWT-bearer presentation depth for NV2 (Cadence 9).
8. Whether Device Reachability Subscriptions should be admitted later for OTA observe (not now).
9. Live trace still uses `PURPOSE_DENIED` rather than discovery code `PURPOSE_NOT_PERMITTED` (alias in Cadence 8).

---

## Explicitly not included

Discovery UI · Basic/Advanced · NV live · OTA live · High Flight rewrite · Sales profile loader · catalog expansion · SMS OTP · LLM.

**STOP. Do not start Cadence 8.**
