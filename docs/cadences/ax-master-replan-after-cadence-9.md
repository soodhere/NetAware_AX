# NetAware AX — Master Commercial / Agentic Replan After Cadence 9

**Status:** Plan only. Not implemented.  
**Baseline:** Cadence 9 complete (`UI_CADENCE=9`, live `0.6.1-ax6.1`, hosted).  
**Do not start Cadence 10 until this plan is explicitly approved.**

This replaces the C10–C13 sequence in `docs/NetAware-AX-Commercial-Evolution-and-Cadence-Plan.md` and the post-Cadence-8 roadmap. Those assumed OTA immediately after NV, Demand Map next, and High Flight as a late rewrite. Cadence 9 changed the dependency order.

---

## 1. Executive recommendation

NetAware AX is no longer a Meta_Demo clone with extra YAML. Cadence 9 proved the commercial differentiator:

**Same business Intent → different network fulfillment → operator readiness decides whether qualified demand is served.**

That is the story a CTO would tell Sales to learn. It is not yet the whole sales asset.

**Do Cadence 10 next as portfolio foundation + Decision Gap visual + High Flight baggage evolution — not OTA.**

Why this order:

1. C9’s visual grammar lives mainly on Number Verification. Other live heroes still look like Cadence 8 text. Sales cannot open Acme or High Flight and feel the same product.
2. Baggage handling is executive/customer requested and **must stay**. The current network contribution fails the Decision Gap test (domain ETA already implies expedite). Leaving it broken while adding OTA trains presenters to skip the airline card.
3. OTA is the right *volume* story and should be Cadence 11 — a second ADVANCED AGENTIC shape, not a pile-on while the visual language is NV-only.
4. 15–20 visible use cases should be configuration on one graph, not 20 runners. That needs an Intent Profile and a BASIC interpreter before we mint more custom engines.

**Target live set: 8. Target visible set: 18. Catalog stays 13 families. No fake revenue. No generic AI platform.**

The CTO test is: “I want my sales people to use this before the meeting.” That requires (a) vertical recognition, (b) a Decision Gap that survives “could this work without the Network API?”, (c) Business vs Technical on the same trace, (d) supply-side unfulfilled demand, (e) a meeting profile — in that dependency order.

---

## 2. What Cadence 0–9 has proven

| Cadence | Proven |
| --- | --- |
| 0–0.2 | 13-family practical catalog; Excel-derived many-intents / few-APIs graph; SOURCE_BACKED vs INFERRED |
| 1 | Demo briefing; Intent without operationIds; configuration-only honesty |
| 2–4 | Deterministic runtime; Telco Finder ≠ API Finder; real `operationId`s; plan / replan / verify; bounded autonomy |
| 5 | Explorer as one graph; evidence store; recovery reuse |
| 6 / 6.1 | Presentation freeze; DX→AX line; Network adds vs enterprise systems; CAMARA maturity as metadata |
| 7 | NV path ≠ operation; ECS as configured readiness not catalog; DPV purposes; subscription ≠ entitlement; discovery reason codes; High Flight replacement *modelled*; OTA *modelled*; SalesScenarioProfile schema not loaded |
| 8 | `discovery[]` is a view of the same engine; Basic/Advanced lens; no second engine |
| 9 | Same Intent, three fulfillments; NV1 on cellular; NV2 on Wi-Fi; ECS gap → CAPABILITY_UNAVAILABLE; unfulfilled qualified demand; path vs operation; Telco Finder ≠ access type; API Finder ≠ ECS |

**Retained Meta_Demo strengths:** tiny request / large trace; selective invocation; reuse; replan; verification; autonomy; finders; why / why-not.

**New AX strengths C9 added:** demand → governed Intent → discovery → deliverable path → consumption → outcome; and the supply reading of the same trace.

---

## 3. What is still missing for Sales

Ranked. These are why the previous C10=OTA plan is wrong.

**P0 — blocks “configure this for the meeting”**

1. **Decision Gap is not a first-class visual** except as NV path cards. Executives still ask “why a Network API?” on Rocket Bank, Acme, CityCare, High Flight.
2. **Presentation lens ≠ scenario complexity.** Cadence 8 called both “Basic/Advanced.” Sales cannot ask for a 45-second BASIC story vs a 2-minute ADVANCED AGENTIC story as a product dimension.
3. **High Flight still fails the contribution test** while remaining in the picker. Domain already knows to expedite. Network reachability does not change the action. The *domain* is valuable; the *network job* is wrong.
4. **Only NV has the C9 visual wow.** Other heroes did not inherit path cards, opportunity panel, or Decision Gap.
5. **No configuration-driven BASIC runner.** Every live Intent is a custom engine. 15–20 visible cases cannot mean 15–20 `run_*` functions.

**P1 — required for a CTO sales asset**

6. No fleet / repeatable-consumption story (OTA still config-only).
7. Explorer answers “what exists,” not “where can I sell SIM Swap” or “can Germany fulfill passwordless sign-in.”
8. No Fulfillment Coverage (FULLY / PARTIALLY / NOT_FULFILLABLE) per Intent × region × operator.
9. Stakeholder lens (enterprise / operator / aggregator) is not a first-class flip of the same trace — only NV’s Network Opportunity sketch.
10. Intent is still largely a string plus a policy row. No Intent Profile.
11. Policy is one evaluation blob, not a visible hierarchy with source/precedence.
12. Meeting still requires remembering hash routes. `SalesScenarioProfile` is schema-only.
13. Hosted Basic Auth exists as env plumbing; not fail-closed; no vertical profile.

