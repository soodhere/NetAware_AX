# AX Cadence 8 — Capability Discovery + Basic / Advanced

**Status:** Complete  
**UI cadence:** 8  
**Model cadence:** 7 (discovery enums unchanged)  
**Live demo baseline:** `0.6.1-ax6.1` (unchanged)  
**Product behavior:** Frozen live outcomes. No NV/OTA live, no High Flight rewrite, no SalesScenarioProfile loader, no new hero scenarios.

Do **not** start Cadence 9 until explicitly approved.

---

## 1. Discovery trace model

`discovery[]` is attached to every live `ExecutionTrace` after the existing runner completes (`backend/app/discovery_trace.py`).

It is a **structured view of the same decisions** already used by runtime (`evaluate_capability_policy`, decision states, Telco Finder, API Finder, route, evidence). It is **not** a second decision engine.

Each event includes: `stage`, `candidate`, `candidateType`, `capability`, `apiFamily`, `operationId`, `result`, `reasonCode`, `humanReason`, `source`, `provider`, `route`, `metadata`.

Stage groups remain Cadence 7: `CANDIDATE_GENERATION`, `CONFIGURED_ELIGIBILITY`, `RUNTIME_FEASIBILITY`, `SELECT`. Not every stage is emitted for every candidate.

Canonical reason codes are the Cadence 7 enum. Live policy aliases are mapped, not invented:

| Runtime state / policy | Discovery reason |
| --- | --- |
| INVOKED / SELECTED | SELECTED |
| EVIDENCE_REUSED | EVIDENCE_REUSED |
| NOT_REQUIRED (usefulness) | NOT_REQUIRED |
| Not mapped / not relevant | NOT_RELEVANT |
| Consent required and unavailable | CONSENT_MISSING |
| Policy deny / agreement gap | AGREEMENT_GAP |
| PURPOSE_DENIED | PURPOSE_NOT_PERMITTED |
| NOT_SUBSCRIBED / NOT_ENTITLED | same |

Schema: `data/schemas/discovery-event.json`.

## 2. Basic pipeline

Five layers, business language:

1. **Your application** — what it already knows, Intent sent, Purpose (audience label).
2. **What the network could add** — business capabilities (number possession, SIM continuity, QoD, age assertion, …).
3. **What your configuration allows** — purpose, policy, subscription, entitlement, consent.
4. **What is possible right now** — region, operator, API availability, provider/route.
5. **What NetAware selected** — invoked / reused / skipped / filtered, each with one human reason.

Visual: layered narrowing pipeline with counts. operationId, DPV ids, TMF, HTTP, spec maturity stay in Advanced.

## 3. Advanced candidate matrix

One row per candidate (Acme QoD has INITIAL and AFTER_BREACH rows). Columns are grouped:

- Candidate generation: Relevance
- Configured / onboarding: Agent/Intent, DPV Purpose, Policy, Agreement, Consent, **Subscription**, **Entitlement**
- Runtime discovered: Region, **Telco Finder**, **API Finder**, **Provider**, **Route**, Evidence, Autonomy, Usefulness
- Select: Final result (Cadence 7 reason codes)

Empty technical columns (access type, ECS, operator NV prereqs) are omitted until they have signal.

Source badges: `ONBOARDING` · `CONFIGURATION` · `RUNTIME`.

## 4. Basic / Advanced lens

Same engine. Same trace. Same outcome. No forked scenario implementations.

- Session-persisted (`sessionStorage`), default **BASIC**
- Switch does **not** rerun `/intents`
- Basic tabs: Overview · Discovery · Outcome (Live Flow de-emphasized)
- Advanced tabs: Overview · Discovery · Live Flow · Decisions · APIs · Policy

## 5. Rocket Bank discovery example

Default opener. Network contribution is immediate.

Typical narrowing:

- 7 potentially relevant capabilities
- Location **CONSENT_MISSING** (filtered)
- Number recycling **NOT_REQUIRED**
- 5 selected and invoked
- Outcome **STEP_UP** (unchanged)

