# Cadence 12 — Sales portfolio breadth + config-driven GUIDED scenarios

Status: complete. Cadence 13 not started.

NetAware AX is now a **sales portfolio**: 17 visible use cases across 10 industries, with LIVE heroes preserved, a shared GUIDED interpreter, and EXPLORE opportunities that are not fake executions.

## 1. Total visible use cases

**17** (inside the 15–20 target). Quality over quota — 18 was not forced.

## 2. Industries covered

Financial Services, Retail / Commerce, Insurance, Airlines / Airports, Manufacturing, Logistics / Delivery, Healthcare, Media / Broadcast, Smart Buildings / Facilities, Field Service / Construction.

## 3. Commercial motions

Identity & Trust, Connected Operations, Device & Fleet Operations, Customer Experience, Location & Presence (secondary on field / construction), Network Assurance.

Organized by **business motion and industry**, not by CAMARA API name.

## 4. LIVE scenarios (7 + recovery companion)

| Enterprise | Application | Intent | Outcome |
|---|---|---|---|
| Rocket Bank | Payments Risk | `assess_network_trust` | `STEP_UP` |
| Rocket Bank | Digital Identity / IAM | `verify_mobile_number` | `VERIFIED` |
| Rocket Bank | Payments (companion) | `assess_recovery_continuity` | `CONTINUITY_ALIGNED` |
| High Flight | Baggage Operations | `ensure_baggage_connection` | `CONTINUE` / `SWAP_DEVICE` |
| Acme | Quality Inspection | `maintain_inspection_experience` | `ASSURED` |
| Acme | Connected Device Operations | `prepare_ota_cohort` | `NETWORK_QUALIFIED_COHORT` |
| CityCare | Pharmacy Eligibility | `verify_pharmacy_age_gate` | `ELIGIBLE` |

Approved live behavior is regression-protected. Featured `/demo` hero order is unchanged.

## 5. GUIDED scenarios (6)

All execute through `backend/app/guided_runtime.py` from `data/guided/scenarios.yaml`.

| Enterprise | Application | Intent | Complexity | AX behavior |
|---|---|---|---|---|
| SwiftShip Logistics | Delivery Operations | `assure_delivery_device` | BASIC | selection |
| MegaMart | Checkout Risk | `assess_checkout_trust` | COMPOSED | filtering |
| Northstar Insurance | Claims | `assess_claim_device_trust` | COMPOSED | aggregator normalization |
| High Flight | Ground Operations | `assure_ground_device` | COMPOSED | bounded action |
| Acme | Field Maintenance | `assure_technician_device` | BASIC | skip unneeded QoD |
| Apex Media | Live Contribution | `assure_live_broadcast` | COMPOSED | QoD because an SLO exists |

## 6. EXPLORE scenarios (4)

| Enterprise | Application | Intent | Note |
|---|---|---|---|
| CityCare | Telehealth | `maintain_telehealth_experience` | QoD only if an SLO exists. No medical claims. |
| Harbor Facilities | Building Operations | `assure_building_equipment` | Reachability opportunity. |
| BuildRight | Field Operations | `maintain_site_uplink` | Field connectivity. Not fake execution. |
| Rocket Bank | Digital Onboarding | `match_customer_kyc` | Privacy / DPA / consent bound. |

EXPLORE is labelled and is **not** presented as LIVE.

## 7. Scenarios rejected and why

| Candidate | Why |
|---|---|
| Locate baggage | C10 demoted. Network Location is not bag tracking. LOW sales clarity. |
| Stadium / venue | LOW network uniqueness vs inspection / contribution SLO stories. |
| Claim location | Surveillance-adjacent. Location Verification is not fraud proof. |
| Retail age-gate | Duplicates CityCare pharmacy age. |
| Dock-scan session | Duplicates manufacturing inspection QoD. |
| Shipment custody geofence | Weaker Decision Gap than delivery-device readiness. |
| KYC Match as LIVE | Kept EXPLORE. Do not fake fulfillment. |

## 8. Guided interpreter architecture

```
Existing LIVE runners
        +
Shared GUIDED interpreter  (guided_runtime.py)
        +
EXPLORE mappings
```

The interpreter consumes configuration: scenario, enterprise, application, Intent, existing systems, business event, Decision Gap, candidate capabilities, policy, provider / route, simulated evidence, selection rules, outcome rules, autonomy, close.

Deterministic. No LLM. No MCP. No generic autonomous planner. Cadence 10 `interpreter_spike.py` remains parallel and is **not** wired into `execute_intent`.

## 9. SwiftShip scenario

Fictional enterprise **SwiftShip Logistics**, application **Delivery Operations**.