**P2 — later**

14. MCP Intent tools vs DX operation tools.
15. Business View / Technical View rename.
16. Demand Map surface (reverse graph already exists).
17. Field/logistics BASIC live case (research-ready, not modelled as a seed).

---

## 4. Competitive / product positioning

| Product | What it is | What AX must not become |
| --- | --- | --- |
| **Meta_Demo** | Agentic orchestration proof on Network APIs | A second copy with more panels |
| **CAMARA / Open Gateway DX** | Developer selects `checkSimSwap` | A prettier DX portal |
| **Aggregator developer portal** | Catalog + credentials + try-it | Marketplace clone |
| **Generic agent platforms** | Unrestricted tools + LLM | “MCP over CAMARA” |
| **Enterprise systems** | IAM, fraud, BRS, MES, OTA, TMS | Replacements for those systems |

**AX positioning line:**

> Your application stays in its domain. You request a governed business outcome. NetAware discovers which Network APIs are relevant, available, entitled, permitted and needed — then consumes only those that can actually serve the Intent. Operators see which qualified demand they fulfilled, and which readiness gaps blocked it.

Differentiation vs Meta_Demo is **not** more animation. It is: governed Intent, Decision Gap, discovery as product, path vs operation, unfulfilled qualified demand, fulfillment coverage, Demand Map.

---

## 5. Network Decision Gap framework

**Definition.** A Network Decision Gap is a piece of information, verification, network control, or network readiness that the enterprise’s existing systems do not independently have, and which **materially changes** the business decision or action.

**Required visual for every live scenario:**

```
YOU ALREADY HAVE     → enterprise systems / APIs
YOU NEED TO DECIDE   → business decision
NETWORK DECISION GAP → missing information or control
NETWORK ADDS         → capability (not operationId in Business View)
NETAWARE AX          → discover / govern / select / execute
OUTCOME              → business result the application understands
```

**Seven questions (must all pass for a hero):**

1. What enterprise systems already exist?
2. What do they already know?
3. What decision are they trying to make?
4. What is the Network Decision Gap?
5. What unique thing does the network contribute?
6. Which practical Network API provides that?
7. Does it materially change the business action?

If removing the Network API makes little difference: **REJECT / DEMOTE**.

**Tiers**

| Tier | Meaning | Hero eligible |
| --- | --- | --- |
| **A — Indispensable** | Enterprise cannot get the same answer without the Network API | Yes |
| **B — Materially improves** | Workflow works without it, with less confidence or control | Yes, with honest framing |
| **C — Merely interesting** | “We have roaming, let’s show roaming” | No |

Do not start from a Network API. Start from the workflow.

---

## 6. Scenario complexity model

**Two orthogonal dimensions. Do not collapse them.**

### A. Presentation lens (same scenario, same trace)

| Lens | Audience | Shows |
| --- | --- | --- |
| **Business View** | Exec, sales, line-of-business | Event, Decision Gap, Intent, contribution, narrowing, outcome |
| **Technical View** | Architect, CAMARA, operator engineer | DPV, TMF-aligned onboarding, policy source, finders, `operationId`, evidence, autonomy |

Today this is labelled Basic / Advanced. **Do not rename in Cadence 10.** Rename when Meeting Mode / sales freeze ships, so presenters are not retrained twice. Until then: document the two dimensions in model (`presentationLens`, `scenarioComplexity`) and stop using “Advanced” to mean both “show operationIds” and “multi-step agentic.”

Lens switch **must not** rerun (Cadence 8 invariant).

### B. Scenario complexity (different stories, possibly different seeds)

| Class | Shape | Duration | Engine |
| --- | --- | --- | --- |
| **BASIC** | One decision gap, one primary capability, obvious contribution | 30–60s | Configuration-driven interpreter |
| **COMPOSED** | Enterprise + network evidence, several capabilities, policy/discovery | 1–2 min | Shared interpreter + light seed rules |
| **ADVANCED AGENTIC** | Dynamic discovery, multi-step plan, replan, reuse, conditional action, path selection, verify, autonomy | 2–4 min | Dedicated runner allowed |

**Rule:** only ADVANCED AGENTIC earns a custom runtime module (`nv_runtime.py`, Acme loop, future OTA). BASIC/COMPOSED should not each get a 400-line function.

---

## 7. Business vs Technical view

**Recommendation:** keep current Basic/Advanced *control* through C11. Introduce the names Business View / Technical View in copy and docs in C10. Physical rename of the toggle in the sales-freeze cadence.

**Business View content contract**

- Business Event (not `intentId` as the headline)
- Decision Gap strip
- Intent in one sentence
- Network contribution (capability language)
- Discovery narrowing (visual, not count-only)
- Selected action / path
- Outcome the application understands
- Optional: Network Opportunity (operator reading) after result
- No OIDC/CIBA, no DPV IRIs, no TMF class names

**Technical View content contract**

- Enterprise / Application / Agent / actsFor
- DPV purpose + context
- Policy hierarchy with **source**
- Agreement / DPA / consent evaluation
- Subscription vs entitlement
- Four region facets (commercial / technical / governance / data)
- Telco Finder, API Finder, provider, route
- Prerequisites (access, ECS, TS.43) when in play
- Path vs operation when in play
- `operationId`, spec maturity as metadata
- Evidence + reuse audit
- Autonomy / approval

