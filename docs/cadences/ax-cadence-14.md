# Cadence 14 — Demand Map + commercial opportunity

Status: complete. Cadence 15 not started.

Cadence 12 answered *what enterprise problems Network APIs could solve*. Cadence 13 answered *whether NetAware can fulfill those Intents with configured operator / aggregator supply*. Cadence 14 answers:

**Where is qualified demand, what network capability is needed, what can already be fulfilled, and what supply gap would unlock more use cases?**

This is the commercial bridge:

```
ENTERPRISE DEMAND
       ↓
Applications / Business Events
       ↓
     INTENTS
       ↓
 Network Decision Gaps
       ↓
  CAPABILITY DEMAND
       ↓
 NetAware Fulfillment
    ↙          ↘
AVAILABLE       GAP
   ↓             ↓
API INVOCATION  SUPPLY OPPORTUNITY
```

Live version remains `0.6.1-ax6.1`. Model cadence remains 7. UI cadence is **14**. C13 remains the fulfillment source — C14 consumes `public_coverage()` and does not duplicate that engine.

This is **commercial opportunity intelligence**, not financial forecasting. No revenue, ARR, TAM, API price, lost revenue, ROI, or invented customer/transaction volume.

Derived top-level counts (from configured demo data, not hardcoded marketing numbers):

| Measure | Count |
|---|---|
| Visible use cases | 17 |
| Configured applications | 16 |
| Qualified capability demands | 29 |
| Fulfilled | 26 |
| Partially fulfilled | 1 |
| Unfulfilled | 2 |
| Potential (not qualified) | 5 |
| Not required | 30 |
| Regions in configured demo coverage | 4 |
| Providers | 4 |
| Aggregated routes | 10 |

## 1. Demand model

Normalized records in `backend/app/demand.py`. Schema: `data/schemas/demand-record.json`. Overlay: `data/model/demand-map.yaml`.

Conceptual fields: `demandId`, `enterpriseId`, `applicationId`, `useCaseId`, `intentId`, `businessEvent`, `commercialMotion`, `industry`, `region`, `capability`, `requirementType`, `demandState`, `fulfillmentStatus`, `provider`, `providerType`, `route`, `blockingGap`, `affectedUnits`, `affectedUnitsLabel`, `source`, `provenance`, `coverageRecordId`.

No `revenue`, `price`, `ARR`, or `tam` fields.

## 2. Demand states

`POTENTIAL` · `QUALIFIED` · `FULFILLED` · `PARTIALLY_FULFILLED` · `UNFULFILLED` · `NOT_REQUIRED`.

`QUALIFIED` is the predicate (`qualified=true`). Configured LIVE/GUIDED demand that C13 can evaluate is displayed as `FULFILLED`, `PARTIALLY_FULFILLED`, or `UNFULFILLED`. EXPLORE / `NOT_CONFIGURED` stays `POTENTIAL`. Optional/considered capabilities that are not in the minimum sufficient set are `NOT_REQUIRED`.

These are not API invocation states.

## 3. Qualified-demand definition

A legitimate configured enterprise Intent has reached a point where a network capability could materially contribute to the business decision or action.

It is **not** generic API interest, catalog browsing, every possible API/use-case mapping, revenue, or an API call.

Example: Acme has 500 simulated devices whose OTA qualification requires Roaming Status, and Provider C cannot provide it. That is 500 units of **simulated qualified demand** for Roaming Status — not 500 lost API sales.

## 4. Demand Map

First-class surface `#/demand` (`frontend/src/pages/Demand.jsx`). Visual chain: INDUSTRY → ENTERPRISE → APPLICATION → BUSINESS EVENT / USE CASE → INTENT → NETWORK DECISION GAP → REQUIRED CAPABILITY → REGION → FULFILLMENT STATUS → PROVIDER / SUPPLY GAP.

Navigable in both directions via `/demand/enterprises/{id}`, `/demand/providers/{id}`, `/demand/capabilities/{id}`, `/demand/intents/{id}`, `/demand/industries/{id}`, `/demand/regions/{id}`, `/demand/motions/{id}`, `/demand/gaps/{gap}`.

## 5. Demand-side entry

Question: *I am talking to an enterprise. Where can Network APIs help?*

Example: Financial Services → Rocket Bank → Payments Risk / Digital Identity / Recovery / Digital Onboarding → Intent → decision gap → capabilities → regions → fulfillment → gaps.

The screen answers: what business problem, why network, which capability, can we deliver it, what is missing.

## 6. Supply-side entry

