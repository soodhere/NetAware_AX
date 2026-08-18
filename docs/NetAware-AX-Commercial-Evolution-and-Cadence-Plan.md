# NetAware AX — Commercial Evolution & Cadence Plan

**Status:** Research / analysis only. **Not approved for implementation.**  
**Baseline:** `0.6.1-ax6.1` (Cadence 6.1 presentation freeze). Treat as the stable deployed demo.  
**Write:** NetAware_AX only.  
**Read-only reference:** Meta_Demo (not present in this workspace; used via Cadence 0 audit and prototype plan).  
**Do not touch:** Jigyasa.  
**This document does not start Cadence 7.**

---

## 1. Executive recommendation

NetAware AX should become a **sales-configurable demonstration of the real NetAware product model**, not a larger catalogue of executable Explorer rows and not a generic agent platform.

The next commercial leap is not “more scenarios.” It is making three things undeniable in a customer meeting:

1. **Capability discovery** — how NetAware decides what it can do for *this application, right now*.
2. **NV1 vs NV2** — same Intent (`VERIFY THIS MOBILE NUMBER`), different fulfillment because of access type and **operator entitlement-server readiness**.
3. **A high-volume fleet story** — OTA / device management that generates believable Network API consumption without forcing QoD.

**Recommended live portfolio (smallest covering the six commercial stories):**

| Story | Live vehicle | Disposition |
| --- | --- | --- |
| Volume / identity | Rocket Bank `assess_network_trust` | **KEEP** |
| Operator-readiness | Same Rocket Bank enterprise; new Intent `verify_mobile_number` with cellular vs Wi-Fi seeds | **ADD** |
| Governance / minimization | CityCare pharmacy age | **KEEP** |
| Closed-loop ACT | Acme Manufacturing inspection QoD | **KEEP** |
| Fleet / volume | New application under Acme: Device Fleet OTA | **ADD** |
| Cross-domain operations | High Flight **evolved** to ramp-scanner / connected ground handling | **IMPROVE** (do not keep current baggage opener as hero) |

**Do not add** retail checkout, a second manufacturing QoD, AGV, turnaround video, or KYC Match as live heroes. They overlap or fail the Network API contribution test.

**Do not expand `AX_ACTIVE_CATALOG`.** Current 13 families cover the recommended live set. Access type should come from runtime context, not a new CAMARA family. Entitlement-server readiness is operator infrastructure discovered by Telco Finder, not a catalogue API.

**Critical spec correction (closes Cadence 0 `NEEDS_REVIEW`):**  
NV1 and NV2 are **authentication / fulfillment paths**, not `phoneNumberVerify` vs `phoneNumberShare`. Binding NV2 to `phoneNumberShare` is commercially wrong. See §12.

**Cadence order (not the sketch in the brief):**

| Cadence | Why this order |
| --- | --- |
| **7** | Lock models (DPV, TMF931, NV paths, discovery stages, High Flight decision, OTA shape, sales-profile schema). No major UI. |
| **8** | Capability Discovery as a product surface + Basic/Advanced lenses on *existing* heroes. Biggest visible leap. Demote High Flight from opener. |
| **9** | NV1/NV2 live + entitlement-server unavailable path. Operator-meeting weapon. |
| **10** | Device Fleet OTA live. Volume weapon. |
| **11** | High Flight ramp-scanner evolution + YAML sales scenario profiles. |
| **12** | Presentation freeze + hosted sales baseline. |

**First next implementation cadence, after approval:** Cadence 7 only.

Would Sales want this before a major meeting? **Yes — if Cadences 8–10 land.** Cadence 6.1 is already a credible product demo; it is not yet a sales weapon because discovery is implicit, NV1/NV2 is mis-modelled, High Flight’s network contribution is weak, and there is no high-volume fleet story.

---

## 2. Interpretation of feedback

The feedback is not a request for more theatre. It is a request to make AX **commercially selectable**.

| Feedback | What it really means | What it does *not* mean |
| --- | --- | --- |
| More commercial use cases | Different *buyers, volumes, and Network API jobs* | Make Explorer rows executable |
| NV1 and NV2 first-class | Operator-readiness story that changes fulfillment | Two catalogue families, or verify vs share |
| Capability discovery as hero | NetAware’s product brain, visualized | Another decision-trace tab with more jargon |
| High Flight review | The Network API must *change a business action* | More airline copy on the same seed |
| Device OTA high priority | Believable API volume + agentic loop | Force QoD onto firmware |
| Manufacturing | Keep the strong closed-loop; don’t clone it | Latency→QoD as a franchise |
| Sales portfolio | Six *stories*, few *live engines* | One demo per industry |
| Basic vs Advanced | One trace, two lenses | Two implementations |
| Sales configuration | YAML profile before a meeting | Admin UI / CMS |
| DPV 2.3 | Purpose is governance vocabulary | Invent DPV IDs; conflate Intent with Purpose |
| TMF931 | Onboarding/order vs AX vs runtime | Force Agent/Intent/Autonomy into TMF931 |
| Catalog discipline | Small CURRENT_FOCUS set is a sales strength | Admit APIs because they look complete |
| Hosting hardening | Presenter-safe Render | Product feature |

**North-star test used throughout:** before an operator, aggregator, or enterprise meeting, would Sales ask to configure *this* demo for *that* audience because it explains the use case better than slides?

---

## 3. Current-demo strengths

Cadence 6.1 already beats Meta_Demo on domain entry and complementarity. Keep these.

| Strength | Why it is commercially valuable |
| --- | --- |
| Tiny request / huge configured context | Proves onboarding is the product, not the runtime payload |
| Deterministic simulation | Demo-safe; Sales can skip/replay; no LLM theatre |
| Real CAMARA `operationId`s | Credible to operator/API experts |
| Live who-called-whom | Makes AX feel executed, not narrated |
| Available vs invoked vs considered vs not required | Economy of APIs — the adoption argument |
| Why / why-not decisions | Policy is operational, not a slide |
| Evidence reuse (Rocket Bank recovery) | API economy + agentic memory |
| Replan (High Flight location block) | Agent inside an envelope |
| Closed-loop verify (Acme) | Observe → act → verify; the ACT story |
| Bounded autonomy | Enterprise owns bank/ops/pharmacy decisions |
| Telco Finder / API Finder | Existing NetAware assets, visible |
| 13-family pinned catalog | “Small practical set, many domains” is the DX→AX thesis |
| Cadence 6.1 value framing | My world → Network adds → NetAware AX → Intent |
| Honesty labels | Simulated, fictional, not production-claimed |
| Explorer as product graph | Reverse from `checkSimSwap` / `createSession` / `verifyAge` |
| Direct / aggregated / hybrid routes | Topology-neutral; hosting not locked |
| CityCare minimization | Governance story: assertion, not KYC dump |
| Basic Auth already exists when `DEMO_USERNAME` / `DEMO_PASSWORD` are set | Hosting path is started, not finished |

Meta_Demo remains the floor: those concepts must stay. AX’s job is to go *beyond* them by attaching them to NetAware assets and to Sales-configurable commercial stories.

---

## 4. Current-demo weaknesses

| Weakness | Commercial cost |
| --- | --- |
| Capability selection is implicit in per-scenario Python + seed YAML | Experts cannot *see* NetAware figuring out what it can do |
| Subscription and entitlement are collapsed (`entitlement: YES if subscribed`) | Operator/product story is wrong |
| NV1=`phoneNumberVerify`, NV2=`phoneNumberShare` is still `NEEDS_REVIEW` and is the wrong axis | Operator-readiness story cannot be told honestly |
| No access-type or entitlement-server model | Wi-Fi vs cellular is not a runtime dimension |
| High Flight opener: network confirms “not the limiter,” domain APIs already justify expedite | Viewers ask “what did the Network API contribute?” |
| No high-volume fleet / OTA story | Operators cannot see consumption at 10⁴–10⁵ calls |
| Four live enterprises, similar “one intent, one run” shape | Portfolio feels like four canvases, not a product |
| No Basic vs Advanced lens | Sales drown experts in `operationId`s, or experts never see DPV/policy |
| No sales scenario profile | Engineering is required before every serious meeting |
| Purpose IDs are AX-invented (`payment_fraud_assist`) | Misaligned with TMF931 `dpv:*` and CAMARA purpose |
| Explorer breadth > live differentiation | Risk of looking like a catalogue portal |
| High Flight is still presentation-order #1 | Weakest network-contribution hero is the default opener |
| Hosted demo: `BUILD_ID` still `ax6`; credentials optional; no presenter-safe seed/reset contract | Not yet a sales-hosted baseline |
| Runtime is still one interpreter *plus* large per-intent functions | New scenarios still feel like new engines |

**The academic risk:** Explorer + 21 use cases + CAMARA maturity dimensions can look like a standards museum. Basic mode must hide that. Advanced mode must use it as *proof*, not as the plot.

---

## 5. Existing-product alignment

AX must read as **an intelligent layer over NetAware**, never as a replacement product.