---

## 8. Recommended visible use-case portfolio (~18)

Sales should enter a vertical and recognize problems. These are **visible** (Home/Explorer/vertical list). Not all are live.

| # | Visible use case | Vertical | Complexity | Live? |
| --- | --- | --- | --- | --- |
| 1 | Passwordless mobile sign-in | Financial / IAM | BASIC → ADVANCED AGENTIC (variants) | Yes (C9) |
| 2 | High-value transaction protection | Financial | COMPOSED | Yes |
| 3 | Account recovery continuity | Financial | BASIC / COMPOSED | Yes (secondary) |
| 4 | Checkout trust | Retail | COMPOSED | Explorer → optional later live (same identity family) |
| 5 | Pharmacy age / eligibility | Healthcare | COMPOSED / GOVERNANCE | Yes |
| 6 | Age-restricted sale | Retail | BASIC | Explorer |
| 7 | Baggage handling / ramp device operability | Airlines | COMPOSED / ADVANCED | Evolve live (keep visible) |
| 8 | Firmware / device-fleet rollout | Manufacturing / IoT | ADVANCED AGENTIC | C11 live |
| 9 | Critical inspection camera | Manufacturing | ADVANCED AGENTIC | Yes |
| 10 | Field / delivery device operability | Logistics | BASIC | C12 live |
| 11 | High-value shipment custody | Warehouse / logistics | BASIC / COMPOSED | Explorer |
| 12 | Claim / FNOL device continuity | Insurance | COMPOSED | Explorer (identity family reuse) |
| 13 | Claim location consistency | Insurance | COMPOSED | Explorer |
| 14 | Home-care visit verify | Healthcare | BASIC | Explorer (consent-heavy) |
| 15 | Telehealth session quality | Healthcare | COMPOSED | Explorer (experimental QoD) |
| 16 | Site equipment on site | Construction | BASIC | Explorer |
| 17 | Dock scan session | Warehouse | BASIC | Explorer |
| 18 | KYC attribute match | Financial | GOVERNANCE | Explorer only (privacy-sensitive) |

**Not in the 18 as heroes:** locate-baggage (bag location via Network Location — fails Decision Gap), live-broadcast, venue-experience, airside-asset-presence, turnaround-video, site-uplink. Keep in the universal graph as Explorer-only so the catalog still teaches reuse; do not feature them.

18 is inside 15–20. Adding checkout as live later would be a 9th executable — resist unless a retail meeting requires it; show it as “same APIs, different enterprise” in Explorer first.

---

## 9. Recommended executable / live portfolio (8)

| # | Live story | Intent | Complexity | Cadence |
| --- | --- | --- | --- | --- |
| 1 | Passwordless mobile sign-in | `verify_mobile_number` | BASIC / ADVANCED AGENTIC (seeds) | 9 done |
| 2 | Transaction trust | `assess_network_trust` | COMPOSED | 4–9 done |
| 3 | Account recovery | `assess_recovery_continuity` | COMPOSED | 5 done |
| 4 | Critical inspection | `maintain_inspection_experience` | ADVANCED AGENTIC | 4–9 done |
| 5 | Pharmacy age gate | `verify_pharmacy_age_gate` | COMPOSED / GOVERNANCE | 4–9 done |
| 6 | Baggage / ramp device operability | evolve to `assure_ramp_scan_capability` (or keep id, change job) | COMPOSED / ADVANCED | **10** |
| 7 | Device fleet / OTA readiness | `rollout_firmware_safely` | ADVANCED AGENTIC | **11** |
| 8 | Field / delivery device operability | new `assure_connected_operation` (working id) | BASIC | **12** |

Recovery stays secondary to transaction trust (same enterprise, not a fifth Home hero). Field/delivery is the BASIC 45-second operational twin of baggage, without airline context — so logistics meetings are not forced through High Flight.

---

## 10. Existing enterprise / domain systems (live cases)

| Live case | Enterprise already has | Domain APIs (typical) | Network must not replace |
| --- | --- | --- | --- |
| NV sign-in | CIAM / IAM, session, MFA, directory | AuthN, session, risk | Login, OTP product, IdP |
| Transaction trust | Payments, fraud, core banking | Payments API, fraud decisioning | Fraud models, decline authority |
| Recovery | IAM / recovery, tickets | Recovery / step-up | Password reset |
| Inspection | MES, QMS, vision / camera control | MES, QMS, camera | Plant control, inspection verdict |
| Age gate | Pharmacy / POS eligibility | Pharmacy transaction | Pharmacist dispense decision |
| Baggage / ramp | **BRS, DCS, baggage events, ground handling, flight/AODB, load-close, ramp assignment, handheld inventory** | BRS scan session, DCS bag-flight, flight status, device assignment | Bag tracking, sortation, physical transfer |
| OTA | Inventory, twin, firmware, campaign, telemetry, rollback | list/get device, twin, package, campaign, wave, check-in | Flashing firmware |
| Field / delivery | WFM / TMS, driver app, POD, device assignment | Route, stop, POD, device | Dispatch, proof-of-delivery system |

Airline realism (keep this vocabulary on screen):

- **BRS** — IATA Reso 753 custody: bag-to-flight, load/unload, scan events  
- **DCS** — check-in, bag tag, passenger/flight coupling  
- **Ground handling** — ramp crew, assigned scanner `HF-HDL-0192`  
- **Load-close / turnaround** — operational deadline the enterprise already owns  
- Network subject is the **connected handheld**, not the suitcase  

