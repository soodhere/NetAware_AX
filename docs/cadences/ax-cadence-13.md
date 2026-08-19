# Cadence 13 — Fulfillment Coverage Explorer

Status: complete. Cadence 14 not started.

Cadence 12 answers what Network APIs could do for an enterprise application. Cadence 13 answers whether NetAware can actually fulfill the Intent in this region, for this application, through available operator/aggregator supply. This is **fulfillment truth**, not Demand Map, pricing, TAM, or commercial ranking.

Live product version remains `0.6.1-ax6.1`. Model cadence remains 7. UI cadence is **13**.

## 1. Fulfillment model

Derived, not a parallel engine. Records are assembled in `backend/app/fulfillment.py` from Cadence 8 discovery/policy evaluation, Cadence 9 NV path / ECS readiness, Cadence 10 Intent Profiles, Cadence 11 OTA provider cohorts, Cadence 12 portfolio regions/providers/routes, plus existing subscriptions, entitlements, consent, providers, and routes.

Visual chain: ENTERPRISE → APPLICATION → INTENT → REQUIRED / OPTIONAL CAPABILITIES → GOVERNANCE ELIGIBILITY → REGION → NETWORK / OPERATOR → API AVAILABILITY → OPERATOR READINESS / PREREQUISITES → PROVIDER / ROUTE → FULFILLMENT.

## 2. Fulfillment states

`FULFILLABLE` · `FULFILLABLE_WITH_REDUCED_EVIDENCE` · `PARTIALLY_FULFILLABLE` · `BLOCKED` · `NOT_AVAILABLE` · `NOT_CONFIGURED` · `NOT_APPLICABLE`.

Failures are not collapsed into “unavailable.” EXPLORE scenarios without supply configuration are `NOT_CONFIGURED`, not `BLOCKED`.

## 3. Blocking-gap taxonomy

Reuses Cadence 7/8/9 reason codes rather than inventing duplicates: `API_NOT_AVAILABLE`, `NOT_SUBSCRIBED`, `NOT_ENTITLED`, `PURPOSE_NOT_PERMITTED`, `CONSENT_MISSING`, `AGREEMENT_GAP`, `OPERATOR_READINESS`, `ENTITLEMENT_SERVER_UNAVAILABLE`, `ACCESS_PATH_UNSUPPORTED`, `ROUTE_UNAVAILABLE`, `REGION_NOT_SUPPORTED`, `CAPABILITY_GAP`.

## 4. Minimum sufficient capability model

Intent Profiles distinguish REQUIRED / OPTIONAL / CONDITIONAL. An Intent is fulfillable when the configured **minimum sufficient set** (profile `minimumEvidence`, plus OTA campaign-required roaming where configured) can be satisfied. Optional/considered gaps do not automatically block (Rocket Bank / MegaMart location; High Flight QoD/Location).

## 5. Enterprise / demand entry

`/coverage` and `/coverage/enterprises/{id}`. Flow: enterprise → application → intent → region → fulfillment. Example: Rocket Bank Digital Identity `verify_mobile_number` Canada is fulfillable; Wi-Fi / Provider B is blocked by Entitlement Server readiness.

## 6. Network / supply entry

`/coverage/providers/{id}`. Flow: region → provider → available/ready capabilities → intents → applications → industries. Not ranked. Not Demand Map.

## 7. Coverage summary

Derived counts, not hardcoded. 17 sales-visible use cases; 13 with configured fulfillment coverage; remaining EXPLORE rows are unknown/not configured. Fully fulfillable / partial / blocked / not available / unknown come from evaluated records.

## 8. Application / region coverage

Compact matrix for Canada / Germany / Singapore. Cells are derived. Missing operator configuration is `NOT_CONFIGURED` (not blocked). Click a cell for WHY.

## 9. Provider coverage

Network Provider A / B and Network Provider C (specialist) shown with advertised operations, enabled intents, and gaps. Fictional names only.

## 10. Aggregator coverage

Aggregator A shows normalized capabilities and routed regions. Explicit note: it does **not** own the operator APIs it routes to.

## 11. NV1 / NV2 fulfillment example

One business Intent `verify_mobile_number`:

- Cellular / Provider A — API available, NV1 supported → `FULFILLABLE`, path `NV1_NETWORK_BASED`
- Wi-Fi / Provider A — API available, NV2 supported, ECS available → `FULFILLABLE`, path `NV2_OPERATOR_TOKEN`
- Wi-Fi / Provider B — API available, NV2 supported, ECS unavailable → `BLOCKED`, `ENTITLEMENT_SERVER_UNAVAILABLE`

The application does not select NV1 vs NV2.

## 12. Entitlement Server readiness

First-class **OPERATOR PREREQUISITE / CONFIGURED OPERATOR READINESS**. Not a CAMARA API. NetAware does not control the operator Entitlement Server.

## 13. OTA Provider C gap

Reachability available; Roaming Status unavailable. Campaign policy still requires roaming evidence → `PARTIALLY_FULFILLABLE` with `CAPABILITY_GAP`, affected cohort 500 simulated devices, qualified demand present, **no revenue**.

## 14. High Flight fulfillment-success distinction

Required Device Reachability is available, routed, and permitted → `FULFILLABLE`. Runtime may still return DEVICE NOT DATA REACHABLE. That is a business outcome, not a supply failure. Fulfillment asks whether NetAware could obtain the evidence; business outcome asks what the evidence meant.

## 15. Policy / consent blocking

MegaMart/Rocket Bank/High Flight location: API can be available while consent is missing (`CONSENT_MISSING`) without blocking the Intent when location is optional. Pharmacy KYC Match is `PURPOSE_NOT_PERMITTED` while age verification remains the minimum sufficient set.

## 16. Telco Finder role

Which network/operator applies to this subject?

## 17. API Finder role

Which candidate Network API operations are available through which providers?

## 18. Fulfillment Coverage role

Given the Intent, governance, required capabilities, operator readiness and routes, can the business need actually be fulfilled?

These three questions are labelled separately in Technical View.

## 19. Route Explorer

Capability → available providers → DIRECT / AGGREGATED / HYBRID → readiness → selected fulfillment path. Connects to API Finder / catalog.

## 20. Reverse provider traversal

From Network Provider A: capabilities → intents enabled → applications → industries (High Flight, OTA, SwiftShip, field operations, and other configured rows). No value ranking.

## 21. Qualified demand treatment

A legitimate enterprise Intent requires a network capability. OTA Provider C shows 500-device unfulfilled roaming demand. It does **not** mean revenue.

## 22. Provenance

Coverage facts cite ONBOARDING, CONFIGURATION, RUNTIME, SIMULATED PROVIDER DATA, INTENT PROFILE, CONFIGURED POLICY, CONFIGURED_OPERATOR_READINESS, or DERIVED.

## 23. Sales View

Answers in seconds: can we support this customer, where, through whom, which capabilities, what is missing, and whether the gap is policy, commercial, API availability, or operator readiness.

## 24. Technical View

Intent Profile, DPV purpose, minimum set, subscription/entitlement, policy, consent, Telco Finder, API Finder, operationId, operator readiness, route, blocking reason, provenance. Not dumped at once.

## 25. Portfolio integration

Every C12 scenario card and briefing has **See Fulfillment Coverage**. Coverage has **Back to business story**.

## 26. Catalog integration

API family pages expose **Where is this available?** and **Which intents depend on it?**

## 27. Regression tests

`backend/scripts/validate_ax_cadence13.py` nests Cadence 0–12, freezes live outcomes, preserves the 17-use-case portfolio and 13-family catalog, and asserts NV / ECS / OTA / High Flight / consent / provenance / route distinctions.

## 28. Known gaps

- Coverage is a prototype model, not a live operator SLA, health check, production certification, or commercial launch claim.
- EXPLORE rows (telehealth, Harbor equipment, BuildRight, KYC Match) are honestly `NOT_CONFIGURED`.
- Rocket Bank Germany / Singapore cells are `NOT_CONFIGURED` because operator availability is not configured there.
- SwiftShip Singapore is configured `NOT_AVAILABLE` (reachability not offered), which is different from unknown.
- No Demand Map, revenue, pricing, TAM, Meeting Mode, or Cadence 14 commercial ranking.

**STOP. Do not start Cadence 14.**