| Concept | Existing NetAware asset | AX extension |
| --- | --- | --- |
| Enterprise / Application | Application / enterprise onboarding | Agent as authorized principal *on behalf of* Application |
| Purpose | Onboarding / API grant purpose | DPV 2.3 identifier + scenario context; Intent ≠ Purpose |
| Policy / security | Policy, auth, consent | Runtime evaluation that *changes the plan* |
| Agreement / DPA | Contract / terms on API product | Configured agreement gate (`AGREEMENT_GAP`) |
| Subscription | API product order | Filter `NOT_SUBSCRIBED` |
| Entitlement | What the app may actually invoke (narrower than subscription) | Split from subscription; `NOT_ENTITLED` |
| API Catalog | Pinned CURRENT_FOCUS families | Capability mapping; never invent `operationId`s |
| Telco Finder | Home/serving network resolution | Input to path selection (NV, OTA cohort, High Flight device) |
| API Finder | Which operations exist on that network | Candidate generation for discovery |
| Provider / routing | Direct / aggregated / hybrid | Route shown as *where it will be invoked* |
| CAMARA invocation | Southbound call | Plan step + evidence + correlation |
| Observability / OAM | Trace, who-called-whom | Decision trace + discovery funnel + Basic/Advanced lenses |
| Intent | **AX-specific** | Outcome without naming APIs |
| Capability discovery | Implicit today | **Hero AX extension**, built from the assets above |
| Autonomy | **AX-specific** | Envelope: OBSERVE / RECOMMEND / ACT_WITH_APPROVAL / ACT |
| Evidence reuse | Traceability + cache-like OAM | `EVIDENCE_REUSED` as an execution state |
| Plan / replan / verify | Orchestration patterns | Visible agent loop |
| NV1/NV2 path | Number Verification product + TS.43 entitlement story NetAware already sells | Runtime discovery of access type + entitlement server |
| Sales scenario profile | Configuration, not a new engine | YAML instance of the model Sales already has |

**Line to use with customers:**  
AX does not replace the catalogue, onboarding, subscriptions, Telco Finder, or invocation. It decides *whether, which, and why* those assets fire for an Intent.

---

## 6. Commercial thesis

Network APIs sell when they do one of three jobs the enterprise cannot do itself:

1. **Verify** something only the operator knows (number possession, SIM/device continuity, age assertion).
2. **Observe** network state the enterprise application does not have (reachability, roaming, connectivity).
3. **Act** on the network when that state is the limiter (QoD) — rarely, and only then.

AX increases consumption when it:

- selects the *minimum* permitted capability (CityCare);
- selects the *available path* (NV1 vs NV2);
- *does not* call APIs that are not required or not allowed;
- *reuses* evidence;
- *segments* a fleet so the enterprise OTA system only pushes when the network says it will work;
- makes that selection inspectable so an operator architect trusts it.

**Sales message by audience**

| Audience | Message |
| --- | --- |
| Enterprise buyer | Keep your application. Express the outcome. Get network evidence/action you cannot produce. |
| Operator | AX turns onboarding + catalogue into *repeatable invocation*, including Wi-Fi Number Verification if your entitlement server is ready. |
| Aggregator | Same Intent, hybrid routes, operator-specific prerequisites filtered in one place. |
| Sales | Configure industry / region / topology / problem in YAML; do not wait for a new engine. |

If a scenario only shows “the agent called two APIs in order,” it is DX with nicer labels. Kill it as a hero.

---

## 7. Research findings

### 7.1 CAMARA Number Verification 2.1.0 (pinned)

Source: `openapi/camara/NumberVerification__number-verification.yaml` (CAMARA 2.1.0).

Two **operations** (both require a 3-legged token; no SMS OTP / password):

| `operationId` | HTTP | Job |
| --- | --- | --- |
| `phoneNumberVerify` | `POST /verify` | App already has a claimed MSISDN (plain or hashed). Returns true/false. |
| `phoneNumberShare` | `GET /device-phone-number` | Returns the MSISDN bound to the access token so the app can match itself. |

Two **authentication methods** (this is the NV1/NV2 axis):

| Method | Spec language | Prerequisite |
| --- | --- | --- |
| Network-based | Operator identifies the subscriber on the mobile connection. OIDC Authorization Code, `prompt=none`. Device **must be on mobile network**. | Cellular access; operator can bind the session to the SIM/MSISDN. |
| SIM-based (TS.43) | Temporary operator token from GSMA TS.43 / ASAC. CIBA `login_hint=operatortoken:…` or JWT-bearer `sub=operatortoken:…`. **Works over Wi-Fi.** | Device TS.43 client; **operator Entitlement Configuration Server** that issues Operator Token; OS/SIM support. |

GSMA and industry usage (“NV1” vs “Number Verify 2 / NV2 / Operator Token”) maps to **auth path**, not to verify vs share. GSMA Identity (2026) is explicit: NV2 needs entitlement servers; many operators do not have them; OS support is uneven (Android ahead; iOS called out as coming). That is the NetAware commercial wedge.

**Do not implement the brief’s simplified model blindly.** Cellular → `phoneNumberVerify` and Wi-Fi → `phoneNumberShare` is not what the spec says. Both operations can be used with either auth path. Verify vs share is a *claim-shape* decision (does the application already know the number?).

### 7.2 Entitlement server / TS.43

- TS.43 is Service Entitlement Configuration between a device client and the operator **Entitlement Configuration Server (ECS)**.
- Open Gateway Number Verification over non-cellular uses the Operator Token produced in that ecosystem.
- Token acquisition on the device is **out of scope of the CAMARA API**.
- NetAware’s published TS.43 story is aligned: middleware maps operator token into Open Gateway Number Verification so the enterprise sees a consistent verification outcome.
- Failure mode that matters commercially: **NV2 indicated, ECS unavailable / not entitled / OS cannot obtain token → capability unavailable**, not a silent fallback that pretends NV1 worked on Wi-Fi.

### 7.3 DPV 2.3 Purpose