---

## 11. Network contribution test (live cases)

| Live case | Decision | Gap | Network adds | Practical API | Removes API → still works? | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| NV sign-in | Can we silently trust this MSISDN? | IAM cannot prove possession without user friction | Silent possession | Number Verification (path NV1/NV2) | Yes, with OTP — worse UX, not the same | **Tier A — KEEP** |
| Transaction trust | Step-up or proceed? | Fraud does not see SIM/device/network identity change | Continuity evidence | NV, SIM Swap, Device Swap, Roaming | Yes, weaker — **Tier B/A mix** | **KEEP** |
| Recovery | Normal recovery or step-up? | Recovery looks digitally normal | Continuity / reuse | SIM/device/roaming | Yes, weaker | **KEEP secondary** |
| Inspection | Hold line or restore SLO? | MES sees camera SLO, not whether network action would help | Observe + QoD act + verify | Connectivity Insights, QoD | Partly — **Tier A when QoD is the lever** | **KEEP** |
| Age gate | Age threshold only? | Pharmacy must not run full KYC | Minimum assertion | Age Verification; KYC filtered | Broader KYC would work and is *wrong* | **KEEP governance** |
| **Current High Flight** | Expedite transfer? | Domain ETA already says expedite | Reachability / QoD | Reachability | **Yes, almost unchanged** | **FAIL — EVOLVE** |
| **Evolved baggage** | Can assigned scanner complete custody scan before load-close? | BRS knows bag/worker/deadline, not DATA reachability | Reachability, roaming if material, connectivity if practical | `getReachabilityStatus`, optionally roaming | No for *connected* custody workflow | **Tier B → hero** |
| OTA | Which devices get this wave *now*? | OTA platform knows inventory/firmware, not cellular suitability | Reachability, roaming, connectivity if needed | Reachability, Roaming | Campaign possible, worse failure rate | **Tier B — C11** |
| Field / delivery | Can this device complete POD / connected stop? | TMS knows stop, not device DATA reachability | Reachability; location verify only if it changes the stop | Reachability | Offline fallback exists — **Tier B BASIC** | **C12** |

---

## 12. KEEP / EVOLVE / DEMOTE / EXPLORER ONLY

| Item | Action | Why |
| --- | --- | --- |
| Passwordless NV | **KEEP** | C9 flagship; volume + readiness |
| Rocket Bank trust | **KEEP** | COMPOSED identity; add Decision Gap visual |
| Recovery | **KEEP** secondary | Reuse / minimization; not another fraud story |
| Acme inspection | **KEEP** | Best ADVANCED AGENTIC closed loop |
| CityCare age | **KEEP** | Governance/minimization; not the volume opener |
| **Baggage handling (domain)** | **KEEP visible** | Executive/customer requested |
| **Current `ensure_baggage_connection` job** | **EVOLVE** | Contribution test fail; do not delete airline |
| Locate baggage | **EXPLORER ONLY** | Network Location ≠ bag tracking |
| OTA | **ADD live C11** | Modelled; not executable |
| Field / delivery | **ADD live C12** | BASIC operational; logistics vertical |
| Checkout trust | **EXPLORER** (identity reuse) | Do not clone Rocket Bank as a 9th engine |
| KYC match | **EXPLORER ONLY** | Privacy; CityCare already teaches filter |
| Telehealth, venue, broadcast, turnaround video | **EXPLORER ONLY** | QoD-interesting (Tier C as heroes) |
| Construction geofence / site uplink | **EXPLORER ONLY** | Thin Decision Gap vs equipment registry |
| High Flight as opener | **Stay demoted** until evolved; then may sit #3 | After C10, NV still opens |

---

## 13. Baggage Handling / High Flight evolution — KEEP THE STORY

**Do not remove baggage handling. Do not make it a generic reachability demo.**

### What stays

- High Flight Airlines  
- Bag `HF123456`, connecting flight as **domain context**  
- Ground operations, load-close pressure  
- Picker card in Airlines vertical  
- Complementary domain APIs on screen: BRS, DCS, flight/AODB, device assignment  

### What changes (Cadence 10)

**Business event:** Bag needs a custody/load scan before load-close. Assigned ramp scanner `HF-HDL-0192`.

**Intent (working):** Assure the assigned connected device can complete the required baggage digital operation. Prefer `assure_ramp_scan_capability` (already in C7 model) over stretching `ensure_baggage_connection`. If changing Intent id is too disruptive for traces, keep the id and **change the job, outcome, and subject** — do not keep EXPEDITE_TRANSFER as the network-driven action.

**Network subject:** handler device, not the bag.

**Network adds:** Device Reachability; Roaming when it explains unreachability; Connectivity Insights only if it would change SWAP vs CONTINUE. **QoD and Location default NOT_REQUIRED.**

**Network does not:** move bags, replace BRS tracking, invent bag GPS.

**Outcomes the airline already understands:** CONTINUE · SWAP DEVICE · REASSIGN HANDLER · USE OFFLINE FALLBACK · HOLD LOAD-CLOSE / ESCALATE.

**AX shape:** COMPOSED, with a light ADVANCED path if reachability is down and roaming explains why.

**C7 model** `data/model/high-flight-replacement.yaml` remains the source. C10 *executes* it. Purpose DPV remains NEEDS_REVIEW (`dpv:FulfilmentOfContractualObligation` vs ServiceOptimisation).