Question: *I am talking to an operator. What demand could its network capabilities serve?*

Example: Network Provider A capabilities → Intents → applications → enterprises → industries. Each hit labelled LIVE / GUIDED / EXPLORE. EXPLORE is not counted as proven fulfilled demand.

## 7. Aggregator entry

Question: *I am talking to an aggregator. What demand can its footprint aggregate and normalize?*

Aggregator A (`simulated-aggregator-b`): regions served, network providers reached, capabilities available via routes, enterprise Intents fulfillable, industries enabled, coverage gaps.

Wording: **ROUTED THROUGH / NORMALIZED THROUGH / AVAILABLE VIA**. Aggregator A does not own the underlying operator APIs.

## 8. Commercial motions

C12 motions filter the map: Identity & Trust, Connected Operations, Device & Fleet Operations, Customer Experience, Network Assurance, Location & Presence → industries → applications → Intents → capabilities. Salespeople do not start from CAMARA `operationId`s.

## 9. Capability leverage

One capability → many business outcomes. Device Reachability reaches High Flight baggage and ground ops, Acme OTA and field maintenance, SwiftShip delivery, Harbor facilities, BuildRight. Counts are industries / applications / Intents / regions / providers. No dollar value.

## 10. API family leverage

13 catalog families → capabilities → Intents → applications → industries. Sales line: **one network capability can serve multiple enterprise applications.**

## 11. Supply-gap impact

Selecting a gap shows what it prevents:

- Provider B · Entitlement Server unavailable → NV2 Wi-Fi blocked → `verify_mobile_number` → Digital Identity → Identity & Trust.
- Provider C · Roaming Status unavailable → OTA cannot fully qualify 500 simulated devices → `prepare_ota_cohort` → Connected Device Operations → Device & Fleet Operations.

Language: **UNFULFILLED QUALIFIED DEMAND** / **SUPPLY GAP AFFECTING QUALIFIED DEMAND**. Not lost revenue.

## 12. Operator enablement view

For a fictional provider: currently ready vs gaps. Enabling Provider B ECS would make additional configured Digital Identity demand fulfillable. Fulfillment impact, not an implementation-recommendation engine.

## 13. NV / ECS example

Rocket Bank Digital Identity `verify_mobile_number`:

- Provider A CELLULAR · NV1 ready · FULFILLED
- Provider A WI-FI · NV2 + ECS ready · FULFILLED
- Provider B WI-FI · NV API available · NV2 supported · ECS unavailable · UNFULFILLED

Operator-facing line: *Exposing the API is not always enough. The fulfillment path must also be operationally ready.*

## 14. OTA example

Acme Manufacturing → Connected Device Operations → `prepare_ota_cohort` → simulated campaign devices → enterprise eligibility → network qualification across Providers A / B / C.

Provider C: Reachability available, Roaming unavailable → 500-device simulated qualified-demand gap. One missing network capability affects one business workflow at fleet scale. No revenue.

## 15. High Flight example

Baggage Operations → `ensure_baggage_connection` → Device Reachability → provider supports it → **FULFILLMENT SUCCESS**.

API returning DEVICE NOT DATA REACHABLE is still successful network evidence delivery. Negative network evidence can be successful API fulfillment.

## 16. Acme inspection dynamic demand

QoD starts available / permitted / entitled / `NOT_REQUIRED`. SLO breach makes it qualified → selected → invoked → verified → `ASSURED`. Network API demand can be contextual, not merely subscription-driven.

## 17. CityCare minimization

Demand is a minimum age assertion. Age Verification is sufficient, permitted, selected, fulfilled. KYC Match is available/relevant but broader than necessary → `NOT_REQUIRED`. AX selects the minimum appropriate network capability. Unnecessary API invocation is not marketed as success.

## 18. Industry view

All ten C12 industries: Financial Services, Retail / Commerce, Insurance, Airlines / Airports, Manufacturing, Logistics / Delivery, Healthcare, Media / Broadcast, Smart Buildings / Facilities, Field Service / Construction. Applications, Intents, decision gaps, capabilities demanded, fulfillment coverage, supply gaps.

## 19. Region view

Canada / Germany / Singapore labelled **CONFIGURED DEMO COVERAGE**. Not market-wide country statistics.

## 20. Provider view

For each fictional provider: regions, routes, capabilities, readiness, configured Intents/applications/industries it can fulfill, qualified demand blocked by gaps. Labelled **CONFIGURED DEMO PORTFOLIO**, not commercial customer counts.

## 21. Aggregator view