Source: [W3C DPV 2.3 Purposes](https://w3c-cg.github.io/dpv/2.3/dpv/modules/purposes.html).

Intent remains the requested outcome. Purpose is why processing is performed. Do not invent IDs. Use `https://w3id.org/dpv#…`.

TMF931 v5.2.1 `DpvPurposeType` is a **DPV v2.0-era enum**. It includes `AgeVerification`, `FraudPreventionAndDetection`, `IdentityAuthentication`, `IdentityVerification`, `ServiceOptimisation`, `ServiceProvision`, `RepairImpairments`, `RequestedServiceProvision`, `IncreaseServiceRobustness`, `ImproveExistingProductsAndServices`. It does **not** include DPV 2.3 additions `ServiceManagement` / `ServiceMonitoring` / `ServiceAccessDetermination`. Prefer TMF931-overlapping IDs for onboarding alignment; if a 2.3-only term is truly better, mark it `TMF931-INSPIRED / EXTENSION`.

### 7.4 TMF931 (not TMF921)

Source: TMF931 Open Gateway Onboarding and Ordering Component Suite v5.2.1.

TMF931 is Channel Partner ↔ Operator **onboarding and API product order**. Resources: `applicationOwner`, `application`, `apiProduct`, `apiProductOrder`. `ApiGrantInformation` carries `purpose` (DPV), `scope`, `grantType`, `legalBasis`. Agreements are referenced on products/orders.

TMF931 is **not** Intent Management (TMF921). Do not force Agent, Intent, Autonomy, evidence, replan, or capability-discovery pipeline into TMF931.

### 7.5 Airline / airport operations

Bags are tracked by **BRS / BHS / DCS / AODB** and IATA RP 1745 messages (BSM, BPM, BTM, BMM) plus Reso 753 custody events. Physical bag position is an **airline/airport system fact**, not a Network API fact.

Ramp handlers use **ruggedized handhelds over Wi-Fi/4G** to scan bags into ULDs. If the scanner cannot reach BRS, custody events stop even if the bag is moving. That is a credible Network API job: reachability/connectivity of the **operational device**, not location of the luggage.

### 7.6 Device management / OTA

Enterprises already have inventory, twin, firmware campaign, telemetry (LwM2M Object 5, Azure Device Twin, AWS IoT Jobs, etc.). The network does not flash firmware. The network tells the campaign manager **which devices can receive a payload now** (reachable on DATA, not roaming-excluded, connectivity adequate). CAMARA Device Reachability Status 1.1.0 is explicitly positioned for IoT fleet management. Volume is the commercial point.

### 7.7 Catalog honesty

Current active catalog already includes Number Verification, SIM/Device Swap, Reachability, Roaming, Location, QoD, Connectivity Insights, Edge, Age Verification, KYC Match. That is enough for the recommended live set. Experimental Insights/Profiles and Age Verification stay labelled honestly.

---

## 8. Candidate scenario matrix

| ID | Scenario | Buyer | Pain | Network job | Volume profile | Distinct vs others |
| --- | --- | --- | --- | --- | --- | --- |
| RB-TRUST | High-value payment protection | Bank fraud / risk | Auth succeeded, SIM/device may have changed | Verify continuity | Per high-value txn | Identity volume + selective evidence |
| RB-NV | Verify mobile number (NV1/NV2) | Bank IAM / operator | Silent auth on cellular *and* Wi-Fi | Path selection | Login / onboarding / recovery | Operator-readiness |
| RB-RECOVERY | Account recovery reuse | Bank IAM | Don’t re-call APIs | Evidence reuse | Per recovery | Companion, not a fifth hero |
| CC-AGE | Pharmacy age gate | Health / retail compliance | Need 18+ assertion, not KYC dump | Min capability | Per restricted sale | Governance |
| ACME-QOD | Inspection camera SLO | Plant quality | Network is the limiter | Observe → QoD → verify | Per session / line | Closed-loop ACT |
| ACME-OTA | Firmware 8.4 to fleet | OEM / IoT / utilities | Don’t brick / waste campaign | Segment by network state then call enterprise OTA | 10⁴–10⁵ devices | Fleet volume |
| HF-BAG | Baggage connection (current) | Airline ops | Missed connection | Weak: confirm network is *not* limiter | Per bag | Overlaps domain systems |
| HF-RAMP | Ramp-scanner assurance | Airline / ground handler | Silent scan failure | Reachability of handler device | Devices × turns × stations | Cross-domain, unique network |
| HF-TURN | Turnaround video | Airport | Video SLO | QoD/edge | Per turnaround | Clone of Acme |
| M-PRED | Predictive maintenance | Plant / OEM | Machine offline | Reachability | Per asset poll | Weaker uniqueness |
| M-AGV | AGV fleet | Plant | Latency | QoD | Per vehicle | Clone of Acme |
| LOG-FLEET | Logistics handhelds | 3PL | Drivers offline | Reachability/roaming | Per stop | Fold into OTA pattern |
| RET-CHECK | Checkout trust | Retail | Card present fraud | Same as RB-TRUST | High | Duplicate identity story |
| RET-AGE | Age-restricted POS | Retail | Age gate | Same as CityCare | High | Duplicate governance |
| KYC | KYC Match | Bank onboarding | Attribute match | KYC Match | Onboarding | Privacy-hostile as hero |
| LOC-BAG | Locate baggage | Airline | Find bag | Location retrieval | Exceptions | Consent-heavy; Explorer |

---

## 9. Commercial scoring / ranking

Scores 1–5. Weights emphasise commercial dimensions (volume, operator monetization, unique network value, sales relevance, willingness to pay). Implementation effort: 5 = already live / cheap.

**Weights:** Pain 1.2 · Volume 1.5 · WTP 1.3 · Operator $ 1.5 · Unique network 1.4 · Agentic 1.1 · Clarity 1.2 · Catalog ready 1.0 · Cross-operator 1.0 · Sales 1.4 · Effort 0.8. Max 67.0.

| Rank | Scenario | Pain | Vol | WTP | Op$ | Uniq | Agt | Clr | Cat | Xop | Sales | Eff | Weighted | Live? |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | RB-TRUST | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 5 | 66.3 | KEEP |
| 2 | RB-NV | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 4 | 5 | 5 | 3 | 63.2 | ADD |
| 3 | ACME-OTA | 5 | 5 | 4 | 5 | 4 | 5 | 4 | 5 | 5 | 5 | 3 | 61.5 | ADD |
| 4 | ACME-QOD | 4 | 3 | 4 | 4 | 5 | 5 | 5 | 4 | 3 | 4 | 5 | 55.6 | KEEP |
| 5 | HF-RAMP | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 4 | 4 | 4 | 54.6 | IMPROVE |
| 6 | CC-AGE | 4 | 3 | 4 | 3 | 5 | 4 | 5 | 3 | 3 | 4 | 5 | 52.0 | KEEP |
| 7 | RET-CHECK | 3 | 5 | 4 | 4 | 4 | 2 | 4 | 5 | 5 | 3 | 4 | 52.3 | Explorer (overlap) |
| 8 | RET-AGE | 4 | 4 | 4 | 3 | 5 | 3 | 4 | 3 | 3 | 4 | 4 | 50.4 | Explorer (overlap) |
| 9 | LOG-FLEET | 4 | 4 | 3 | 4 | 4 | 3 | 3 | 5 | 4 | 3 | 3 | 48.8 | Explorer / profile remap |
| 10 | M-PRED | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 5 | 4 | 3 | 3 | 44.4 | Explorer |
| 11 | HF-BAG (current) | 4 | 2 | 3 | 2 | 2 | 4 | 2 | 5 | 4 | 3 | 5 | 41.5 | Demote |
| 12 | M-AGV | 3 | 3 | 3 | 4 | 3 | 3 | 2 | 4 | 3 | 2 | 3 | 40.1 | Explorer only |
| 13 | HF-TURN | 3 | 2 | 3 | 3 | 3 | 3 | 2 | 4 | 3 | 2 | 4 | 37.9 | Explorer only |
| 14 | KYC | 3 | 2 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 37.6 | Explorer only |

Retail checkout scores well on volume but **fails uniqueness of story** versus Rocket Bank. Do not promote.

---

## 10. Recommended live scenario portfolio

**Five live runs, four enterprises, six commercial stories.** Recovery remains a companion, not a hero card.

### 10.1 Rocket Bank — Volume + identity (KEEP)

- **Buyer:** Bank fraud / risk / digital.
- **Already has:** Payments, core banking, IAM, fraud decisioning.
- **Network adds:** Number possession, SIM/device continuity, roaming — facts the bank cannot see.
- **Why AX > static integration:** Selective invocation, location blocked without consent, recycling NOT_REQUIRED, enterprise owns STEP_UP.
- **Agentic:** Policy-filtered plan; not a fixed A→B chain.
- **Volume:** High-value txn + (later) login/NV. Operator cares: identity APIs are the deployed Open Gateway money.

### 10.2 Rocket Bank — NV1/NV2 (ADD, same enterprise)

- **Intent:** `verify_mobile_number` — “verify this mobile number.”
- **Seeds:** (A) cellular / NV1 path available; (B) Wi-Fi / NV2 path; (C) Wi-Fi / ECS unavailable.
- **Buyer:** Bank IAM *and* operator product (entitlement-server readiness).
- **Already has:** Claimed MSISDN in the app.
- **Network adds:** Silent possession check that SMS OTP cannot equal; Wi-Fi coverage only if operator ECS is ready.
- **Why AX > static:** Application does not hardcode NV1 vs NV2. NetAware discovers access, operator, NV support, ECS, then selects.
- **Agentic:** Context-driven path selection + explicit failure.
- **Do not** make this a sixth enterprise.

### 10.3 CityCare — Governance (KEEP)

- **Buyer:** Pharmacy / compliance / privacy officer.
- **Network adds:** Age assertion only.
- **Why AX:** KYC Match subscribed maybe, **not entitled / denied for this purpose**. Minimum capability.
- **Volume:** Lower than NV/OTA; keep because it is the only minimization hero.
- **Maturity honesty:** Age Verification experimental — already labelled.

### 10.4 Acme Manufacturing — Closed-loop (KEEP)

- **Buyer:** Plant quality / OT.
- **Network adds:** Connectivity observe + QoD act when SLO breached.
- **Why AX:** Intent was experience, not `createSession`. Verify after act.
- **Do not clone** this pattern into AGV, turnaround, telehealth as live heroes.

### 10.5 Acme Device Fleet — OTA (ADD)

- **Enterprise:** Keep **Acme Manufacturing** as Application Owner; add Application **Device Fleet** (not a new brand unless Sales profile remaps to automotive OEM).
- **Buyer:** OEM / fleet / manufacturing IT. Sales profile can relabel industry to Automotive.
- **Intent:** `rollout_firmware_safely`.
- **Already has:** Inventory, twin, firmware service, campaign manager, telemetry.
- **Network adds:** Reachability (DATA vs SMS vs unreachable), roaming, optionally connectivity. **QoD not default.** Location only if campaign is geo-constrained (NEEDS_REVIEW; default off).
- **AX loop:** Discover → Segment → Plan cohort → Act via **enterprise OTA API** → Observe → Replan (expand / defer / retry) → Verify campaign counts.
- **Volume:** 100k targeted → tens of thousands of Reachability (+ Roaming) calls. This is the operator consumption slide.
- **Agentic:** Cohort segmentation + conditional enterprise action + replan. Not “call API A then B.”

### 10.6 High Flight — Cross-domain (IMPROVE, Cadence 11)

See §18. Live hero becomes **ramp-scanner / connected ground handling**. Current baggage-connection demoted to Explorer.

### 10.7 Demo order (from Cadence 8)

1. Rocket Bank (zero-context opener; identity unique value is obvious).  
2. Acme QoD or NV1/NV2 depending on audience (sales profile).  
3. CityCare if governance/privacy audience.  
4. OTA if operator volume / OEM audience.  
5. High Flight if airline / cross-domain audience (after evolution).

Until High Flight evolves, **do not open with it.** Cadence 6.1 already said this; Cadence 8 should make it the default picker order.

---

## 11. Explorer-only portfolio

Keep Explorer as leverage proof (“one catalog, many domains”). Do **not** execute these.

| Use case | Why Explorer only |
| --- | --- |
| Locate baggage | Location ≠ bag position without a tracked device + consent; easy to over-claim |
| Airside asset presence | Geofence/consent; overlaps ramp device story |
| Turnaround video | Acme clone |
| Equipment on site | Presence pattern; weak vs OTA/ramp |
| Site uplink | QoD clone |
| Shipment custody | Location over-claim risk |
| Dock scan session | QoD clone / overlaps ramp |
| Checkout trust | Rocket Bank identity duplicate |
| Claim device trust | Identity duplicate |
| Claim location | Consent-heavy |
| Telehealth | Acme clone; clinical over-claim risk |
| Home-care visit | Geofence/consent |
| Live broadcast | Niche; QoD |
| Venue experience | Niche |
| Age-restricted sale | CityCare duplicate |
| KYC attribute match | Privacy-hostile as hero; DPA/consent theatre |
| Predictive maintenance | Weak uniqueness (reachability only) |
| AGV fleet | Acme clone |
| Current baggage-connection | After High Flight evolution |

Explorer should stay a **graph**, not a second demo product. Cadence 8 Basic mode should not land users in Explorer first.

---

## 12. NV1/NV2 model

### 12.1 Product labels (for Sales / operators)

| Label | Meaning in this plan | Not |
| --- | --- | --- |
| **NV1** | Network-based Number Verification. Device on cellular. Operator identifies the subscription from the mobile access. | `phoneNumberVerify` |
| **NV2** | SIM-based / Operator Token Number Verification. TS.43 token from operator entitlement server. Works on Wi-Fi (and cellular). | `phoneNumberShare` |

### 12.2 Runtime decision model (proposed)

```
INTENT: verify_mobile_number
  → CAPABILITY: number_possession_verification
  → RESOLVE claimed MSISDN? (yes → prefer phoneNumberVerify; no → phoneNumberShare)
  → DISCOVER ACCESS TYPE     (runtime context from app/SDK: CELLULAR | WIFI | VPN | UNKNOWN)
  → TELCO FINDER             (home / serving network)
  → DISCOVER OPERATOR NV SUPPORT
        NV1_NETWORK_BASED?
        NV2_OPERATOR_TOKEN?
  → DISCOVER ENTITLEMENT SERVER   (operator readiness: AVAILABLE | UNAVAILABLE | UNKNOWN)
  → DISCOVER TECHNICAL PREREQS    (SIM present, TS.43 client, 3-legged token path)
  → FILTER → RANK → SELECT PATH → SELECT OPERATION → SELECT ROUTE → INVOKE
```

### 12.3 Path table

| Access | NV1 ready | NV2 ready | ECS | Selected | Outcome |
| --- | --- | --- | --- | --- | --- |
| CELLULAR | yes | * | * | **NV1** | Invoke Number Verification via network-based token; operation from claim-shape |
| CELLULAR | no | yes | available | **NV2** | Fallback to operator token |
| WIFI | * | yes | available | **NV2** | Operator token path |
| WIFI | * | yes | **unavailable** | none | `ENTITLEMENT_SERVER_UNAVAILABLE` — capability unavailable; no fake NV1 |
| WIFI | * | no | * | none | `ACCESS_TYPE_INCOMPATIBLE` / `TECHNICAL_PREREQUISITE_MISSING` |
| VPN | treat as non-cellular | same as Wi-Fi | | | Do not pretend header enrichment works |

### 12.4 Operation selection (orthogonal)

| Application already has MSISDN? | Operation |
| --- | --- |
| Yes (typical bank login / recovery) | `phoneNumberVerify` |
| No (onboarding “tell me the number”) | `phoneNumberShare` |

Rocket Bank NV demo should use **verify** (claimed number exists). Show `phoneNumberShare` as considered/not-required, not as “the Wi-Fi API.”

### 12.5 What the demo must not say

- Reachability or SIM Swap is NV.
- NV1 is CAMARA `/verify` and NV2 is `/device-phone-number`.
- Wi-Fi Number Verification works without operator ECS.
- OTP SMS is an NV path (CAMARA Number Verification forbids user-interaction auth).

### 12.6 Catalog

Remain **one** Number Verification family. Relabel operations: remove productLabel NV1/NV2 from verify/share. Add path metadata on the **capability**, not on the operations.

### 12.7 NEEDS_REVIEW (close in Cadence 7, implement in 9)

1. Exact simulated token path (CIBA vs JWT-bearer) — show as Advanced-only, do not over-animate crypto.
2. Whether Telco Finder can know ECS readiness from a configured operator profile (yes for demo) vs a live CAMARA “capabilities” API (do not admit CapabilitiesAndRuntimeRestrictions casually).
3. iOS readiness — honesty footnote, not a blocker for the simulated demo.

---

## 13. Entitlement-server model

The entitlement server is **operator infrastructure**, not an AX catalogue family and not a CAMARA Number Verification resource.

| Field (operator profile) | Source |
| --- | --- |
| `entitlementServer.available` | Configured operator readiness (Sales-profile / seed). Runtime-discovered in production later. |
| `entitlementServer.supportsOperatorToken` | Configured |
| `ts43.clientAvailable` | Runtime context / device capability (simulated) |
| `nv2Supported` | Derived: ECS available ∧ operator advertises SIM-based NV |

**Filter reason:** `ENTITLEMENT_SERVER_UNAVAILABLE`.

**Commercial line:** NetAware is pushing operators to be ECS-ready because **Wi-Fi is where consumer auth actually happens**. AX shows the application Intent succeeding or failing *because of that readiness*, without the bank coding TS.43.

**Failure visualization (required live beat):** Wi-Fi + NV2 needed + ECS down → plan shows NV1 filtered (`ACCESS_TYPE_INCOMPATIBLE`), NV2 filtered (`ENTITLEMENT_SERVER_UNAVAILABLE`), outcome `CAPABILITY_UNAVAILABLE` / alternate (e.g. enterprise falls back to its own IAM — **enterprise-owned**, not AX inventing SMS OTP).

Do not have AX send SMS OTP as a “clever agent.” That undermines the Number Verification product.

---

## 14. Capability-discovery model

Current runtime evaluates purpose, subscription, consent, and deny-rules **inside each scenario function**. That is not a product model.

### 14.1 Proposed stages (order)

Discovery is a **pipeline of filters on a candidate set**, not a flowchart of industries.

**Candidate generation (what *could* be relevant)**

1. **Catalog** — CURRENT_FOCUS families/operations (NetAware asset).  
2. **Intent mapping** — configured Intent → candidate capabilities (AX config).  
3. **Claim / subject type** — phone vs plant uplink vs scanner IMSI vs camera (runtime).

**Configured eligibility (what this application is allowed to use *in principle*)**

4. **Application / Agent authorization** — may this agent send this Intent?  
5. **DPV Purpose** — family permitted for this purpose?  
6. **Policy** — permit / deny / constrain.  
7. **Agreement / DPA** — purpose, region, residency.  
8. **Consent requirement** — required vs available (configured demo consent, not a legal engine).  
9. **Subscription** — API product ordered?  
10. **Entitlement** — app/agent actually granted? (must split from 9)

**Runtime feasibility (what can be done *right now*)**

11. **Region / country** — serving vs home.  
12. **Telco Finder** — operator / serving network.  
13. **API Finder** — operator/aggregator advertises the operation.  
14. **Provider / route** — DIRECT / AGGREGATED / HYBRID.  
15. **Access type** — cellular / Wi-Fi / VPN.  
16. **Operator prerequisites** — NV1/NV2, entitlement server, QoD support.  
17. **Technical prerequisites** — SIM, token class, device identifier type.  
18. **Existing evidence** — TTL / purpose / subject reuse.  
19. **Autonomy** — may we ACT or only OBSERVE/RECOMMEND?  
20. **Usefulness** — NOT_REQUIRED if it cannot change the outcome (High Flight QoD; recycling).

**Select**

21. Rank remaining (minimum sufficient, route preference, cost/budget if configured).  
22. SELECT → invoke or reuse.

Stages 1–10 are mostly **onboarding/config**. Stages 11–20 are **runtime discovery**. The demo must show that split. That is the TMF931 vs AX vs runtime story.

### 14.2 Filter reasons (canonical)

Use these codes in Advanced mode. Basic mode uses the human label only.

| Code | Meaning |
| --- | --- |
| `NOT_RELEVANT` | Not in Intent mapping / wrong subject type |
| `PURPOSE_NOT_PERMITTED` | DPV purpose does not allow family |
| `NOT_SUBSCRIBED` | No API product order |
| `NOT_ENTITLED` | Subscribed but this app/agent cannot use it |
| `CONSENT_MISSING` | Consent required and unavailable |
| `AGREEMENT_GAP` | DPA/terms do not cover purpose/region |
| `REGION_NOT_SUPPORTED` | Geography |
| `PROVIDER_NOT_AVAILABLE` | No route |
| `OPERATOR_NOT_SUPPORTED` | Telco Finder network does not offer it |
| `ENTITLEMENT_SERVER_UNAVAILABLE` | NV2 path blocked |
| `ACCESS_TYPE_INCOMPATIBLE` | e.g. NV1 on Wi-Fi |
| `TECHNICAL_PREREQUISITE_MISSING` | Token/SIM/OS |
| `EVIDENCE_REUSED` | Selected by reuse; invocation skipped |
| `NOT_REQUIRED` | Relevant and allowed; does not change outcome |
| `AUTONOMY_FORBIDS` | Outside envelope |
| `SELECTED` | Remaining winner |

Do not assume this order is frozen in UI animation. Cadence 7 should encode it as data. Cadence 8 may collapse adjacent stages for Basic (e.g. “Governance” = 5–10).

### 14.3 What was wrong with “just show mapping and runtime”

Mapping answers “what is *related*.” Runtime today answers “what the seed script did.” Discovery must answer **“what was considered, what died, why one path remains, where it will be invoked.”**

---

## 15. Capability-discovery visualization

### Recommendation

**Basic: layered pipeline (collapsed stages).**  
**Advanced: same pipeline + candidate matrix.**

Reject Sankey as the primary (hard to present live; looks like analytics, not a product). Reject a free-form decision graph as the default (academic). A funnel is acceptable as the Basic *shape* of the pipeline (wide → narrow) but should be **stages with counts**, not a marketing funnel chart.

### Basic mode (Sales / executive)

Five layers, each with a one-line verdict:

1. **Your application** — what it already knows / which Intent it sent.  
2. **What the network could add** — candidate capabilities in business words (Verify number, SIM continuity, Reachability…).  
3. **What governance allows** — purpose, policy, subscription.  
4. **What is possible right now** — this operator, this access, this device.  
5. **What NetAware selected** — capability + outcome implication, not `operationId`.

Each discarded item: one human reason (“Wi-Fi — cellular number verify not possible”).

### Advanced mode (CTO / operator / CAMARA)

- Expand layers 3–5 into the full filter list.  
- **Candidate matrix:** rows = capabilities/operations/paths; columns = stage results (`PERMITTED` / reason code); final column SELECTED / filtered.  
- Click a cell → policy/subscription/operator/ECS evidence.  
- Footer: API Finder + route (Direct / Aggregated / Hybrid) + `operationId` + spec version.

### Interaction

The pipeline is a **view of the same execution trace**, not a second engine. Every filter event is already a Decision. Cadence 8 adds a structured `discovery[]` array to the trace.

This should become the strongest visual in the product — stronger than Live Flow for operator meetings.

---

## 16. Basic vs Advanced UX

**Same engine. Same trace. Two presentation lenses.** Persist the toggle on Runtime (and Briefing). Default from sales profile; allow in-meeting switch.

| | Basic | Advanced |
| --- | --- | --- |
| Audience | Sales, exec, enterprise buyer | CTO, architect, operator, aggregator, CAMARA |
| Answers | Problem, existing systems, unique network add, Intent, decision, business outcome | Agent, DPV, policy, consent, DPA, subscription vs entitlement, region, discovery pipeline, Telco/API Finder, ECS, route, NV path, `operationId`, evidence, replan, verify |
| Tabs | Overview + Live Flow + Outcome | All current tabs + Discovery |
| Copy | Business verbs (Verify / Observe / Act) | Spec names |
| Catalog | Hidden unless asked | Pinned family + version + maturity dimensions (keep 6.1 honesty) |
| Explorer | Link “technical detail” | First-class |

**Do not duplicate scenario YAML.** Seed + interpreter stay one. Presentation layer reads `lens=basic|advanced`.

**90-second Basic script (any hero):**  
Problem → what we already know → what only the network can add → Intent (tiny JSON) → NetAware decided X because Y → outcome the enterprise owns.

---

## 17. Sales scenario configuration model

**YAML profile. No admin UI in Cadences 7–12.** Compelling UI reason does not exist yet: Sales will email Product a paragraph; Engineering (or a salesperson with git) copies a profile. A UI would look like a generic agent console.

### 17.1 `SalesScenarioProfile` (proposed)

```yaml
id: operator-cto-de-ota
audience: operator_cto          # sales | executive | enterprise | operator_cto | aggregator | camara
lensDefault: advanced
enterpriseId: acme-manufacturing
applicationId: acme-device-fleet
industryLabel: Automotive        # presentation remap; enterprise remains fictional Acme
region: DE
topology: aggregated_plus_direct
meetingGoal: show_ax_increases_api_consumption
businessProblem: OTA rollout for 500k devices
existingSystems: [Device management, Telemetry]
domainApis: [inventory, twin, ota-campaign]
intentId: rollout_firmware_safely
purpose:
  vocabulary: DPV
  id: dpv:ImproveExistingProductsAndServices
  label: Improve Existing Products and Services
  context: Safely stage firmware 8.4; network state gates campaign cohorts.
networkSubjectModel: device_msisdn
relevantCapabilities: [device_reachability, roaming_status]
providerTopology: { default: AGGREGATED, exceptions: [DE-operator-direct] }
subscriptions: [CONNECTIVITY, LOCATION_AND_MOBILITY]
entitlements: [device_reachability, roaming_status]
policyRef: acme-ota-policy
autonomy: { observe: ACT, invoke_qod: NOT_AUTHORIZED, call_enterprise_ota: ACT_WITH_APPROVAL }
scenarioSeed: acme-ota-de-500k
expectedOutcome: COHORT_GATED_ROLLOUT
commercialMessage: >
  AX turns reachability/roaming into campaign control, so operators see
  volume and OEMs do not push firmware into unreachable or roaming-excluded devices.
demoMode: advanced
```

Profiles **select and label** existing model objects. They must not introduce a parallel engine. Unknown `intentId` / missing seed → fail closed.

Cadence 11 implements loading a profile. Cadences 8–10 only reserve the schema (Cadence 7 writes the schema file as documentation/config stub, unused by runtime until 11).

---

## 18. High Flight recommendation

**Do not keep current baggage-connection as a hero.**

### Why the current scenario fails the contribution test

| Question | Current answer | Verdict |
| --- | --- | --- |
| What does the enterprise already know? | Bag journey, last scan, flight window, ground ETA | Strong domain story |
| What unique thing does the network add? | Handler device reachable; connectivity adequate | True but **does not change the action** |
| Why did NetAware need that? | To test if network was the limiter | Honest, weak |
| What business decision changes? | Expedite transfer — **already implied by ETA > margin** | **Fail** |

Reachability is not location. Connectivity is not bag position. Cadence 6.1 copy is correct and still leaves the viewer asking “so what?”

### Alternatives evaluated

| Option | Verdict |
| --- | --- |
| Keep baggage-connection, more copy | **No** — copy cannot fix a contribution fail |
| Locate baggage via Location API | **No** — implies Network = bag GPS |
| Turnaround video | **No** — Acme clone |
| Gate/boarding device assurance | Credible; narrower buyer; similar to scanner |
| **Ramp-worker / BRS scanner connectivity during a tight transfer** | **Yes — recommended live** |
| Connected ground handling (fleet of scanners + vehicles) | Good later; too big for one cadence |

### Recommended live: ramp-scanner assurance

- **Device:** Ruggedized BRS handheld `HF-HDL-0192` used by a ramp agent.  
- **Who:** Ground handler scanning bags into the ULD for HF281 (IATA Reso 753 custody).  
- **Why network state matters:** If the scanner is not reachable on DATA, **scan events never reach BRS/DCS**. The airline’s bag picture goes stale. That is a different failure mode from “belt is slow.”  
- **Business action that changes:** Swap device / reassign a live handler / hold load-close / proceed only with confirmed DATA reachability.  
- **Domain APIs:** BRS scan session, DCS/BSM-BPM style bag-flight match, AODB/flight status.  
- **Network APIs:** `getReachabilityStatus` (DATA vs SMS vs unreachable), `getRoamingStatus` if contractor SIM, `checkNetworkQuality` if reachable but failing uploads. QoD **only if** network quality is the limiter for scan upload — not default. Location **off** unless a later consent story.  
- **Intent (working name):** `assure_ramp_scan_capability` (final ID in Cadence 7).  
- **Keep High Flight Airlines brand.** Change Application from “Baggage Operations as bag tracker” to **Ground Handling / BRS**.

Until Cadence 11, **demote High Flight from opener** (Cadence 8 picker order) and keep the current run as optional/Explorer-adjacent so we do not churn the frozen demo before the model lands.

**NEEDS_REVIEW:** Exact Intent ID and whether last bag scan remains *context* (domain evidence) beside the scanner-device subject. Recommendation: yes — domain APIs still show *why the turn is tight*; network APIs show *whether the operational device can do the work*.

---

## 19. Device-management / OTA recommendation

**Promote to live. Highest new commercial value after NV1/NV2.**

### Commercial

- **Who buys:** OEM (automotive, CPE, industrial IoT), sometimes the operator’s IoT unit.  
- **Pain:** Failed OTA on unreachable/roaming devices wastes campaign window, support cost, and (in auto) safety/compliance risk.  
- **Operator care:** Reachability + roaming at fleet scale is **real CAMARA volume**, unlike one QoD session per camera.  
- **Enterprise already has:** The OTA stack. AX must call a simulated campaign API, not pretend NetAware flashes firmware.

### Network contribution test — PASS

| Question | Answer |
| --- | --- |
| Already knows | Inventory, firmware version, campaign targeting, telemetry if device last called home |
| Network unique | *Current* operator view: reachable on DATA? roaming? (enterprise last-seen is not the same) |
| Why NetAware | Gate the enterprise OTA API; don’t push into a black hole |
| Decision that changes | Cohort A now, defer roaming, retry unreachable later |

### Agentic properties (required)

DISCOVER device/network state → SEGMENT (reachable DATA / SMS-only / unreachable / roaming / policy-excluded) → PLAN cohort → ACT (enterprise `createOtaCampaign` / `startWave`) → OBSERVE → REPLAN expand/defer/retry → VERIFY counts.

QoD: **not** in the default plan. Admit only if a future profile has a time-critical download SLO *and* QoD is entitled. Do not force it.

Location: default **NOT_REQUIRED**. Optional later for “home-country only” campaigns — consent/purpose heavy; Explorer or profile flag, not hero default.

Edge: **not** for OTA.

### Catalog

**Sufficient:** Reachability, Roaming, optionally Connectivity Insights.  
**Gap (do not admit in C10):** Device Reachability *Subscriptions* would reduce polling; mark as gap. eSIM remote management: not required for this story.

### Domain APIs (credible shapes, fictional vendors)

| System | Example operations (simulated) |
| --- | --- |
| Inventory | `listDevices`, `getDevice` |
| Twin | `getTwin`, `reported.firmwareVersion` |
| Firmware | `getPackage` (8.4) |
| Campaign | `createCampaign`, `startWave`, `getCampaignStats` |
| Telemetry | `latestCheckIn` (enterprise last-seen, contrasted with network reachability) |

### Manufacturing vs IoT vs logistics vs utilities

Same engine. Sales profile remaps industry label and numbers (500k auto vs 20k plant tools vs 80k meters). **One live seed** (e.g. 100k plant/IoT devices) is enough. Do not build four OTA engines.

---

## 20. Manufacturing recommendation

**Keep Acme QoD as the only manufacturing live hero.** It is the strongest ACT/closed-loop story in the demo.

Do **not** make every plant story “latency bad → QoD.”

| Scenario | Live vs Explorer | Why |
| --- | --- | --- |
| Critical inspection camera | **LIVE KEEP** | Unique ACT + verify |
| Device OTA / shift-based fleet | **LIVE** as Acme Device Fleet app | Different story (volume), not a QoD clone |
| Predictive maintenance coordination | Explorer | Reachability-only; weaker uniqueness |
| AGV fleet | Explorer only | QoD clone |
| Remote diagnostics | Explorer | Overlaps OTA/reachability |
| Machine/asset reachability | Fold into OTA segmentation | Don’t split |
| Factory edge placement | Explorer | Experimental; Acme already considers edge NOT_REQUIRED |
| Quality inspection (other) | Don’t add | Duplicate |
| Safety camera assurance | Explorer only | QoD clone |

---

## 21. DPV 2.3 purpose migration

**Model:**

```yaml
purpose:
  vocabulary: DPV
  version: "2.3"
  id: dpv:FraudPreventionAndDetection   # validated
  iri: https://w3id.org/dpv#FraudPreventionAndDetection
  label: Fraud Prevention and Detection
  context: Scenario-specific sentence. Not a new DPV term.
```

Keep AX `purposeId` as an internal key during Cadence 7; map to DPV. Do not use invented DPV-looking IDs.

| Current AX purpose | Closest DPV 2.3 | In TMF931 enum? | Notes |
| --- | --- | --- | --- |
| `payment_fraud_assist` | `dpv:FraudPreventionAndDetection` | Yes | Primary for Rocket Bank trust |
| `identity_continuity_assist` | `dpv:IdentityVerification` | Yes | Recovery; not Fraud if the processing is continuity not fraud scoring |
| NV verify number | `dpv:IdentityAuthentication` | Yes | Best fit for silent auth |
| `kyc_attribute_match` | `dpv:IdentityVerification` | Yes | No dedicated KYC purpose; context explains match-vs-auth |
| `pharmacy_age_eligibility` / `age_assertion` | `dpv:AgeVerification` | Yes | Exact |
| `inspection_video_assurance` | `dpv:ServiceOptimisation` | Yes | Experience/SLO restoration. Alternative `dpv:IncreaseServiceRobustness`. **No** plant-video DPV term — do not invent |
| `baggage_connection_assurance` | `dpv:RequestedServiceProvision` | Yes | Weak fit. After High Flight evolution use `dpv:ServiceOptimisation` or `dpv:FulfilmentOfContractualObligation` (Reso 753) — **NEEDS_REVIEW** which is less forced |
| `presence_assurance` | `dpv:ServiceProvision` | Yes | Broad; many Explorer cases. Report: no “geofence/presence” DPV purpose |
| `experience_assurance` | `dpv:ServiceOptimisation` | Yes | Telehealth/venue/broadcast Explorer |
| OTA / device management | `dpv:ImproveExistingProductsAndServices` | Yes | Firmware as improving the product. Alt: `dpv:RepairImpairments` if the campaign is a fix. Prefer Improve* for planned 8.4 rollout |
| `dpv:ServiceMonitoring` | — | **No** (2.3 only) | Attractive for observe-loops; **do not use** if we want TMF931-direct purpose on the API product grant. Prefer `ServiceOptimisation` / `IncreaseServiceRobustness` |

**Intent ≠ Purpose examples**

- Intent `verify_mobile_number` / Purpose `IdentityAuthentication`.  
- Intent `rollout_firmware_safely` / Purpose `ImproveExistingProductsAndServices`.  
- Intent `maintain_inspection_experience` / Purpose `ServiceOptimisation`.

If no clean DPV concept exists, keep `context` and a broader parent (`ServiceProvision`) rather than minting IDs. Baggage/ramp is the awkward case — report it rather than forcing `DeliveryOfGoods` (that is parcel delivery to a data subject, wrong).

---

## 22. TMF931 alignment

TMF931 = Open Gateway **onboarding and ordering**, Channel Partner ↔ Operator. Aggregator ≅ ChannelPartner; developer/ASP ≅ ApplicationOwner.

### Field classification

| Field | Classification | Notes |
| --- | --- | --- |
| Application Owner / Enterprise | **TMF931 DIRECT** | `applicationOwner` |
| Application | **TMF931 DIRECT** | `application` |
| API Product / catalog family | **TMF931 DIRECT** | `apiProduct` |
| Subscription / order | **TMF931 DIRECT** | `apiProductOrder` |
| Scope | **TMF931 DIRECT** | CAMARA scopes on grant |
| Purpose (DPV) | **TMF931 DIRECT** | `ApiGrantInformation.purpose` |
| Legal basis | **TMF931 DIRECT** | `legalBasis` |
| Terms / agreement | **TMF931 DIRECT** | agreement refs on product/order |
| Grant type / security profile | **TMF931 DIRECT** | `grantType`, digital identity |
| Region / geography on product | **TMF931-INSPIRED** | Product/order geography exists in TMF patterns; confirm per field in C7 |
| Operator / provider | **TMF931-INSPIRED** | Operate API is CP↔operator; serving network at runtime is discovery |
| Entitlement (app may use X) | **TMF931-INSPIRED / NETAWARE** | PermissionSet / product status; NetAware may be stricter |
| Agent | **AX-SPECIFIC** | Not a TMF931 resource. Do not force it. |
| Intent | **AX-SPECIFIC** | Not TMF921 either, in this prototype |
| Autonomy | **AX-SPECIFIC** | |
| Capability discovery pipeline | **AX-SPECIFIC** built on TMF931 + runtime | |
| Telco Finder / API Finder | **NETAWARE-SPECIFIC** | |
| Evidence / replan / verify | **AX-SPECIFIC** | |
| Access type | **RUNTIME-DISCOVERED** | From app/SDK context |
| Entitlement server availability | **RUNTIME-DISCOVERED** (demo: configured operator profile) | |
| Home/serving network | **RUNTIME-DISCOVERED** | Telco Finder |
| NV1 vs NV2 selection | **AX-SPECIFIC** on top of runtime + operator profile | |
| Sales scenario profile | **AX-SPECIFIC** | Presentation/config overlay |
| DPA as enterprise YAML | **NETAWARE-SPECIFIC** wrapping TMF931 agreement | |

**Onboarding vs order vs enterprise vs AX vs runtime**

| Comes from | Examples |
| --- | --- |
| ONBOARDING | ApplicationOwner, Application, security profile, DPV purpose declared |
| API ORDER / SUBSCRIPTION | Which API products, scopes, agreements, commercial status |
| ENTERPRISE CONFIGURATION | Policy extras, autonomy, agent, domain API stubs, SLO |
| AX-SPECIFIC | Intent, discovery ranking, evidence store, sales profile |
| RUNTIME DISCOVERY | Access type, operator, ECS, route, evidence TTL, QoS breach |

---

## 23. Configured vs runtime knowledge

| Knows before the Intent | Discovers / evaluates at runtime |
| --- | --- |
| Enterprise, Application, Agent | Subject instance (this device, this bag, this MSISDN) |
| Allowed Intents | Access type |
| DPV Purpose (default) | Home/serving network (Telco Finder) |
| Subscriptions, entitlements | Operator NV1/NV2/ECS *status* (demo: seeded per scenario; still presented as discovery) |
| Policy, consent rules, DPA | Consent *availability* if we later model it dynamically (today configured) |
| Preferred routes | Actual route chosen |
| Catalog pin | Which operations the serving network advertises (API Finder) |
| Autonomy envelope | Whether this *action* is inside the envelope |
| Sales profile labels | Outcome, evidence, replan |

The tiny request remains sacred. Access type belongs in **runtime context** (from the application/SDK), not in onboarding.

---

## 24. Domain / API research

Fictional brands only. Shapes should look like real systems.

### Airlines / airports (High Flight evolved)

| Layer | Credible APIs / systems |
| --- | --- |
| Domain | BRS scan session; IATA RP 1745-style bag messages (BSM/BPM as named stubs); DCS bag-flight; AODB / flight status |
| Enterprise | Ground handling device registry; shift assignment |
| Network | Reachability, Roaming, Connectivity Insights; QoD only if limiting |

### Manufacturing (Acme inspection)

| Layer | APIs |
| --- | --- |
| Domain | MES work-order / line state; QMS inspection job |
| Enterprise | Camera / VMS control |
| Network | Connectivity Insights, Application Profiles, QoD, Edge (consider/not required) |

### Device management / OTA

| Layer | APIs |
| --- | --- |
| Domain | LwM2M-like firmware object; campaign manager; inventory; twin |
| Network | Reachability, Roaming, optional Connectivity |

### Logistics (Explorer / profile remap)

Shipment/TMS, driver handheld registry, delivery events + Reachability/Roaming. Do not live-build if OTA exists.

### Retail (Explorer)

POS/payments + same identity APIs as banking; POS age-gate + Age Verification.

### Financial (Rocket Bank)

Payments, fraud decisioning, IAM/recovery, core banking + Number Verification / SIM Swap / Device Swap / Roaming.

**Every recommended live scenario: enterprise APIs already exist; Network APIs complement; AX decides.**

---

## 25. Catalog gaps

**Do not expand `AX_ACTIVE_CATALOG` for the recommended live set.**

| Capability | CAMARA / spec | Maturity | Business justification | Admit? |
| --- | --- | --- | --- | --- |
| Access type | Connected Network Type (pinned, not active) | Incubating/experimental in pin | App/SDK already knows Wi-Fi vs cellular | **No** — runtime context. Admitting it is “looks complete.” |
| NV2 ECS | Not a CAMARA API | Operator TS.43 | Operator-readiness | **No** — operator profile |
| Reachability subscriptions | Device Reachability Status Subscriptions | In pin, not active | OTA observe without poll | **Gap, not C10.** Revisit C11+ if polling looks fake |
| eSIM / FOTA | eSimRemoteManagement experimental | Experimental | Real OEM story | **No** — enterprise OTA API is the actor |
| IoT SIM fraud | IoTSIMFraudPrevention | Experimental | Different buyer | **No** |
| Capabilities & restrictions | experimental pack | Experimental | Meta-discovery | **No** for now; operator profile is enough |
| OTP SMS | OTPValidation | In pin | Fallback | **No** — contradicts NV product |

If C10 OTA observation feels dishonest as N sequential retrieves, prefer **simulated batch retrieve** in the seed (one plan step, many logical devices) rather than admitting subscriptions under pressure.

---

## 26. KEEP / IMPROVE / DEMOTE / REMOVE table

| Component | Action | Notes |
| --- | --- | --- |
| Rocket Bank trust | **KEEP** | Best unique-network opener |
| Rocket Bank recovery | **KEEP** (secondary) | Evidence reuse; not a hero card |
| CityCare | **KEEP** | Governance; don’t clone as retail live |
| Acme inspection | **KEEP** | Closed-loop ACT |
| High Flight baggage-connection | **DEMOTE TO EXPLORER** (after C11 replacement) | Until then: **DEMOTE FROM OPENER** |
| High Flight ramp-scanner | **IMPROVE** (new live in C11) | Same brand |
| Explorer product graph | **KEEP** | Advanced/leverage; not the sales plot |
| Evidence reuse | **KEEP** | |
| API Catalog 13 families | **KEEP** | Strength |
| Agent ≠ Application | **KEEP** | |
| Policy as runtime | **KEEP** | Split subscription vs entitlement (**IMPROVE**) |
| Autonomy levels | **KEEP** | |
| Provider routes | **KEEP** | |
| Live Flow | **KEEP** | Secondary to Discovery in Advanced |
| Decision Trace | **IMPROVE** | Feed Discovery pipeline |
| API Trace | **KEEP** | Advanced default |
| Cadence 6.1 value strip | **KEEP** | Basic Overview |
| Home DX→AX | **KEEP** | |
| NV labels on verify/share | **REMOVE** (relabel) | C7 model / C9 UI |
| High Flight as default opener | **REMOVE** | C8 |
| Basic vs Advanced | **ADD** | C8 |
| Capability Discovery view | **ADD** | C8 |
| `verify_mobile_number` | **ADD** | C9 |
| Acme Device Fleet OTA | **ADD** | C10 |
| Sales YAML profiles | **ADD** | C11 |
| Checkout / AGV / turnaround live | **EXPLORER ONLY** | |
| Generic chatbot / LLM planner | **REMOVE** from roadmap in this horizon | Would make AX look like generic AI |
| Admin UI for profiles | **NOT INCLUDED** | |
| Catalog portal vibe | **DEMOTE** | Explorer only after a live run |

---

## 27. Proposed Cadence 7+

Product behavior stays frozen until Cadence 7 is **explicitly approved**.

### Cadence 7 — Research / model alignment

**Objective.** Lock DPV, TMF931 mapping, NV path architecture, discovery stages, High Flight decision, OTA shape, and sales-profile schema in config/docs — **no major UI and no new live runs**.

**Why this cadence exists.** Cadence 0’s NV2 `NEEDS_REVIEW` is still open. Implementing visualization or NV live on the wrong axis would encode a lie.

**Sales value.** None visible yet; prevents a wrong operator story.

**Product value.** Shared language for C8–C11. Split subscription vs entitlement in the *model* (even if runtime still mirrors today’s evaluations).

**NetAware assets leveraged.** Catalog, onboarding entities, Telco Finder/API Finder concepts, operator profiles.

**New AX concepts.** NV path (not operation alias); discovery stage list; `SalesScenarioProfile` schema (unused); DPV purpose records.

**Research required.** Done in this document; C7 encodes it. Remaining: TMF931 region field exactness; High Flight Intent ID; OTA campaign API shape freeze.

**Data/model changes.** `purposes.yaml` DPV fields; operator `entitlementServer` placeholders; discovery reason code enum; comments/relabel in catalog (NV productLabels). **No active catalog expansion.**

**Backend/runtime.** Minimal: load new purpose fields; do not change outcomes of the four heroes. Validators for DPV IDs ∈ known list.

**Frontend.** None required. Optional footer still says freeze until C8.

**Explorer.** Purpose labels may show DPV id (low risk). Prefer wait for C8 Advanced.

**Scenario changes.** None to seeds/outcomes.

**Acceptance criteria.**

- Documented NV1/NV2 ≠ verify/share; catalog labels corrected in YAML comments/productLabel.  
- Every purpose has a real DPV id or an explicit “no clean concept” note.  
- TMF931 classification table implemented as machine-readable config or docs table in-repo.  
- Discovery reason codes enumerated.  
- Four hero outcomes **unchanged**.  
- Cadence 0–6.1 validators still pass.

**Tests.** Schema/validator: DPV ids; no new executable intents; catalog family count 13; NV operations not labelled NV1/NV2.

**Risks.** Scope creep into C8 UI. Relabeling catalog without UI may confuse presenters — add FAQ one-liner.

**NEEDS_REVIEW.** High Flight Intent ID; whether recovery purpose is IdentityVerification vs FraudPreventionAndDetection.

**Not included.** Discovery UI, NV live, OTA, High Flight rewrite, Basic/Advanced, hosting freeze.

**STOP.** No Cadence 8 until C7 accepted.

---

### Cadence 8 — Capability Discovery UX + Basic/Advanced

**Objective.** Make discovery a first-class product surface on **existing** live scenarios. Add Basic/Advanced lens. Change default demo order to Rocket Bank first.

**Why.** Highest visible product leap; NV and OTA will *use* this surface. Doing NV first would hide selection in the old Decision tab.

**Sales value.** Executives get 90-second Basic. Operators see *how NetAware figures out what it can do*. Sales can switch lens in-meeting.

**Product value.** Trace gains `discovery[]`. Subscription ≠ entitlement in evaluations. High Flight no longer default opener.

**Assets leveraged.** Policy, subscription, agreement, Telco Finder, API Finder, routes, existing decisions.

**New AX concepts.** Discovery pipeline visualization; presentation lens.

**Research.** Visualization collapse of stages for Basic (lock 5 layers).

**Data/model.** Emit structured discovery events from current policy evaluations (even if some stages are N/A).

**Backend.** Shared discovery emitter used by all four (five) executors. Split entitlement from subscription in trace. **Do not change business outcomes.**

**Frontend.** Lens toggle; Discovery tab (Advanced default on); Basic hides operationIds; picker order Rocket Bank first.

**Explorer.** Unchanged except purpose DPV if not done in C7 UI.

**Scenarios.** No new seeds. High Flight remains executable but not opener.

**Acceptance.**

- Same STEP_UP / AT_RISK / ASSURED / ELIGIBLE / CONTINUITY_ALIGNED.  
- Basic answers the six business questions without CAMARA literacy.  
- Advanced shows considered / filtered / why / remaining / selected / route.  
- CityCare shows KYC `PURPOSE`/`POLICY` filtered, Age `SELECTED`.  
- Rocket Bank shows recycling `NOT_REQUIRED`, location `CONSENT_MISSING`.

**Tests.** Trace schema; lens does not fork engines; snapshot discovery codes for each hero; Cadence 6.1 validators still pass.

**Risks.** Over-animating 20 stages. Mitigate: Basic 5 layers; Advanced matrix.

**NEEDS_REVIEW.** Exact Basic layer titles.

**Not included.** NV paths, OTA, High Flight rewrite, sales profiles runtime, catalog adds.

**STOP.** No C9 until discovery is presentable on current heroes.

---

### Cadence 9 — NV1/NV2 live experience

**Objective.** Same Intent `verify_mobile_number`; cellular NV1; Wi-Fi NV2; Wi-Fi + ECS unavailable.

**Why.** Operator-meeting weapon; entitlement-server commercial story; closes the Cadence 0 review with *behavior*, not comments.

**Sales value.** “This is why operator ECS readiness matters.” Configurable access-type seed.

**Product value.** Path selection on top of discovery; Number Verification family used correctly.

**Assets leveraged.** Number Verification, Telco Finder, API Finder, operator profile, Identity purpose, 3-legged token *described* not implemented as real OIDC.

**New concepts.** NV path, ECS availability filter, access type.

**Research.** Token flow shown at honesty level (simulated). No real TS.43.

**Data.** Three seeds; operator A ECS up; operator variant ECS down. Rocket Bank application + agent allowedIntents updated.

**Backend.** New executable intent; prefer extending interpreter over a fifth 400-line function. Still deterministic YAML.

**Frontend.** Access-type visible in Basic (“On Wi-Fi”); Advanced shows NV1 filtered / NV2 selected / ECS reason. Discovery pipeline must show the path.

**Explorer.** Intent appears; not a new catalog family.

**Scenarios.** Do not replace `assess_network_trust`. NV is adjacent (IAM), trust remains fraud-assist.

**Acceptance.**

- Cellular seed selects NV1; invokes `phoneNumberVerify` (claimed number). `phoneNumberShare` NOT_REQUIRED.  
- Wi-Fi + ECS up selects NV2; same operation if claimed number exists.  
- Wi-Fi + ECS down: `ENTITLEMENT_SERVER_UNAVAILABLE`; no silent NV1; enterprise-owned alternate, not SMS OTP from AX.  
- Catalog still 13 families.

**Tests.** Path table; operation ≠ path; discovery reasons; trust scenario regression.

**Risks.** Presenters still say “NV2 is share.” FAQ + UI copy must hammer path vs operation.

**NEEDS_REVIEW.** CIBA vs JWT-bearer presentation depth.

**Not included.** OTA, High Flight rewrite, sales profile loader, real tokens.

**STOP.** No C10 until the three NV seeds are demo-safe.

---

### Cadence 10 — Device Fleet OTA (commercial expansion)

**Objective.** One new live application: Acme Device Fleet `rollout_firmware_safely`. DISCOVER–SEGMENT–PLAN–ACT–OBSERVE–REPLAN–VERIFY. QoD not default.

**Why.** Volume story operators ask for; different agentic shape than identity and QoD.

**Sales value.** “100k devices, Network APIs gate the campaign.” Profile later remaps to automotive 500k.

**Product value.** Domain OTA API as the ACT; Network APIs as OBSERVE. Proves AX is not a generic orchestrator: the unique input is operator reachability/roaming.

**Assets leveraged.** Reachability, Roaming, Telco Finder (per device or simulated batch), subscriptions, autonomy ACT_WITH_APPROVAL on campaign start.

**New concepts.** Cohort segmentation; enterprise ACT; batch/volume presentation (do not animate 100k Live Flow hops).

**Research.** Campaign API shape freeze from this plan.

**Data.** New application, agent, policy, subscriptions (connectivity/mobility), seed with cohort counts (not 100k individual invocations in the trace).

**Backend.** Interpreter support for segment summary + one enterprise campaign invocation + replan wave. Resist 100k HTTP rows.

**Frontend.** Basic: pie/counts of reachable vs deferred. Advanced: sample device rows + discovery on one roaming device.

**Explorer.** New use case + intent; reverse from `getReachabilityStatus`.

**Scenarios.** Acme QoD **unchanged**.

**Acceptance.**

- Network contribution test pass in briefing (6.1 structure).  
- QoD NOT_REQUIRED / not in plan.  
- Volume visible as counts; operator monetization line in close/briefing.  
- Catalog still 13.  
- Agentic properties listed in trace (`SEGMENT`, `REPLAN`).

**Tests.** No QoD invocation; cohort math; enterprise OTA API kind labelled ENTERPRISE; Cadence 9 regression.

**Risks.** Looks like a generic workflow tool if network uniqueness is weak in Basic copy. Mitigate with contribution strip.

**NEEDS_REVIEW.** Batch vs subscriptions; plant vs automotive default label.

**Not included.** High Flight rewrite, sales profile loader, second manufacturing live, catalog subscriptions API.

**STOP.** No C11 until OTA is a clean 90-second Basic story.

---

### Cadence 11 — High Flight evolution + sales profiles

**Objective.** Replace High Flight hero with ramp-scanner assurance. Load YAML `SalesScenarioProfile` to select enterprise/intent/lens/topology/copy without a new engine.

**Why.** Cross-domain story that **passes** the contribution test; Sales can configure a meeting.

**Sales value.** Industry/audience/region/problem/topology in a file. High Flight finally usable in airline meetings.

**Product value.** Proves scenarios are instances. Profile cannot invent operations.

**Assets leveraged.** Reachability, roaming, connectivity; BRS/DCS domain stubs; discovery UX; Basic/Advanced.

**New concepts.** Sales profile; High Flight Application = Ground Handling.

**Data.** New High Flight seed; old baggage-connection `explorerOnly: true`. Profile examples: operator-CTO-DE-OTA, bank-exec-CA-NV, airline-ops-HF-ramp.

**Backend.** Profile loader; fail if intent not executable.

**Frontend.** Optional `?profile=` or picker “Load meeting profile”; still no admin UI.

**Explorer.** Baggage-connection stays as graph node.

**Acceptance.**

- Ramp-scanner: unreachable device → business action changes.  
- No implication that reachability is bag location.  
- Profile switches lens and scenario without code change.  
- Current Acme/Rocket/CityCare/OTA/NV still pass.

**Tests.** Profile schema; unknown intent 4xx; High Flight briefing contribution test strings; baggage not in featured opener.

**Risks.** Two High Flight stories confuse presenters. Runbook: one live, one Explorer.

**NEEDS_REVIEW.** Intent ID; whether QoD appears if connectivity is the limiter (allowed, not required).

**Not included.** Admin UI, new catalog APIs, LLM mapping of natural language to Intent.

**STOP.** No C12 until profiles work on the live set.

---

### Cadence 12 — Presentation freeze + hosted sales baseline

**Objective.** Freeze product behavior for Sales hosting. Presenter-safe Render: secrets, version, health, reset, stable seed, auto-deploy.

**Why.** A sales weapon that cannot be hosted is a laptop demo.

**Sales value.** Share a URL before the meeting; Basic Auth; known version.

**Product value.** None functional; operational trust.

**Assets.** Existing `/health`, Basic Auth middleware, `render.yaml` `DEMO_USERNAME`/`DEMO_PASSWORD` (`sync: false` already).

**Hardening plan (not a product feature):**

- Require Basic Auth in `ENVIRONMENT=hosted` (fail closed if secrets missing).  
- Secrets only in Render env; never source.  
- `BUILD_ID` / `APP_VERSION` = freeze tag (e.g. `0.7.0-ax12` or whatever C7–11 produce — **not** today’s `ax6`).  
- Health returns version, cadence, `basicAuthConfigured`, seed generation.  
- `POST /executions/reset` remains the Reset path; document “reset before every meeting.”  
- Stable seed: no clock-dependent outcomes (already mostly true).  
- Auto-deploy: keep Render Docker; pin release branch; smoke script (`smoke_hosted.py`) in runbook.  
- Presenter-safe: no debug stack traces; fictional data only.

**Frontend.** Footer freeze line; version visible. No scenario work.

**Acceptance.** Hosted smoke with auth; unauthenticated `/health` ok; other routes 401; reset restores NV/OTA/High Flight seeds; no credentials in git.

**Tests.** smoke_hosted; secret scanner on repo; version endpoint.

**Risks.** Forcing auth locally if env leaks — document local vs hosted.

**Not included.** New scenarios, catalog, LLM, multi-tenant real IdP.

**STOP.** Cadence 13 not planned here.

---

## 28. Acceptance criteria (horizon)

The post-C12 sales baseline is accepted when:

1. Sales can pick a YAML profile for industry/audience/region/problem without a new engine.  
2. Every hero has a named buyer and a Network API contribution that **changes an action**.  
3. NV1/NV2 is path-based; ECS failure is visible.  
4. OTA shows fleet-scale consumption without QoD theatre.  
5. Discovery is a product surface (Basic pipeline, Advanced matrix).  
6. Executives can do 90 seconds in Basic; architects can drill `operationId` + filter codes.  
7. AX is explained as evolution of onboarding, catalog, subscription, Telco Finder, invocation — not a replacement.  
8. `AX_ACTIVE_CATALOG` still 13 families unless a later cadence explicitly admits a documented gap.  
9. Hosted demo is auth-gated, versioned, resettable.  
10. Nothing was added solely because it looked impressive (Connected Network Type, SMS OTP, AGV, chatbot).

---

## 29. Risks / assumptions

| Risk | Mitigation |
| --- | --- |
| Presenters keep saying NV2 = `phoneNumberShare` | C7 relabel + C9 UI + FAQ |
| Capability discovery looks like a generic AI planner | Only Network+NetAware assets as filters; no LLM |
| OTA looks like a workflow product | Contribution test in briefing; enterprise OTA owns flashing |
| High Flight rewrite late (C11) | C8 already removes it as opener |
| Too many live runs for a 10-minute slot | Profiles pick 2–3; full set is the library |
| DPV 2.3 vs TMF931 2.0 enum | Prefer overlapping IDs |
| Subscriptions API temptation | Batch in seed, don’t expand catalog |
| Per-intent Python continues to grow | C9/C10 should share interpreter; **NEEDS_REVIEW** refactor vs time |
| Hosted credentials unused | C12 fail-closed |
| Meta_Demo nostalgia (273 capabilities) | Keep Explorer Advanced; never home hero |
| Legal over-claim on consent/DPA | Keep “configured demo policy” honesty |

**Assumptions:** Deterministic simulation remains; no live operators; no LLM; fictional enterprises; Jigyasa unused; Meta_Demo not imported.

---

## 30. Recommendation for first next implementation cadence

**Do not start Cadence 7 until this plan is explicitly approved.**

When approved, implement **Cadence 7 only** (model alignment). Do not combine C7+C8. Do not change the deployed `0.6.1-ax6.1` demo until C7 lands and C8 is separately approved.

Cadence 7 is the correct first step because the current NV1/NV2 catalogue labelling is the wrong axis, High Flight’s hero status is a commercial liability if we keep building on it, and Discovery UX built on implicit per-scenario logic would freeze the wrong model.

---

## Appendix A — Final sales test

| Question | Answer in this plan |
| --- | --- |
| Would Sales want this before a major meeting? | Yes after C8–10; C6.1 is a product demo, not yet a weapon |
| Customizable without a new product? | Yes — YAML profile (C11) over one engine |
| Every hero a clear buyer? | Bank, plant quality, OEM/fleet, pharmacy, airline/ground handler, operator (NV/ECS) |
| Credible Network API volume? | NV/login + OTA fleet yes; QoD/age lower and kept for story diversity not volume |
| Unique Network API value? | Failures (current High Flight) demoted; replacements must pass §15 test |
| Feels agentic? | Path selection, discovery filters, evidence reuse, closed-loop, cohort replan |
| Executive in 90s? | Basic lens |
| Operator architect drill-down? | Advanced discovery matrix |
| Leverages today’s NetAware assets? | Onboarding, catalog, subscription, entitlement, Telco/API Finder, routes, invocation, OAM |
| Discovery looks like a product capability? | C8 hero surface |
| NV1/NV2 shows operator readiness? | C9 ECS unavailable beat |
| OTA high-volume believable? | Counts, not 100k animations |
| Small catalog still credible? | 13 families sufficient |
| Anything added to look impressive? | Explicitly rejected: Connected Network Type, SMS OTP, AGV live, chatbot, admin UI |

If High Flight were kept as-is as a hero, **unique value** and **90-second executive** answers would be weak. That is why it is demoted/evolved rather than copy-patched again.

---

## Appendix B — Network contribution tests (heroes)

### Rocket Bank trust — PASS

Bank knows transaction + app auth. Network adds SIM/device/number facts. AX selects a subset. Bank steps up.

### NV1/NV2 — PASS

App knows claimed number and access type. Network adds silent possession via the *available* path. ECS down **changes** the outcome (cannot verify on Wi-Fi).

### CityCare — PASS

Pharmacy knows SKU and threshold. Network adds age assertion. Broader KYC not used. Pharmacist dispenses.

### Acme QoD — PASS

MES/QMS know the job and SLO. Network observes limiter and applies QoD. Inspection continues.

### OTA — PASS

Campaign manager knows who should get 8.4. Network says who is reachable/not roaming. Cohort membership changes who gets flashed now.

### High Flight current — FAIL as hero

Expedite is already implied by domain ETA. Network does not change the action.

### High Flight ramp-scanner — PASS (proposed)

BRS knows the turn is tight. Network says the scanner cannot record custody. Action becomes swap device / hold close — **not** “the bag is in T-B-SORT-12.”

---

## Appendix C — Agentic properties (advanced live)

| Scenario | Beyond A then B |
| --- | --- |
| Rocket Bank trust | Policy/consent filtering; recycling NOT_REQUIRED; location replan |
| Recovery | Evidence reuse |
| NV1/NV2 | Access- and ECS-driven path selection; explicit unavailability |
| CityCare | Minimum-capability selection |
| Acme QoD | Observe, conditional ACT, verify, replan on breach |
| OTA | Segment, cohort plan, enterprise ACT, replan waves |
| High Flight evolved | Device-state conditional ops action; QoD only if limiting |

---

**STOP.**  

Do not implement.  
Do not change the deployed demo.  
Do not start Cadence 7 without explicit approval.