**Sales 45-second line:** “BRS already knows the bag, the flight, and who should scan. NetAware answers whether that scanner can complete the scan on the operator network before load-close.”

---

## 14. OTA / device-management scenario

**Cadence 11, not 10.** C7 model `ota-device-fleet.yaml` is still correct.

- Application: new Acme Device Fleet (or equivalent), **not** the inspection camera app  
- Enterprise owns flash / campaign / rollback  
- Network never flashes firmware  
- Agentic shape: DISCOVER → SEGMENT → PLAN COHORT → ENTERPRISE OTA ACTION → OBSERVE → REASSESS → EXPAND / DEFER  
- Network: Reachability + Roaming; Connectivity optional; QoD/Location/Edge default NOT_REQUIRED  
- Visual: cohorts, not a giant device table  
- Complexity: ADVANCED AGENTIC  
- Commercial: repeatable API consumption; operator volume  

Do not admit eSIM FOTA, Connected Network Type, or reachability-subscriptions into the 13-family catalog for this demo.

---

## 15. Identity / NV / recovery portfolio

One enterprise (Rocket Bank) demonstrates **catalog reuse**:

| Application | Use case | Intent | Point |
| --- | --- | --- | --- |
| Digital Identity / IAM | Passwordless sign-in | `verify_mobile_number` | Path selection; ECS gap |
| Payments Risk | Transaction protection | `assess_network_trust` | Selective evidence; STEP_UP |
| IAM / Recovery | Account recovery | `assess_recovery_continuity` | Governed reuse; not fraud |

Do not merge NV into `assess_network_trust`. Do not make recovery a second STEP_UP story. Explorer should show checkout/claims as **same capabilities, different enterprises**.

---

## 16. Manufacturing portfolio

| Story | Role |
| --- | --- |
| Critical inspection | Live ADVANCED AGENTIC; observe / NOT_REQUIRED / breach / QoD / verify |
| OTA fleet | Live C11; different application under same enterprise |
| Equipment on site | Explorer only |

Two live stories, one enterprise, two applications — same pattern as Rocket Bank IAM vs Payments.

---

## 17. Logistics / field operations portfolio

**C12 BASIC live:** driver or field technician must complete a connected workflow (POD, work-order close, photo). Workforce/TMS already has the stop. Gap: is the assigned mobile DATA reachable?

Outcomes: READY · OFFLINE_FALLBACK · SWAP_DEVICE. Location Verification only if independent location assertion changes the stop (geofenced site). Do not turn it into a tracking demo.

Shipment custody / dock scan remain Explorer until this BASIC story is demo-safe — they are easy to fake as “location because we have location.”

---

## 18. Healthcare / governance role

CityCare stays **live** as the minimization/governance proof (Age selected, KYC filtered). It is not the volume opener. Telehealth and home-care stay Explorer: experimental maturity and consent gravity. Do not lead operator sales with Age Verification unless the meeting is explicitly Open Gateway identity + privacy.

---

## 19. Governed Intent model

**Intent is not a string.** It is a governed request for a business or operational outcome, evaluated in onboarding + runtime context:

Enterprise, Application, Agent / API client, Use Case, Intent, DPV Purpose, Subject, Region (four facets), Agreement/DPA, Consent, Subscription, Entitlement, Policy, Agent authority, Autonomy, Provider availability, Runtime network context (access type, etc.).

The **HTTP body stays small** (Cadence 2 invariant). The profile lives in configuration.

---

## 20. Intent Profile schema proposal

New config object `IntentProfile` (YAML under `data/model/`, schema under `data/schemas/`). **Runtime request does not send this.** Cadence 10: schema + populate for live Intents; interpreter may read it. Do not load `data/profiles/` SalesScenarioProfile yet.

Proposed fields:

```
intentId
label
businessOutcome
complexity: BASIC | COMPOSED | ADVANCED_AGENTIC
enterpriseId / applicationId
authorizedActors[]          # agentIds
purposeId                   # DPV via purposes.yaml
regions[]                   # commercial default
candidateCapabilities[]     # { id, role: required|considered }
minimumEvidence
optionalEvidence
dataMinimization            # true → skip broader than needed
reusePolicy                 # { allowed, ttl, purposeCompatibility }
failurePolicy               # CAPABILITY_UNAVAILABLE | CONTINUE_WITHOUT | ESCALATE
autonomy                    # observe/recommend/act bounds
decisionOwner               # enterprise function
verificationRequirement     # none | after_act | always
decisionGap                 # { alreadyHave, decide, gap, networkAdds }
networkContributionTier     # A | B | C
```

This is the onboarding contract. `SalesScenarioProfile` later *selects* an Intent Profile + seed + audience; it does not duplicate governance.

---

## 21. Policy hierarchy

Show as stacked sources in Technical View, not one boolean.

```
GLOBAL / PLATFORM GUARDRAILS     (AX: no SMS OTP fallback, no fake NV1, catalog pin)
        ↓
ENTERPRISE POLICY
        ↓
APPLICATION POLICY
        ↓
INTENT POLICY
        ↓
REGIONAL POLICY                  (governance region facet)
        ↓
PURPOSE / DATA POLICY            (DPV + data category)
        ↓
AGENT DELEGATION                 (allowedIntents, notAuthorized actions)
        ↓
COMMERCIAL ENTITLEMENT           (subscription ≠ entitlement)
        ↓
RUNTIME FEASIBILITY              (finder, path, ECS, access)
        ↓
AUTONOMY                         (ACT vs RECOMMEND vs NOT_AUTHORIZED)
```