Already have: dispatch, route, delivery workflow, driver assignment, proof-of-delivery.

Decision: can the assigned handheld complete the digital delivery workflow?

Gap: dispatch does not independently know DATA reachability.

Network adds: Device Reachability (`getReachabilityStatus`).

Outcomes from YAML variants: `CONTINUE` or `SWAP_DEVICE`.

No `run_swiftship_delivery()`.

## 10. SwiftShip trace

BUSINESS EVENT → INTENT → CONFIGURED / ONBOARDED CONTEXT → CANDIDATE GENERATION → POLICY / ENTITLEMENT / PURPOSE → TELCO FINDER → API FINDER → PROVIDER / ROUTE (DIRECT in CA) → SELECTED Reachability → SIMULATED EVIDENCE → CONTINUE or SWAP_DEVICE.

Discovery grammar is the shared CALL / SKIP / FILTER model. QoD is SKIP (no delivery SLO).

## 11. Decision Gap coverage

Every visible row states what the enterprise already has, the business decision, the Network Decision Gap, and what the network uniquely adds. Forced API tourism was excluded.

## 12. Application-first coverage

Hierarchy is Enterprise → Application → Business event → Intent → Decision Gap → capability discovery → Network API.

Examples: Rocket Bank Payments Risk / IAM; Acme Quality Inspection / Device Fleet / Field Maintenance; High Flight Baggage vs Ground Operations; MegaMart Checkout Risk; CityCare Pharmacy vs Telehealth.

## 13. Capability / API leverage

**13 API families → business capabilities → multiple intents → multiple applications → multiple industries.**

The sales surface states this explicitly. It does not market “hundreds of APIs.”

## 14. Reverse API-to-use-case traversal

“Where could I sell this?” for Device Reachability, SIM continuity, and QoD.

Reachability: High Flight ramp, Acme OTA, SwiftShip delivery, ground device, technician device, Harbor equipment, field ops.

SIM continuity: Rocket Bank trust / recovery, MegaMart checkout, Northstar claims.

QoD: Acme inspection, Apex contribution, telehealth / field where an SLO is genuine.

Not a Demand Map.

## 15. Regional / provider model

Portfolio rows carry region, availability, route, subscription, entitlement, fulfillmentStatus, blockingGap.

SwiftShip example: Canada DIRECT, Germany AGGREGATED, Singapore readiness gap. Not every scenario is multi-region.

## 16. Aggregator representation

Northstar Claims: Enterprise → NetAware → Aggregator A → Network Provider B.

SwiftShip / MegaMart: Enterprise → NetAware → Network Provider.

NetAware normalizes intent/capability across heterogeneous routes. It is not implied to be the commercial aggregator.

## 17. DPV / TMF onboarding treatment

Business View: human-readable purpose.

Technical View: DPV identifier when validated; `NEEDS_REVIEW` on `delivery_device_assurance` (no dedicated device-operability DPV term).

Configured / onboarded context (enterprise, application, agent, subscriptions, entitlements, allowed intents, purpose, region, policy, agreement, autonomy) is labelled as **not** a runtime request payload.

TMF931 labels appear only where mapped, with AX extensions called out.

## 18. Sales Portfolio UI

`/demo` is a sales portfolio: filters by industry and motion, scenario cards with enterprise / application / problem / gap / contribution / LIVE|GUIDED|EXPLORE / BASIC|COMPOSED|ADVANCED.

Live heroes remain in featured order for regression. Home is unchanged.

## 19. Industry view

Selecting an industry shows applications → use cases → Decision Gaps → network contribution / capabilities.

## 20. Commercial Motion view

Same capability across industries (e.g. Device & Fleet: Acme OTA, High Flight ramp, SwiftShip, Harbor).

## 21. Regression tests

`backend/scripts/validate_ax_cadence12.py` nests Cadence 0–11.

Protects: Rocket Bank trust / NV / recovery, High Flight, Acme inspection, Acme OTA, CityCare, 13-family catalog, live version `0.6.1-ax6.1`, no experimental promotion, no SwiftShip runner, guided Discovery grammar, Meta_Demo / Jigyasa untouched.

## 22. Known gaps

- Location & Presence is a motion overlay, not a dedicated surveillance-like LIVE scenario.
- Telehealth, Harbor, BuildRight, and KYC remain EXPLORE until SLO / consent / onboarding justify execution.
- Singapore SwiftShip readiness gap is metadata for later commercial exploration — not a C13 Demand Map.
- No login, Meeting Mode, or sales-person profiles (intentionally deferred).

**STOP. Cadence 13 not started.**