## 6. CityCare discovery example

- Age Verification: sufficient, permitted, entitled → **SELECTED**
- KYC Match: related, broader than required, policy/agreement denied → **AGREEMENT_GAP**
- Makes **availability ≠ permission ≠ need** visible
- Outcome **ELIGIBLE** (unchanged)

## 7. Acme dynamic usefulness example

Discovery over time for the same capability:

- Initially QoD: available, permitted, entitled, **NOT_REQUIRED** (objective already satisfied)
- After breach: reconsidered → **SELECTED** → invoked
- Outcome **ASSURED** (unchanged)

## 8. High Flight secondary example

Not the default opener. Scenario not rewritten.

- Location: relevant, available, **CONSENT_MISSING**
- Reachability: **SELECTED**
- Connectivity: **SELECTED**
- QoD: available, **NOT_REQUIRED**
- Outcome **AT_RISK** (unchanged)

## 9. Evidence reuse discovery

Recovery continuity after Rocket Bank trust:

- SIM / device / roaming candidates → **EVIDENCE_REUSED**
- Invocation **SKIPPED**
- Outcome **CONTINUITY_ALIGNED** (unchanged)

Discovery decides CALL / REUSE / SKIP / FILTER, not only which API to pick.

## 10. Telco Finder / API Finder visualization

Advanced Discovery keeps three distinct blocks:

| Asset | Question |
| --- | --- |
| Telco Finder | Which operator/network applies to this subject? |
| API Finder | Which candidate API operations are available through which provider? |
| Provider / route | Where will the selected operation actually be invoked? |

They are not merged into one “discovery” box.

## 11. Configured vs runtime distinction

Advanced splits the matrix:

- **Configured / onboarding:** enterprise, application, purpose, subscriptions, entitlements, policy, agreements, security/agent authorization
- **Runtime discovered / evaluated:** subject context, Telco Finder, operator, API Finder, provider/route, evidence freshness, usefulness, autonomy

TMF931 is not forced onto every screen. A source badge is enough.

Purpose: Basic shows audience label (e.g. Fraud Prevention). Advanced shows `dpv:FraudPreventionAndDetection` plus context. DPV is governance metadata, not the plot.

## 12. Explorer links

Explorer is not redesigned. Light linkage only:

- Intent: **See Discovery model**
- Capability: **Used in live Discovery**
- API family: selected / filtered examples
- Policy: **See where this filtered a candidate**

## 13. Tests

`backend/scripts/validate_ax_cadence8.py`

Covers discovery schema, every live run, Cadence 7 reason codes, same-trace lenses, no rerun on lens switch, subscription vs entitlement, DPV purpose, unchanged hero outcomes, evidence reuse, distinct finders, provider/route, 13-family catalog, picker order, Cadence 0–7 regression, Meta_Demo / Jigyasa untouched.

Cadence 6 opener check is cadence-aware (Rocket Bank first when `UI_CADENCE >= 8`). Cadence 7’s “no Discovery UI” check yields to Cadence 8.

## 14. Known UX gaps

- Access type, operator NV prerequisites, and ECS columns stay hidden because current live heroes do not exercise them (Cadence 9).
- No live **NOT_ENTITLED** example unless existing config already produces one — none was invented.
- High Flight remains a weak network-contribution story; Discovery makes the limitation visible but does not replace the scenario (Cadence 11).
- Basic auto-completes the beat animation so Discovery/Outcome are immediately readable; Advanced keeps the paced Live Flow.
- Explorer Discovery links land on the live run, not a dedicated deep-link into the Discovery tab.

## 15. No new live scenario

Explicit confirmation:

- Executable intents remain the existing five.
- No NV1/NV2 live flow.
- No OTA live flow.
- No High Flight replacement.
- No SalesScenarioProfile runtime loading.
- No catalog expansion.
- No new hero cards.

**STOP. Do not start Cadence 9.**