Each evaluation in the trace should carry `source` + `layer`. Cadence 8 already has ONBOARDING / CONFIGURATION / RUNTIME. Extend; do not replace.

**Do not implement a real policy engine in C10.** Emit layer labels from existing `evaluate_capability_policy` + path selection.

---

## 22. Consent / DPA / agreement model

Stop decorative “DPA ✓ Consent ✓.”

**Consent** (when modelled): subject, enterprise, application, purpose, capability or data category, region, scope, validity, source.

Evaluation: `NOT_REQUIRED` | `REQUIRED_AND_PRESENT` | `REQUIRED_AND_MISSING` | `NOT_APPLICABLE`.

Today High Flight / Rocket Bank location is `REQUIRED_AND_MISSING` — keep that as the teaching case. NV sign-in is typically `NOT_REQUIRED` for claimed-MSISDN verify under configured purpose (honest: configured demo, not a legal conclusion).

**Agreement / DPA** may constrain: capabilities, purposes, regions, reuse, data categories, retention. Label **CONFIGURED DEMO GOVERNANCE**. NetAware does not make legal determinations.

---

## 23. Regional policy / commercial / data model

Split four facets (C10 model comments + C13 Explorer):

| Facet | Question | Source |
| --- | --- | --- |
| **Commercial region** | Which contract / provider commercial overlay? | Onboarding |
| **Technical region** | Which operator APIs exist here? | Telco Finder + API Finder |
| **Governance region** | Which policy/DPA applies? | Agreement |
| **Data region** | Which processing/reuse profile? | Agreement residency |

Do not claim country law. Germany passwordless example is **configured** operator readiness + API inventory, not “GDPR engine.”

---

## 24. Governed evidence reuse

Keep Cadence 5 behavior; tighten the audit checklist in Technical View:

same enterprise · compatible application · same subject · compatible purpose · region facet compatible · agreement permits reuse · TTL valid · policy unchanged · fresh enough for this Intent → `EVIDENCE_REUSED`.

Sales meaning: latency, API economy, data minimization — not “cache for fun.” Recovery remains the live proof. Do not reuse Number Verification evidence from sign-in into a payment without purpose compatibility (they are different purposes).

---

## 25. Agent onboarding / delegation

```
ENTERPRISE
  ├── APPLICATION     commercial relationship, subscriptions, purposes, agreements, credentials
  └── AGENT           actsFor application, identity, allowed intents, delegated authority, autonomy, MCP/API access
```

Application ≠ Agent (already true). Cadence 16 makes delegation visible as a graph: actsFor, allowedIntents, NOT_AUTHORIZED actions. Rocket Bank already has two applications / two agents — use that as the teaching picture before inventing MCP.

---

## 26. DX vs AX vs MCP vs A2A

| Mode | Who | What they send | Who selects Network APIs |
| --- | --- | --- | --- |
| **DX** | Developer | CAMARA operation | The caller |
| **AX / Intent** | Application | Governed Intent | NetAware |
| **AX / Agent** | Enterprise agent | MCP **Intent tool** | NetAware |
| **A2A** | Domain agent ↔ network agent | Only when two agent identities are real | NetAware still governs network side |

**MCP layers (do not dump the catalog):**

- DX-style tools: `checkSimSwap`, `phoneNumberVerify` — exist for honesty, **not** the AX story  
- AX Intent tools: `verify_mobile_number`, `assess_network_trust`, `prepare_ota_cohort`, `assure_connected_operation`  

Tool availability = agent identity × actsFor × application × allowed intents × purpose × policy × subscription × entitlement × region.

Do not force MCP/A2A into NV or CityCare. First MCP demo should be an agent that only receives `verify_mobile_number`, not 37 operations.

---

## 27. Provider model

**Provider** is the parent. Types: **MNO**, **Aggregator**.

| | MNO | Aggregator |
| --- | --- | --- |
| Owns | Radio, often ECS | Commercial route, normalized APIs |
| Defines | NV1/NV2, ECS readiness, inventory, versions | Downstream coverage, API availability, not ECS ownership |
| Route | DIRECT: NetAware → MNO | AGGREGATED: NetAware → Aggregator → MNO |

**HYBRID:** different operations, different routes (already in AX). C9 supply-side metadata (A NV2-ready, B API+ECS gap, C NV unavailable) is the seed for Fulfillment Coverage and Demand Map. Do not invent a fourth provider type.

---

## 28. Fulfillment Coverage model

Not “API available in Germany.” **Can this business use case be fulfilled here?**

Example: Passwordless mobile sign-in / Germany

| Operator | NV1 | NV2 | ECS | Status |
| --- | --- | --- | --- | --- |
| A | ✓ | ✓ | ✓ | **FULLY_SUPPORTED** |
| B | ✓ | advertised | ✕ | **PARTIALLY_SUPPORTED** (cellular only) |
| C | — | — | — | **NOT_FULFILLABLE** |

Statuses: `FULLY_SUPPORTED` | `PARTIALLY_SUPPORTED` | `NOT_FULFILLABLE`.

Explorer C13. Built from C9 path + operator-readiness + API Finder. No new CAMARA APIs.

---

## 29. Universal Explorer design

**One graph. Login only highlights.** Never fork Explorer per vertical.

Entry points (same nodes, different roots):