Aggregator A: operators reachable, regions, normalized capabilities, routes, configured enterprise Intents served, coverage gaps. An aggregator can broaden supply reach. NetAware AX normalizes that supply against enterprise Intent. No overstated commercial ownership.

## 22. API-to-demand traversal

From Device Reachability: where configured demand exists, each labelled LIVE / GUIDED / EXPLORE and FULFILLED / PARTIAL / UNFULFILLED / NOT_CONFIGURED (potential).

## 23. Intent-to-supply traversal

From `prepare_ota_cohort`: business need → capabilities required → regions → providers → routes → fulfillment → supply gaps.

## 24. Demand / fulfillment distinction

C13: *Can it be fulfilled?* C14: *What configured demand is fulfilled or left unfulfilled?* C14 does not duplicate C13 logic.

## 25. Qualified demand / invocation distinction

Qualified demand does not necessarily produce an API invocation. Reasons: evidence reuse, policy filter, consent, not required after evaluation, already sufficient evidence, no available supply.

## 26. Provenance

Every demand assertion has provenance: INTENT PROFILE, BUSINESS EVENT, CONFIGURED APPLICATION, GUIDED SCENARIO, SIMULATED FLEET, RUNTIME, DERIVED. Demand is not derived merely because an API maps to an industry.

## 27. Affected units

Used only where the existing demo supports it: Acme OTA Provider C roaming = **500 simulated devices**. No invented counts for Rocket Bank, CityCare, High Flight, or SwiftShip. Qualitative qualified demand otherwise.

## 28. Basic Sales View

Top of Demand Map: *Where is network API demand?* Motions → industries → applications → capability demand → fulfilled / gap. A salesperson can read the screen without knowing CAMARA. `operationId`, spec version, OAuth, DPV, TMF, ECS appear only in Technical View.

## 29. Technical View

Drill-down: enterprise, application, Intent, coverage record, purpose, required/optional, minimum sufficient set, region, provider, aggregator, route, CAMARA family, `operationId`, blocking gap, provenance, fulfillment status. Not shown simultaneously.

## 30. Explorer integration

From domain / application / Intent / capability / API family / provider / region: See Demand, See Fulfillment, What does this enable? Explorer is not redesigned.

## 31. Portfolio integration

C12 scenario → See Demand / See Fulfillment. Demand Map → Open business story.

## 32. Coverage integration

C13 remains fulfillment truth. Coverage cards link See Demand. C14 asks what demand that coverage serves.

## 33. Why NetAware panel

Without NetAware: enterprise sees APIs, operator sees network capabilities, aggregator sees supply footprint — disconnected.

With NetAware AX: Business Intent → qualified capability demand → governance → operator / aggregator supply → fulfillment → business outcome.

Close: **NetAware connects enterprise demand to network supply.**

## 34. 3-minute demo story

On-screen, not presenter-dependent:

1. ENTERPRISE — business applications where network information actually changes a decision.
2. FULFILLMENT — which capabilities can be delivered in each region through operators or aggregators.
3. DEMAND MAP — where qualified demand exists and where network supply is missing.
4. OPERATOR — the same information in reverse: which enterprise applications a capability enables.
5. CLOSE — NetAware connects enterprise demand with network supply.

## 35. Regression tests

`backend/scripts/validate_ax_cadence14.py` — 50 OK, 0 FAIL, nesting Cadence 0–13.

Validates: live heroes unchanged; NV / High Flight / OTA / CityCare unchanged; 17-use-case portfolio; 13 API families; demand schema; demand derived from configured business context; potential ≠ qualified; qualified ≠ invocation; fulfilled ≠ positive business result; unfulfilled requires genuine configured demand; EXPLORE is not fake qualified demand; C13 remains fulfillment source; direct and aggregator traversal; capability → intents and intent → supply; NV ECS gap; OTA Provider C 500-unit gap; High Flight unreachable is fulfilled demand; Acme QoD contextual; CityCare minimization; affectedUnits only where supported; no invented revenue/TAM; no real operator claims; provenance exists; Meta_Demo and Jigyasa untouched.

## 36. Known gaps

- Counts are configured demo coverage, not market-wide demand or customer counts.
- EXPLORE remains potential; it is not proven fulfilled demand.
- `QUALIFIED` is a predicate; display uses FULFILLED / PARTIAL / UNFULFILLED once C13 has a coverage status.
- No revenue, pricing, TAM, provider ranking, sales lead scoring, CRM, Meeting Mode, login, MCP, A2A, LLM planner, new hero verticals, new catalog families, or live operator claims.

**STOP. Do not start Cadence 15.**