| Entry | Path |
| --- | --- |
| **BUSINESS** | Industry → Enterprise → Application → Use Case → Intent → Decision Gap → Capabilities |
| **INTENT** | Intent → Purpose → Governance → Capabilities → APIs → Providers |
| **NETWORK** | Capability/API → Decision gaps → Intents → Use cases → industries → regions/providers |
| **PROVIDER** | MNO/Aggregator → regions → APIs → readiness → fulfillable Intents → gaps |
| **AGENT** | Agent → actsFor → application → authorized Intents → purposes → authority |

Cadence 5 already has forward/reverse catalog. C13 adds Decision Gap + coverage as node metadata, not a second graph.

---

## 30. Demand Map design

Two sales questions, one reverse graph (evidence grades preserved):

**WHERE CAN I SELL THIS NETWORK API?**  
SIM Swap → sim continuity → transaction protection / recovery / checkout / claims → Financial / Retail / Insurance → regions/providers → live proof.

**WHAT NETWORK APIs CAN I SELL TO THIS CUSTOMER?**  
Manufacturing → OTA + inspection + field equipment → decision gaps → Reachability / Roaming / QoD → provider/region support.

Preserve SOURCE_BACKED / INFERRED / NEEDS_REVIEW. Cadence 14. Do not attach revenue.

---

## 31. Stakeholder lenses

Same execution, three readings (generalize C9 Network Opportunity):

| Lens | Question |
| --- | --- |
| **Enterprise** | What network capability helped my business? One Intent, no NV1/NV2 code. |
| **Operator** | Which qualified demand reached my APIs? What blocked fulfillment? |
| **Aggregator** | Which downstream MNOs could serve this? Where is coverage/readiness thin? |

Do not create three engines. Flip is presentation. Ship as a first-class control in C14; C10 may reuse NV’s opportunity panel pattern on evolved High Flight.

---

## 32. Unfulfilled Qualified Demand model

C9 generalized conceptually:

`businessDemandQualified` · `demandFulfilled` · `provider` · `route` · `capability` · `path` · `blockingReadinessGap` · `networkApiInvocations`

Blockers (reason codes already largely exist): API unavailable, region, not subscribed, not entitled, purpose denied, consent missing, agreement gap, route unavailable, prerequisite missing, ECS unavailable, access incompatible.

**Qualified** means: relevant + permitted + entitled enough to be real demand — not a random catalog browse.

No monetary values. Phrase: **unfulfilled qualified demand**, never lost revenue.

Apply this object to every live Intent from C10 onward (High Flight evolve is the second proof after NV).

---

## 33. Demo login / vertical profile concept

**Cadence 17 (freeze), not C10.**

1. HTTP Basic Auth from secrets; fail closed when `ENVIRONMENT=hosted` if creds missing; `/health` stays open.  
2. Lightweight **Demo Profile** after login: General · Financial · Manufacturing & IoT · Airlines / Airports · Logistics · Healthcare.  
3. **Audience:** Enterprise · Operator / Aggregator.

Affects only: featured scenarios, default filters, suggested path, default lens. Universal Explorer unchanged. Not a configuration wizard. `SalesScenarioProfile` loader belongs here, not in C10.

---

## 34. Sales questions / shortcuts

Visual shortcuts into the one graph (not a chatbot):

- What can I sell to this bank?  
- Where can I sell SIM Swap?  
- Can we support passwordless sign-in in Germany?  
- Which operator is blocking NV2 and why?  
- What use cases appear if this MNO enables an API?  
- What Network APIs help this manufacturer?  
- Which demand is unfulfilled by current coverage?  

C13–C14. Each shortcut is a pre-set Explorer root + filters.

---

## 35. Visual storyboard principles

**More visual. Less text. No admin dashboard.**

Every live scenario: Decision Gap strip (You already have / Decide / Gap / Network adds / AX / Outcome).

Prefer: event cards, candidates dropping out, NV path switching (exists), OTA cohorts (C11), provider topology, coverage status, enterprise ↔ network split.

**Every motion explains a decision.** No decorative animation (C8 rule stands).

C10 applies this strip to **all current live heroes**, not only NV. That is how C9’s grammar becomes the product.

---

## 36. Recommended Cadence 10+

Previous plan (OTA → checkpoint → Demand Map → Meeting Mode + High Flight → freeze) **is retired.**

| Cadence | Scope | Why this order |
| --- | --- | --- |
| **10** | Decision Gap visual on all live heroes; scenario complexity tags; Intent Profile schema+data; **High Flight baggage EVOLVE** (ramp device); unfulfilled-demand object on that trace; config-driven interpreter **spike** for one COMPOSED path if time | Makes C9 language universal; fixes executive airline story; no new catalog |
| **11** | OTA / fleet live (Acme Device Fleet); cohort visual; network does not flash | Volume/repeatable consumption; second ADVANCED AGENTIC shape |
| **CHECKPOINT** | Sales dry-run NV + evolved baggage + OTA. Do not auto-start 12. | Three strong stories: identity, operations, fleet |
| **12** | Visible 18-use-case vertical portfolio in Home/Explorer; BASIC live field/delivery; configuration-driven interpreter for BASIC | “This is my industry”; no 9th custom engine |
| **13** | Universal Explorer commercial entry points; Fulfillment Coverage (e.g. Germany NV) | Operator/aggregator questions without Demand Map yet |
| **14** | Demand Map + Enterprise/Operator/Aggregator lens flip | Reverse sell + supply reading of any trace |
| **15** | Policy hierarchy + consent/DPA dimensions + four region facets on Technical View; reuse checklist | Architect trust |
| **16** | Agent delegation graph; MCP **Intent** tools (governed); no catalog dump | AX vs DX; still not a generic agent platform |
| **17** | Hosted Basic Auth fail-closed; Demo Profile; SalesScenarioProfile loader; Business/Technical rename; presenter pack; **sales freeze** | CTO can hand URL to Sales |

**Do not combine 10+11.** OTA plus High Flight rewrite plus universal visual is how cadences slip.

Catalog remains 13 families unless a later cadence explicitly admits a family (not expected before freeze).

---

## 37. Acceptance criteria per cadence

**C10**

- All live runs show Decision Gap strip in Business View  
- High Flight: bag remains context; network subject is scanner; no bag-location claim; outcomes in {CONTINUE, SWAP_DEVICE, REASSIGN, OFFLINE_FALLBACK, HOLD/ESCALATE}; QoD/Location not required by default  
- `ensure_baggage_connection` AT_RISK/EXPEDITE is gone or clearly superseded  
- Intent Profiles exist for all live Intents; request body still small  
- Complexity tags BASIC/COMPOSED/ADVANCED_AGENTIC in model  
- Unfulfilled qualified demand fields on NV (regression) and evolved baggage  
- Rocket Bank, Acme, CityCare, NV outcomes unchanged except presentation  
- Cadence 0–9 validators pass  
- **OTA not live. MCP not live. Demand Map not live.**

**C11**

- `rollout_firmware_safely` executable; firmware via enterprise OTA API only  
- Cohort visual; no fake revenue  
- Inspection camera story unchanged  

**C12**

- ≥16 visible use cases grouped by vertical  
- One new BASIC live (field/delivery) on the shared interpreter  
- Home does not grow a 9th custom engine  

**C13**

- Coverage matrix Intent × operator for NV  
- Explorer BUSINESS/NETWORK/PROVIDER entry points (same graph)  

**C14**

- Demand Map forward + reverse with evidence grades  
- Stakeholder lens does not rerun  

**C15–C16**

- Policy layers labelled; MCP Intent tools gated by allowedIntents  

**C17**

- Hosted auth fail-closed; profile changes featured set only; freeze checklist  

---

## 38. What explicitly NOT to build

- Generic chatbot or AI workflow builder  
- Hundreds of APIs / marketplace / DX portal replacement  
- Billing, real ECS, real TS.43, real OIDC/CIBA  
- Device-management, fraud, BRS, MES, or OTA **platforms**  
- Network Location as baggage tracking  
- SMS OTP as AX Number Verification fallback  
- Fake NV1 over Wi-Fi  
- Revenue / lost-revenue numbers  
- Separate Explorer per vertical  
- One custom runner per visible use case  
- Unrestricted MCP over the CAMARA catalog  
- A2A as default architecture  
- Cadence 10 OTA (deferred to 11)  
- Cadence 10 Demand Map / Meeting Mode / login wizard  

---

## 39. Risks / NEEDS_REVIEW

| Item | Risk | Disposition |
| --- | --- | --- |
| High Flight Intent id change | Breaks briefing URLs, Explorer links, validators | Prefer `assure_ramp_scan_capability`; alias old route for one cadence |
| DPV for ramp ops | No dedicated ramp term | Keep C7 NEEDS_REVIEW; do not invent DPV ids |
| Field/delivery Intent id | Not in graph yet | Working id `assure_connected_operation` — lock in C12 |
| Config-driven interpreter | Underpowered for COMPOSED | Spike in C10; if it fails, only BASIC uses it in C12 |
| Basic/Advanced rename | Presenter churn | Copy-only in C10; control rename in C17 |
| Reachability as “generic” | Baggage and field look identical | Bag/flight/BRS context must stay on the airline card |
| Age Verification experimental | Over-selling CityCare | Keep as governance, not volume |
| Device Identifier / Insights experimental | Honesty | Maturity remains metadata |
| Hosted instance already on C9 | Sales uses mixed visual quality | C10 is the “all heroes speak Decision Gap” cadence |
| Scope creep into policy engine | C10 becomes C15 | Labels only in C10 |

---

## 40. Recommended first next implementation cadence

**Cadence 10 — Decision Gap product language + High Flight baggage evolution.**

Not OTA. Not Demand Map. Not MCP. Not login.

**In:**

1. Decision Gap visual on NV, Rocket Bank, recovery, Acme, CityCare, and evolved High Flight  
2. Model fields: `scenarioComplexity`, `presentationLens` (document Business/Technical; keep toggle labels)  
3. `IntentProfile` schema + YAML for live Intents  
4. Execute C7 High Flight replacement: ramp scanner subject, BRS/DCS on screen, new outcomes  
5. Unfulfilled qualified demand on the evolved airline trace if reachability blocks the scan  
6. Optional: shared interpreter spike behind one existing COMPOSED Intent (read-only parallel, not a fork)  

**Out:** `rollout_firmware_safely`, Demand Map, SalesScenarioProfile loader, MCP, auth fail-closed, catalog expansion, Meta_Demo, Jigyasa.

**Sales test when C10 is done:** Open High Flight and NV back-to-back. Both should answer “what did the enterprise already know, what was the gap, what did the network uniquely add.” If High Flight still looks like “expedite because the bag might miss the flight,” C10 has failed.

---

**STOP. Do not implement Cadence 10 until this replan is explicitly approved.**
