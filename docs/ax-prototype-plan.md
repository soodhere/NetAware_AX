# NetAware AX Prototype Plan

**Status:** Planning only. No application code until Cadence 0 is explicitly approved.  
**Write target:** NetAware AX  
**Read-only reference:** Meta_Demo (frozen Cadence 5.5 / deploy 6 Network Intent prototype)  
**Do not touch:** Jigyasa  

**Product shift:** Developer Experience (DX) → Agentic Experience (AX)  
**Mechanism:** Network Intent  
**Principle:** Simple outside. Sophisticated and fully traceable inside.

---

## How this plan was grounded

Meta_Demo was inspected read-only. Evidence used:

| Source | What it provided |
|--------|------------------|
| `openapi/manifest.yaml` | Pinned CAMARA / experimental catalogue (~93 repos surveyed; local YAML copies; acquisition 2026-08-15) |
| `backend/app/registry.py` | Real `operationId`s + TOOL_META. Operations are never invented. |
| `backend/app/product.py` | DX→AX thesis, loop, governed intents, economy (273 / 9 / 2 / 262), governance cards, example/future intents |
| `backend/app/discovery.py` | Simulated Telco Finder / API Finder; Operator A / Aggregator B / Provider C |
| `backend/app/agent.py` + `expand.py` + `experience.py` | Deterministic TRUST / EXPAND / ASSURE / AGE runtimes |
| `data/seed.json`, `graph.json`, `experience.json` | Simulated world, correlation graph, SLO session |
| Frontend traces | Live sequence, Decision Trace, Tool Activity, Outcome, Governance, Playground, Explore |

Honesty rule for this plan:

- **SOURCE-BACKED** — API name / `operationId` / behaviour exists in Meta_Demo’s pinned catalogue or executed scenarios.
- **INFERRED** — Domain mapping of a real capability to a fictional enterprise; not executed in Meta_Demo.
- **NEEDS REVIEW** — Plausible but not locked; no invented `operationId`.

---

# 1. Reference project audit

## 1.1 What made Meta_Demo effective

Recreate / adapt these independently inside NetAware AX.

| Concept | Why it worked | AX adaptation |
|---------|---------------|---------------|
| Immediate business story | Audience sees a high-value action before telecom jargon | Start in **their domain** (bank, airline, factory). Meta/Instagram storytelling **does not** carry over. |
| Deterministic simulation | No LLM. Same run, same decisions. Demo-safe. | Keep. Intent ≠ prompt. Agentic ≠ LLM. |
| Tiny runtime request vs huge underneath | Application did not send the catalogue | Strengthen: onboarding/config is visible as “what NetAware already knows.” |
| Live who-called-whom | `LiveTrace` actors: Application → Intent → Telco Finder → API Finder → Policy → Execution → Network | Add Agent as a first-class actor. Show **route** (Direct / Aggregated / Hybrid / existing integration). |
| Actual `operationId`s | Click-through to CAMARA contract | Keep. API Catalog is the substrate, not a footnote. |
| Available vs invoked vs considered-not-invoked vs not required | 273 · 9 · 2 · 262 made selection visible | Keep economy strip; bind it to **this intent**, not a global slogan. |
| Decision trace (“why this / why not”) | WHY_SELECTED / WHY_NOT | Expand to SELECT / SKIP / BLOCK / REUSE / REPLAN with policy reasons. |
| Evidence + EVIDENCE_REUSED | EXPAND reused TRUST evidence | Keep as a first-class execution state. |
| Closed-loop verify | ASSURE: observe → skip QoD → later invoke → verify | Keep; make OBSERVE → REPLAN → VERIFY a visible agent loop, not a hidden step machine. |
| Bounded autonomy | RECOMMEND / INVESTIGATE / ACT + “not unconstrained” | Replace labels with **OBSERVE / RECOMMEND / ACT_WITH_APPROVAL / ACT**. Autonomy is Agent × Intent × Action. |
| Final business outcome | HOLD / STEP-UP; SATISFIED | Domain vocabulary: STEP_UP, AT_RISK, ASSURED — plus expandable JSON. |
| Optional technical drill-down | ToolDetail, OpenAPI fields | Keep behind APIs tab. Never dump it on the first screen. |
| Telco Finder / API Finder | First-class, simulated providers | Keep as product capabilities, not demo chrome. |
| Pinned OpenAPI registry | Grounded catalogue; superseded packs labeled | Independently copy/pin into NetAware AX. No import from Meta_Demo at runtime. |
| Honesty labels | Simulated context; no live operators; MCP FUTURE | Keep. Fictional enterprises only. |

## 1.2 What should NOT be carried over

| Do not copy | Why |
|-------------|-----|
| Meta / Instagram / WhatsApp / glasses as the story | Audience must start in *their* domain. Meta is a previous customer narrative. |
| TRUST / EXPAND / ASSURE as the **product navigation** | Those are three scenarios, not the AX product. Navigation becomes Demo + Explore. |
| INVESTIGATE as an autonomy level | User-specified levels: OBSERVE, RECOMMEND, ACT_WITH_APPROVAL, ACT. |
| Agent = another Application filling the same onboarding form | Enterprise → Application → Authorized Agent. |
| Policy as a static governance card | Policy must change runtime (BLOCKED_BY_POLICY → REPLAN). |
| “273 capabilities” as the home hero | Still true as catalogue depth; the home hero is **domain → intent → outcome**. |
| Access / self-service / sales-democratize thesis as a primary demo beat | Product-direction, not AX proof. Defer. |
| MCP as a shipped interface | FUTURE, not implemented. Northbound remains structured Intent API. |
| LLM planner / chatbot Playground | Constrained intent IDs only. Natural language mapping is optional later and must stay governed. |
| Real operator brands | Meta_Demo already forbids them. Keep Simulated Operator / Aggregator / Provider labels, or fictional names (Northline Mobile, Harbor Aggregate). |
| Hosting / commercial model lock | Direct vs aggregated vs hybrid vs existing integration are **execution routes**, not a product-hosting decision. |
| Copying Meta_Demo source, Docker, Render hostname, or in-memory agent API as-is | Independent recreation. New cadences (AX 0…n). |
| Cadence 1–6 numbering | Independent AX cadences. |
| Identity-graph as a CAMARA API | Meta_Demo honesty: CAMARA has no historical account↔SIM↔IMEI graph. Correlation remains NetAware-derived. |
| PredictiveConnectivityData as per-session oracle | Explicitly not that. |
| KYC Match / Fill-in as privacy-hostile demo spice | Catalogue-visible; not a hero unless an enterprise purpose + DPA + consent story is configured. |

## 1.3 Components to recreate vs redesign

| Meta_Demo component | Fate |
|---------------------|------|
| Home (DX→AX thesis) | Redesign: zero-context domain entry, not CAMARA-first. |
| TRUST / EXPAND / ASSURE canvases | Redesign as **deep scenario runtimes** (4–5), not product pillars. |
| LiveTrace | Recreate + add Agent, Purpose, Route. |
| DecisionTrace | Recreate; sync with five-tab deep view. |
| ToolActivity / ToolDetail | Recreate as APIs tab. |
| OutcomeTrace | Recreate as domain outcome card + JSON. |
| GovernanceCard | Split: configured policy (Explore) vs runtime Policy tab (Demo). |
| ResolutionStrip (Telco/API Finder) | Recreate; show route type. |
| Playground | Redesign as **run a configured intent**, not a chatbot. |
| Reveal / Explore | Redesign as graph Explorer (five connected graphs). |
| Expand graph (31→11→4) | Optional later Explorer / one inferred scenario. Not a hero until a fictional enterprise owns the digital graph. |
| Age intent | Candidate deep or Explorer-runnable; CityCare / Grand Stadium, not Meta. |

---

# 2. AX product model

## 2.1 The shift

```
DX  Developer discovers, selects, integrates, orchestrates Network APIs.
AX  Application or authorized agent expresses an outcome (Intent).
    NetAware understands context and rules, complements existing
    domain/enterprise APIs with Network APIs, and returns a business outcome.
```

Network APIs **complement** existing systems. They do not replace them.

```
EXISTING APPLICATION
EXISTING BUSINESS LOGIC
EXISTING DOMAIN APIs
EXISTING ENTERPRISE APIs
        +
NETWORK APIs  (CAMARA / Open Gateway via NetAware)
        =
RICHER OUTCOME, SAME APPLICATION
```

## 2.2 Intent (definition used in this prototype)

> **Intent** = the outcome an application or agent wants NetAware to achieve or assess **without specifying which Network APIs should be called**.

Runtime request is small. Configured knowledge is not re-sent.

```json
POST /intents
{
  "intent": "ensure_baggage_connection",
  "subject": { "bagId": "HF123456", "connectingFlight": "HF281" },
  "context": { "priority": "high" }
}
```

Not in the request (already known from onboarding/configuration):

- Enterprise, Application, Agent identity (from auth)
- Allowed intents, purposes, autonomy envelope
- Subscriptions, entitlements, DPA/agreement, residency
- Capability allowlists, preferred routes

## 2.3 Separation of concerns (must stay visible)

| Question | Concept |
|----------|---------|
| Who | Agent / Application actor |
| Wants what | Intent |
| On who / what | Subject + runtime context |
| What NetAware knows | Enterprise / Application / Agent onboarding + configured context |
| Why | Purpose |
| What is allowed | Policy / Consent / DPA / Sovereignty / Security / Subscription / Entitlement / Commercial |
| How far it may go | Autonomy |
| What is needed | Capabilities |
| What implements it | API Catalog |
| Who can provide it | Telco Finder / API Finder / Providers |
| How it is reached | Direct / Aggregated / Hybrid / Existing enterprise integration |
| What NetAware does | Plan → Select → Invoke / Skip / Block → Observe → Replan → Verify |
| What caller gets | Business / domain outcome |

## 2.4 Core mapping (configuration, not code per use case)

```
DOMAIN → USE CASE → INTENT → CAPABILITY → API CATALOG → PROVIDER / ROUTE
                                              ↓
                                    POLICY + AUTONOMY + PURPOSE
                                              ↓
                                    EXECUTION → OUTCOME
```

**API Catalog is critical.** Intent does not replace it. Intent makes the catalogue consumable from a business outcome.

## 2.5 Runtime loop (agentic, not static orchestration)

```
AGENT AUTHENTICATED
→ INTENT RECEIVED
→ CONTEXT RESOLVED          (onboarding + subject + runtime)
→ AGENT AUTHORIZATION       (may this agent send this intent?)
→ PURPOSE RESOLVED
→ POLICY EVALUATED          (may combine many configured layers)
→ USE CASE MAPPED
→ CAPABILITIES DETERMINED
→ API CATALOG RESOLVED
→ TELCO FINDER
→ API FINDER
→ PROVIDER / ROUTE RESOLVED
→ PLAN CREATED
→ EXECUTE
→ OBSERVE
→ REPLAN IF REQUIRED
→ AUTONOMY CHECK            (per action)
→ VERIFY
→ BUSINESS OUTCOME
```

This must look like an agent operating inside an envelope — not a hardcoded API sequence with nicer labels.

## 2.6 Three consumption models (honesty, from Meta_Demo — keep)

| Model | Ask | When |
|-------|-----|------|
| Direct Network API | “Has this SIM changed?” | Caller knows the capability |
| Authored / composed API | “For this use case run A+B+C” | Design-time composition |
| Network Intent | “Assess network trust for this transaction” | Outcome + policy; dynamic execution |

AX demo proves the **third**. The first two remain valid and visible in Explorer.

---

# 3. Data model

Configuration-driven. Deep scenarios are **instances**, not unique engines.

## 3.1 Entities

### Business graph

| Entity | Meaning |
|--------|---------|
| **Domain** | Industry slice (Financial, Airlines, Manufacturing, …) |
| **UseCase** | Named job-to-be-done in that domain |
| **Intent** | Outcome identifier (`ensure_baggage_connection`) + description + default purpose |

### Governance graph

| Entity | Meaning |
|--------|---------|
| **Enterprise** | Fictional customer (High Flight Airlines) |
| **Application** | Existing system (Baggage Operations) |
| **Agent** | Authorized actor acting **on behalf of** an Application |
| **Purpose** | Why network evidence/action is requested (e.g. `baggage_connection_assurance`) |
| **Policy** | Named bundle attached to Enterprise / Application / Agent / Intent / API / Provider |
| **PolicyRule** | Atomic: permit / deny / constrain on a dimension |
| **ConsentRule** | Whether consent is required for a capability; runtime **ConsentState** is evidence |
| **Agreement** | DPA / contract configuration (permitted processing, regions, purposes) — **configured**, not universal law |
| **AutonomyRule** | Agent × Intent × Action → OBSERVE \| RECOMMEND \| ACT_WITH_APPROVAL \| ACT \| NOT_AUTHORIZED |
| **Subscription** | Commercial/product subscription to a capability family or API |
| **Entitlement** | What this tenant/app/agent may actually use (may be narrower than subscription) |

### Capability graph

| Entity | Meaning |
|--------|---------|
| **Capability** | Business-level network ability (Number possession verification, Location verification, QoD, …) |
| **API** | Catalogue entry: name, category, CAMARA version, maturity, spec path |
| **Operation** | Pinned `operationId` + method/path — never invented when spec exists |

### Ecosystem graph

| Entity | Meaning |
|--------|---------|
| **Provider** | Simulated operator, aggregator, or specialist (no real brands) |
| **Route** | How an operation is reached: `DIRECT` \| `AGGREGATED` \| `HYBRID` \| `EXISTING_ENTERPRISE_INTEGRATION` |
| **Subject** | Runtime target (MSISDN, bagId, deviceId, flightId, …) |
| **RuntimeContext** | Access type (Wi-Fi / 5G), region, priority, timestamps, correlation IDs |

### Execution graph

| Entity | Meaning |
|--------|---------|
| **Evidence** | Normalized fact + source operation + TTL + purpose + reuse eligibility |
| **Plan** | Ordered PlanSteps for this intent execution |
| **PlanStep** | Capability + candidate operations + expected state |
| **Decision** | Why SELECTED / SKIPPED / BLOCKED / REUSED / REPLANNED |
| **Invocation** | Technical call: provider, route, correlation, status, latency, (no secrets) |
| **Outcome** | Domain result the application understands + expandable JSON |

## 3.2 Relationships (minimum)

```
Enterprise 1—* Application 1—* Agent
Agent *—* Intent (allowed)
Intent *—1 Purpose (default) ; may override per request if permitted
Intent *—* Capability
Capability *—* Operation (API Catalog)
Operation *—* ProviderCapability
ProviderCapability *—* Route
Enterprise/Application/Agent/Intent/Operation/Provider → Policy (many)
Policy 1—* PolicyRule | ConsentRule | AutonomyRule
Agreement *—* Purpose, Region, Capability
Subscription / Entitlement bound to Enterprise or Application
Execution: IntentInstance → Plan → PlanStep → Decision → Invocation? → Evidence?
IntentInstance → Outcome
Evidence may be reused by a later IntentInstance of the same tenant (EVIDENCE_REUSED)
```

## 3.3 Execution states (canonical)

`REQUIRED` · `CONSIDERED` · `SELECTED` · `INVOKED` · `NOT_REQUIRED` · `BLOCKED_BY_POLICY` · `NOT_AVAILABLE` · `EVIDENCE_REUSED` · `FAILED` · `REPLANNED` · `VERIFIED`

## 3.4 API kinds (must be labeled in UI)

| Kind | Owner | Example |
|------|-------|---------|
| **DOMAIN API** | Industry / line-of-business | Baggage Journey, Flight Status |
| **ENTERPRISE API** | Internal ops | Ground Operations, Fraud Decisioning |
| **NETWORK API** | CAMARA / Open Gateway via NetAware | Device Location, Connectivity Insights, QoD |

Prototype **simulates** domain/enterprise APIs as configured stubs so complementarity is visible. It does not pretend NetAware owns them.

---

# 4. Mapping model (configuration-driven)

One mapping table (or YAML/JSON graph) drives Explorer **and** runtime.

```text
domains/{id}.yaml
use-cases/{id}.yaml          # domainId, title, existingApis[]
intents/{id}.yaml            # useCaseId, capabilities[], defaultPurpose, defaultAutonomy
capabilities/{id}.yaml       # operations[]  (real operationIds)
enterprises/{id}.yaml        # applications, agents, agreements, subscriptions
policies/{id}.yaml
routes/{provider}/{op}.yaml  # DIRECT | AGGREGATED | HYBRID | EXISTING_ENTERPRISE_INTEGRATION
scenarios/{id}.yaml          # deep demo: subject, seed world, expected decisions
```

Runtime algorithm (deterministic):

1. Resolve Agent from auth → Application → Enterprise.
2. Load Intent config; reject if not in Agent.allowedIntents.
3. Merge Policy stack (see §5). Evaluate Purpose.
4. Expand Intent → Capabilities (config).
5. Expand Capabilities → Operations (API Catalog). Filter superseded packs.
6. Telco Finder: subject → network context / home vs visited / serving operator (simulated).
7. API Finder: which providers advertise remaining operations.
8. Route resolution: pick DIRECT / AGGREGATED / HYBRID / EXISTING_ENTERPRISE_INTEGRATION per operation from config + region.
9. Plan: for each capability, mark REQUIRED / CONSIDERED; apply policy, consent, access-type fitness, evidence TTL.
10. Execute selected steps; observe; replan if BLOCKED / FAILED / NOT_AVAILABLE / objective unmet.
11. Autonomy check before any **action** that changes network or recommends enterprise action.
12. Verify against intent success criteria; emit Outcome.

**No new Python engine per use case.** Deep scenarios differ by seed world + expected decision script + config, sharing one interpreter.

Forward exploration: Domain → Use Case → Intent → Capability → API.  
Reverse: API → Capability → Intents → Use Cases → Domains.

---

# 5. Governance model

Policy is **operational**. It is not a slide.

## 5.1 Effective policy (prototype)

Combine, in order, all **configured** layers that apply:

```
Enterprise policy
+ Application policy
+ Agent authorization
+ Purpose
+ Subscription
+ Entitlement
+ API / provider policy
+ Consent requirement + ConsentState
+ Agreement / DPA configuration
+ Jurisdiction / region
+ Data sovereignty / residency
+ Security
+ Commercial constraints
+ Runtime constraints (budget, SLA, access type)
```

**NetAware enforces configured governance.** It does not encode universal legal conclusions (“GDPR always blocks X”). The demo shows: *this tenant configured these rules; this is what happened.*

## 5.2 Evaluation result per capability/operation

| Result | Meaning | Agent behaviour |
|--------|---------|-----------------|
| PERMITTED | May select if useful | Continue plan |
| BLOCKED_BY_POLICY | Relevant but not allowed | Visible **REPLAN** |
| NOT_SUBSCRIBED / NOT_ENTITLED | Commercial gate | Skip / replan if alternate exists |
| CONSENT_REQUIRED_UNAVAILABLE | ConsentRule.required && !ConsentState | BLOCKED_BY_POLICY → replan |
| AGREEMENT_GAP | Purpose or region not on DPA | BLOCKED_BY_POLICY |
| NOT_AUTHORIZED (autonomy) | Action outside envelope | Do not act; return recommendation or denial |

## 5.3 Worked example (must be a live demo beat)

**Location Verification**

| Check | Value |
|-------|-------|
| Purpose | permitted |
| Subscription | yes |
| Region | permitted |
| Agreement / DPA | permitted |
| Consent required | yes |
| Consent available | no |
| **Result** | `BLOCKED_BY_POLICY` |
| **Agent** | REPLAN (e.g. roaming / reachability / domain ops instead) |

## 5.4 Autonomy envelope

Levels (user-facing):

| Level | NetAware may |
|-------|----------------|
| **OBSERVE** | Read / assess / return evidence. No network treatment. No enterprise action. |
| **RECOMMEND** | Return a recommended enterprise action (STEP_UP, HOLD). Enterprise decides. |
| **ACT_WITH_APPROVAL** | Propose a network or ops action; wait for approval (demo can simulate approval). |
| **ACT** | Invoke permitted treatment (e.g. QoD) within policy. |
| **NOT_AUTHORIZED** | Explicitly out of envelope (e.g. decline a bank transaction). |

Granularity: **Agent × Intent × Action**.

Rocket Bank example (configured, not universal):

| Action | Autonomy |
|--------|----------|
| Gather permitted network evidence | ACT |
| Recommend STEP_UP | RECOMMEND |
| Decline / block the transaction | NOT AUTHORIZED |

> The agent is autonomous **within a defined envelope**, not autonomous over the enterprise.

## 5.5 What Meta_Demo governance becomes

Meta_Demo’s compact cards (allowed / not authorized / budget / privacy) remain useful as **summaries**. AX must also show the **evaluation that changed the plan**.

---

# 6. Agent model

```
Enterprise
  └── Application          (existing system; owns domain APIs)
        └── Authorized Agent
              acts on behalf of Application
              allowed Intents[]
              autonomy rules (intent/action specific)
```

Example:

| Layer | Value |
|-------|-------|
| Enterprise | High Flight Airlines |
| Application | Baggage Operations |
| Agent | Baggage Operations Agent |
| Allowed intents | `ensure_baggage_connection`, `locate_baggage` |

**Do not lock production identity** in this prototype. Treat as unresolved:

- OAuth delegation vs workload identity vs agent registration vs application credentials
- Human-in-the-loop vs service account
- Token exchange / DPoP / SPIFFE, etc.

Prototype auth: **simulated Agent credential** → resolves to Enterprise / Application / Agent record. UI copy: “Production identity and delegation: intentionally unresolved.”

Agent is **not** “another Application using the same onboarding form.” Onboarding configures the Application and the Agent **as related but distinct** principals.

---

# 7. UX / information architecture

Two surfaces. Never mix them into TRUST / EXPAND / ASSURE tabs.

## 7.1 DEMO navigation

```
Home
  → Choose a domain / enterprise
  → Scenario briefing (zero-context)
  → Run
  → Deep scenario workspace
  → Outcome
```

**Home (zero-context, ~10 seconds)**

- Headline: From DX to AX — tell the network the outcome; keep your application.
- Three doors: **See it in a bank** · **See it in an airline** · **See it in a factory** (plus Explore).
- One sentence: Network APIs complement the systems you already have.

**Scenario briefing (before Run)** — the 10 answers, all visible:

1. This is my domain  
2. These are my existing systems / APIs  
3. These Network capabilities complement them  
4. This is what NetAware already knows about me  
5. This is my Agent  
6. This is the Intent I send *(tiny JSON)*  
7. This is my configured Purpose + Policy  
8. This is the autonomy I granted  
9. *(After run)* This is what NetAware did under the hood  
10. This is the business outcome my application got back  

**Deep scenario workspace** — five synchronized tabs (§8):

`OVERVIEW` · `LIVE FLOW` · `DECISIONS` · `APIs` · `POLICY`

Header always shows: Enterprise · Application · Agent · Intent · Outcome (pending/final).

**Playground** (secondary): pick a **configured** intent, optionally another enterprise; not free-text LLM.

## 7.2 EXPLORE navigation

Cross-linked knowledge model, not independent tables.

```
Explore
  DOMAINS
  USE CASES
  INTENTS
  AGENTS
  MY CONTEXT
  PURPOSES
  POLICIES
  AUTONOMY
  CAPABILITIES
  API CATALOG
  PROVIDERS / ROUTES
```

Every entity page shows **neighbors on the five graphs** and a “Run this intent” CTA only if a deep scenario exists.

**API Catalog page:** name, category, CAMARA version, maturity, `operationId`s, capabilities, reverse intents/use cases/domains, sample providers/routes. Forward and reverse.

**My Context:** fictional tenant view — what was onboarded (enterprise profile, identifiers types, subscriptions, agreements, preferred routes). Makes “do not resend what we know” tangible.

## 7.3 Visual language (adapt, don’t clone blindly)

Keep Meta_Demo’s calm operator aesthetic: kicker labels, chips for states, live sequence, click-to-drill.  
Change: domain-first color/story per enterprise; Agent in the actor rail; Policy tab that can **block**.

---

# 8. Live trace model

One execution produces one **trace document**. All five views are projections of it. Selecting a step in any view highlights the same `stepId` in the others.

## 8.1 OVERVIEW

Business-friendly story. No `operationId`s unless the user expands.

- What the application asked  
- What NetAware already knew  
- What complementary network evidence/actions were needed  
- What was blocked / reused / replanned (plain language)  
- Final outcome card  

## 8.2 LIVE FLOW

Who called whom, including **selected route**.

Suggested actors:

```
AGENT / APPLICATION
→ NETAWARE INTENT
→ CONTEXT / POLICY
→ TELCO FINDER
→ API FINDER
→ PROVIDER / ROUTE
→ NETAWARE EXECUTION
→ NETWORK PROVIDER  (or AGGREGATOR, or EXISTING ENTERPRISE INTEGRATION)
→ (optional) DOMAIN / ENTERPRISE API  (simulated complementary call)
```

Show hops lighting in order. Correlation: `intentId` · `executionId` · `traceId`.

## 8.3 DECISIONS

Why each capability/API was `SELECTED` / `NOT_REQUIRED` / `BLOCKED_BY_POLICY` / `EVIDENCE_REUSED` / `REPLANNED` / `NOT_AVAILABLE`.

Must support the canonical examples:

| Question | Decision |
|----------|----------|
| Why NV2 instead of NV1? | Access=Wi-Fi → NV1 unsuitable → NV2 available, subscribed, permitted → SELECT NV2 |
| Why not Location? | Available, relevant, consent missing → BLOCKED_BY_POLICY → REPLAN |
| Why not QoD? | Available, permitted, limiting factor is physical bag transfer → NOT_REQUIRED |
| Why no new API call? | Valid evidence exists → EVIDENCE_REUSED |

**NV1 / NV2 honesty:** CAMARA Number Verification in the pinned spec exposes `phoneNumberVerify` and `phoneNumberShare` (**SOURCE-BACKED**). Mapping “NV1 = mobile-network possession verify, NV2 = Wi-Fi-suitable variant” is **NEEDS REVIEW** against the spec’s access assumptions before implementation. Do **not** invent a third `operationId`. If Wi-Fi path is not actually `phoneNumberShare`, label the decision conceptually and bind to the real operation that the spec supports — or use OTP SMS (`one-time-password-sms`) only if the purpose allows (**SOURCE-BACKED** API, **INFERRED** as NV alternative).

## 8.4 APIs

Technical trace per invocation:

- API name, category, CAMARA version  
- `operationId`  
- provider, route  
- correlation / request ID  
- HTTP status, latency  
- scope / auth **abstraction** (never secrets)  
- evidence generated  
- retry / replan  

## 8.5 POLICY

Purpose, consent, DPA/agreement, residency, security, entitlement, subscription, autonomy evaluation — **per step**, with pass/fail.

If nothing was blocked, still show the checks that passed (otherwise policy looks decorative).

---

# 9. Scenario catalogue (Explorer)

Target: **~40 configured intents**. Only 5 get deep executable treatment (§10). The rest are configuration + Explorer graphs.

Legend: **SB** SOURCE-BACKED · **INF** INFERRED · **NR** NEEDS REVIEW

### Capability library (SB — from Meta_Demo families / catalogue)

Identity & trust: Number Verification, Number Recycling, Tenure, SIM Swap, Device Swap, Device Identifier, Call Forwarding Signal, Age Verification, OTP SMS, Device Authenticity (WIP)  
Location & mobility: Location Verification, Location Retrieval, Geofencing, Roaming, Most Frequent Location, Visit Location (WIP), Population Density, Region Device Count  
Connectivity & quality: Reachability, Connected Network Type, Connectivity Insights, Application Profiles, QoD / QoS Profiles / Provisioning, Session Insights (WIP), Traffic Influence, Predictive Connectivity Data (area forecast only)  
Edge: Simple Edge Discovery, Optimal Edge Discovery, Application Endpoint Discovery/Registration, Edge Application Management (WIP)  
IoT: IoT SIM Fraud Prevention, IoT Network Optimization (WIP), eSIM management (WIP)  
Other catalogue (visible, weak demo unless configured): Carrier Billing, Verified Caller, WebRTC, Dedicated Network, Network Slice, Sponsored Data (WIP), Consent Info/Management (plumbing), Blockchain, Click to Dial, Energy Footprint, MultiPoint VPN, In-Home Device Management

---

| # | Domain | Use case | Intent | Capabilities (SB names) | Domain / Enterprise APIs (fictional stubs) | Network APIs (SB) | Grade |
|---|--------|----------|--------|-------------------------|--------------------------------------------|-------------------|-------|
| 1 | Financial | High-value payment protection | `assess_network_trust` | Number possession, SIM/Device continuity, identifier bind, roaming | Payments, Fraud Decisioning, Core Banking | Number Verification, SIM Swap, Device Swap, Device Identifier, Roaming; Location considered | **SB** (TRUST adapted) |
| 2 | Financial | Silent subscriber check | `verify_subscriber_silently` | Number verification, tenure, recycling | Onboarding, Risk | Number Verification, Tenure, Number Recycling | **SB** (example intent “silent”) |
| 3 | Financial | Bank onboarding assurance | `assess_onboarding_network_trust` | Tenure, recycling, SIM swap, KYC age optional | KYC app, Onboarding | Tenure, Number Recycling, SIM Swap; Age Verification optional | **INF** (example “bank”) |
| 4 | Financial | Account recovery anomaly | `assess_recovery_continuity` | SIM/device swap, call forwarding | IAM, Recovery | SIM Swap, Device Swap, Call Forwarding Signal | **INF** (catalogue use-case notes) |
| 5 | Financial | Step-up authentication assist | `recommend_step_up` | Number verification, OTP SMS | Auth, Fraud | Number Verification; OTP SMS **NR** if Meta-owned pattern | **INF** |
| 6 | Airlines | Baggage connection | `ensure_baggage_connection` | Location verify, reachability, connectivity; QoD considered | Baggage Journey, Flight Status, Ground Ops | Location Verification, Reachability, Connectivity Insights; QoD NOT_REQUIRED in deep demo | **INF** (new hero; APIs SB) |
| 7 | Airlines | Locate bag | `locate_baggage` | Location retrieval/verify, geofence | Baggage Journey | Location Retrieval/Verification, Geofencing | **INF** |
| 8 | Airlines | Crew / ops device experience | `maintain_ops_device_experience` | Profiles, insights, QoD, edge | Crew app | Application Profiles, Connectivity Insights, QoD, Edge Discovery | **INF** |
| 9 | Airlines | Irregular ops passenger notify | `verify_caller_to_passenger` | Verified caller | Passenger comms | Verified Caller / Brand Registration | **NR** (optional catalogue) |
| 10 | Airports | Stand / turnaround camera | `maintain_turnaround_video` | QoD, insights, edge | AODB, Video | QoD, Connectivity Insights, Edge | **INF** |
| 11 | Airports | Geofenced airside asset | `verify_airside_presence` | Geofence, location verify | Asset registry | Geofencing, Location Verification | **INF** |
| 12 | Manufacturing | Critical inspection camera | `maintain_inspection_experience` | Profiles, insights, edge, QoD closed-loop | MES, QMS, Camera control | Application Profiles, Connectivity Insights, Edge, QoD | **SB** (ASSURE + industrial example) |
| 13 | Manufacturing | IoT line integrity | `assess_iot_sim_integrity` | IoT SIM fraud, device identifier | MES, OT security | IoT SIM Fraud Prevention, Device Identifier | **INF** (IoT APIs SB) |
| 14 | Manufacturing | Predictive coverage for AGV path | `forecast_site_coverage` | Predictive connectivity (area, not per-UE) | WMS, AGV | Predictive Connectivity Data | **SB** honesty constraint |
| 15 | Warehouse / Logistics | Dock-to-stock scan experience | `maintain_scan_session` | Insights, QoD | WMS | Connectivity Insights, QoD | **INF** |
| 16 | Warehouse / Logistics | High-value shipment custody | `verify_shipment_device_presence` | Location verify, geofence, reachability | TMS, Yard | Location Verification, Geofencing, Reachability | **INF** |
| 17 | Retail | Checkout / payout trust | `assess_checkout_trust` | SIM/device continuity, number verify | POS, Payments, Fraud | Number Verification, SIM Swap, Device Swap | **INF** |
| 18 | Retail | Age-restricted sale | `verify_age_threshold` | Age verification | POS, Loyalty | KYC Age Verification | **SB** (AGE intent) |
| 19 | Retail | In-store experience / AR | `maintain_instore_experience` | QoD, edge, network type | Associate app | QoD, Edge, Connected Network Type | **INF** |
| 20 | Retail | Crowd-aware staffing | `observe_region_density` | Population density / region count | Workforce | Population Density, Region Device Count | **NR** (privacy/purpose heavy) |
| 21 | Insurance | FNOL device continuity | `assess_claim_device_trust` | SIM/device swap, identifier | Claims, FNOL | SIM Swap, Device Swap, Device Identifier | **INF** |
| 22 | Insurance | Claim location consistency | `verify_claim_location` | Location verify, roaming, most frequent | Claims | Location Verification, Roaming, Most Frequent Location | **INF** |
| 23 | Healthcare | Pharmacy age / eligibility | `verify_pharmacy_age_gate` | Age verification | Pharmacy, EHR (enterprise stays) | KYC Age Verification | **INF** (API SB) |
| 24 | Healthcare | Home-care visit verify | `verify_visit_in_geofence` | Geofence, location verify, consent-critical | Scheduling | Geofencing, Location Verification, Consent Info | **INF** |
| 25 | Healthcare | Telehealth session quality | `maintain_telehealth_experience` | Profiles, insights, QoD | Telehealth | Application Profiles, Connectivity Insights, QoD | **INF** |
| 26 | Media | Live broadcast / contribution | `assure_live_broadcast` | QoD, insights, edge, traffic influence | Broadcast control | QoD, Connectivity Insights, Edge, Traffic Influence | **SB** (future “broadcast”) |
| 27 | Media | Streaming rate assist | `observe_media_streaming_rate` | Media streaming rate (WIP) | Player | Device Media Streaming Rate | **NR** (WIP) |
| 28 | Construction | Site camera / safety uplink | `maintain_site_uplink` | Insights, QoD, reachability | HSE, VMS | Connectivity Insights, QoD, Reachability | **INF** |
| 29 | Construction | Geofenced equipment | `verify_equipment_on_site` | Geofence, IoT SIM | Asset | Geofencing, IoT SIM Fraud Prevention | **INF** |
| 30 | Stadium / Venue | Age-gated concession | `verify_venue_age_gate` | Age verification | POS | KYC Age Verification | **INF** |
| 31 | Stadium / Venue | Dense-crowd experience | `maintain_venue_experience` | QoD, slice/dedicated net **NR**, density **NR** | Fan app | QoD; Dedicated Network / Slice **NR** | **INF** / **NR** |
| 32 | Stadium / Venue | Staff radio / app quality | `maintain_staff_comms` | QoD, insights | Ops | QoD, Connectivity Insights | **INF** |
| 33 | Financial | Related-activity correlation | `correlate_network_identifiers` | Device identifier + reuse; **no CAMARA graph API** | Fraud graph (enterprise) | Device Identifier; NetAware-derived clusters | **SB** (EXPAND honesty) |
| 34 | Any / Platform | Maintain app SLO | `maintain_application_experience` | Profiles, insights, edge, QoD | App RUM | Application Profiles, Connectivity Insights, Edge, QoD | **SB** (ASSURE generalized) |
| 35 | Any / Platform | Discover available network capabilities | `discover_network_capabilities` | Catalogue + finder | — | API Finder / registry (not a CAMARA call) | **SB** (product capability) |
| 36 | IoT / Utilities | eSIM profile lifecycle | `manage_iot_esim_profile` | eSIM management (WIP) | Device mgmt | eSIM Profile / Remote Management | **NR** (WIP) |
| 37 | Home / Broadband | In-home device management | `manage_home_network_device` | In-home / access mgmt (WIP) | CSP portal | In-Home Device Management, Network Access | **NR** |
| 38 | Automotive / Mobility | Area coverage for route | `forecast_route_coverage` | Predictive connectivity | Navigation | Predictive Connectivity Data | **SB** (area forecast) |
| 39 | Public safety / Venue | Geofence incident device | `verify_device_in_zone` | Geofence, location | CAD | Geofencing, Location Verification | **INF** |
| 40 | Enterprise comms | Branded outbound call | `place_verified_business_call` | Verified caller | CCaaS | Verified Caller, Brand Registration | **NR** |
| 41 | Payments | Carrier billing checkout | `charge_via_carrier_billing` | Carrier billing | Checkout | Carrier Billing | **NR** (clutter in Meta_Demo) |
| 42 | Edge apps | Place workload near device | `discover_optimal_edge` | Edge discovery, traffic influence | App platform | Simple/Optimal Edge Discovery, Traffic Influence | **INF** |
| 43 | Security | Device authenticity check | `check_device_authenticity` | Device authenticity (WIP) | MDM | DeviceAuthenticity | **NR** (WIP) |
| 44 | Consent ops | Inspect consent plumbing | `inspect_consent_state` | Consent info/management | Privacy | Consent Info, Consent Management | **SB** plumbing; not a hero |
| 45 | Network ops | Health / traffic analysis | `observe_network_health` | Network insights | NOC | Network Health / Traffic Analysis | **NR** |

Do **not** build 45 workflows. Rows 1, 6, 12, 18, 33 (or 17) are deep-demo candidates. Others are Explorer configuration linking real catalogue entries to fictional domains.

**Explicitly not fabricated:** new CAMARA `operationId`s, a CAMARA identity-graph API, PredictiveConnectivityData as per-UE session predictor, live operators.

---

# 10. Deep demo scenarios (recommend 5)

Shared simulation rules: no LLM; pinned catalogue; fictional names; RESET restores all.

---

## 10.1 Rocket Bank — Assess network trust

| Field | Value |
|-------|-------|
| Enterprise | Rocket Bank |
| Application | Payments |
| Agent | Payments Protection Agent |
| Domain | Financial |
| Use case | High-value payment protection |
| Intent | `assess_network_trust` |
| Runtime request | `{ "intent": "assess_network_trust", "subject": { "transactionId": "RB-25000-9182", "amountUsd": 25000, "payerNetworkId": "+1-416-xxx-xxxx" }, "context": { "channel": "mobile_app", "access": "wifi" } }` |
| Already known | Tenant, agent allowlist, purpose `payment_fraud_assist`, subscriptions, DPA CA-processing, evidence budget, **cannot decline the payment** |
| Purpose | `payment_fraud_assist` |
| Policy | Identity/continuity APIs permitted; Location consent required; Call Forwarding not required once confidence met |
| Autonomy | Evidence gather **ACT**; STEP_UP **RECOMMEND**; decline transaction **NOT AUTHORIZED** |
| Capabilities | Number possession, SIM/device continuity, device identifier, roaming; location considered |
| Domain / Enterprise APIs | Payments API, Fraud Decisioning (enterprise keeps final decision) |
| Network APIs | `phoneNumberVerify` / `phoneNumberShare` (**NR** which fits Wi-Fi), `checkSimSwap`, `retrieveSimSwapDate`, `checkDeviceSwap`, `retrieveDeviceSwapDate`, `retrieveIdentifier`, `getRoamingStatus`; `verifyLocation` considered |
| Telco Finder | Subject → Simulated Operator A (home), roaming flag if seed says so |
| API Finder | Operator A vs Aggregator B capability ads (from Meta_Demo pattern, independently re-seeded) |
| Route | Number verify **DIRECT** to Operator A; Device Identifier **AGGREGATED** via Aggregator B (**SB** pattern) |
| Initial plan | Possession → recycling/tenure → SIM/device swap → identifier → roaming; location if still uncertain |
| Invoked | Continuity set (scripted; counts analogous to TRUST 9, not necessarily identical) |
| Considered not invoked | Call Forwarding (`retrieveUnconditionalCallForwarding`) — confidence already sufficient (**SB** why-not) |
| Policy block | If access=Wi-Fi: NV1/`phoneNumberVerify` **NOT_AVAILABLE** or unsuitable → SELECT NV2/real alternate; Location **BLOCKED_BY_POLICY** if consent missing |
| Evidence reuse | Later `correlate_network_identifiers` would reuse identifier (**optional follow**) |
| Replan | Skip blocked location; use roaming instead (**SB** TRUST why-not location) |
| Outcome | `STEP_UP` · Network continuity disrupted · Confidence `HIGH` |
| Autonomy visible | Recommendation only; Rocket Bank Fraud Decisioning owns accept/reject |

Example response:

```json
{
  "intent": "assess_network_trust",
  "outcome": "STEP_UP",
  "confidence": "HIGH",
  "summary": "Network identity continuity disrupted for this $25,000 transaction.",
  "recommendedAction": "STEP_UP_VERIFICATION",
  "decisionOwner": "ROCKET_BANK",
  "evidence": {
    "numberPossession": "VERIFIED_VIA_WIFI_SUITABLE_PATH",
    "simChange": "RECENT",
    "deviceChange": "RECENT"
  },
  "traceId": "…"
}
```

---

## 10.2 High Flight Airlines — Ensure bag makes connection

| Field | Value |
|-------|-------|
| Enterprise | High Flight Airlines |
| Application | Baggage Operations |
| Agent | Baggage Operations Agent |
| Domain | Airlines |
| Use case | Baggage connection |
| Intent | `ensure_baggage_connection` |
| Runtime request | `{ "intent": "ensure_baggage_connection", "subject": { "bagId": "HF123456", "connectingFlight": "HF281" }, "context": { "priority": "high" } }` |
| Already known | Hub airport, bag tag ↔ handler device mapping, subscriptions, purposes, **expedite is ACT_WITH_APPROVAL** |
| Purpose | `baggage_connection_assurance` |
| Policy | Location: purpose ok, subscribed, region ok, DPA ok, **consent required**, **consent not available** on handler personal device; QoD permitted but not for physical transfer |
| Autonomy | Observe/assess **ACT**; recommend expedite **ACT_WITH_APPROVAL**; change flight plan **NOT AUTHORIZED** |
| Capabilities | Location verify, reachability, connectivity insight; QoD considered |
| Domain APIs | Baggage Journey, Flight Status |
| Enterprise APIs | Ground Operations |
| Network APIs | `verifyLocation` (blocked), `getReachabilityStatus`, `checkNetworkQuality` / Connectivity Insights; `createSession` QoD **NOT_REQUIRED** |
| Telco Finder | Handler device MSISDN → Simulated Operator A at hub |
| API Finder | Location on Provider C; reachability on Operator A |
| Route | Reachability **DIRECT**; Location would have been **AGGREGATED** had consent existed |
| Initial plan | Confirm remaining time via Flight Status (domain) → verify handler/bag vicinity (network location) → if late, consider QoD for scanner vs **physical** transfer |
| Invoked | Domain Flight Status + Baggage Journey (simulated); `getReachabilityStatus`; Connectivity Insights |
| Considered not invoked | QoD — limiting factor is physical transfer, not uplink |
| Policy block | Location Verification `BLOCKED_BY_POLICY` (consent) |
| Replan | Use reachability + Ground Ops ETA; do not invent location |
| Evidence reuse | Reachability TTL allows second intent `locate_baggage` without recall |
| Outcome | `AT_RISK` · Recommended `EXPEDITE_TRANSFER` · Approval required |

```json
{
  "intent": "ensure_baggage_connection",
  "outcome": "AT_RISK",
  "recommendedAction": "EXPEDITE_TRANSFER",
  "approvalRequired": true,
  "reasons": [
    "Connection window is tight per Flight Status",
    "Location verification blocked: consent not available",
    "Device reachable; QoD not required — constraint is physical transfer"
  ],
  "complements": ["BaggageJourney", "FlightStatus", "GroundOperations"]
}
```

This is the **clearest AX complementarity** story. Do not skip it.

---

## 10.3 Acme Manufacturing — Maintain inspection camera

| Field | Value |
|-------|-------|
| Enterprise | Acme Manufacturing |
| Application | Quality Inspection |
| Agent | Inspection Experience Agent |
| Domain | Manufacturing |
| Use case | Critical inspection camera |
| Intent | `maintain_inspection_experience` |
| Runtime request | `{ "intent": "maintain_inspection_experience", "subject": { "cameraId": "ACME-CAM-14", "lineId": "LINE-B" }, "context": { "sloMs": 40 } }` |
| Already known | SLO, EU/plant residency, QoD entitlement, autonomy ACT for QoD, plant operator route |
| Purpose | `inspection_video_assurance` |
| Policy | Experience APIs permitted; identity/KYC **not** authorized; PredictiveConnectivityData **not** a session oracle |
| Autonomy | Observe + QoD **ACT**; change MES routing **NOT AUTHORIZED** |
| Capabilities | Application Profiles, Connectivity Insights, Edge Discovery, QoD |
| Domain / Enterprise APIs | MES, QMS, Camera control |
| Network APIs | `createApplicationProfile`, `checkNetworkQuality`, `readClosestEdgeCloudZone`, `retrieveQoSProfiles`, `createSession`, `getSession` (**SB** ASSURE set) |
| Telco Finder | Plant device → Simulated Operator A / private overlay **HYBRID** |
| API Finder | Experience ops on Provider C (**SB** pattern) |
| Route | **HYBRID**: insights DIRECT; QoD via aggregator if configured |
| Initial plan | Profile → observe → edge if useful → **skip QoD** if SLO met |
| Invoked | Profile, insights, edge; later QoD + getSession |
| Considered not invoked | QoD **earlier** (`NOT_REQUIRED`); identity APIs never in plan |
| Replan | When observe shows SLO miss → QoD `INVOKED` → `VERIFIED` |
| Outcome | `ASSURED` · Required service objective restored |

```json
{
  "intent": "maintain_inspection_experience",
  "outcome": "ASSURED",
  "objective": "SATISFIED",
  "sloMs": 40,
  "actions": { "qod": "INVOKED_AFTER_REPLAN", "edge": "CONSIDERED" }
}
```

---

## 10.4 MegaMart — Checkout trust (policy + reuse)

| Field | Value |
|-------|-------|
| Enterprise | MegaMart |
| Application | Store Payments |
| Agent | Checkout Protection Agent |
| Domain | Retail |
| Use case | Checkout / payout trust |
| Intent | `assess_checkout_trust` |
| Runtime request | `{ "intent": "assess_checkout_trust", "subject": { "checkoutId": "MM-8831", "networkId": "+1-647-xxx-xxxx" }, "context": { "storeId": "TOR-14" } }` |
| Already known | Same continuity subscriptions as Rocket Bank variant; store Wi-Fi; consent for location **no** |
| Purpose | `checkout_fraud_assist` |
| Policy | Same identity stack; location blocked without consent |
| Autonomy | Evidence **ACT**; STEP_UP **RECOMMEND**; void sale **NOT AUTHORIZED** |
| Telco / API Finder | Same simulated providers |
| Route | DIRECT number path; AGGREGATED device identifier |
| Invoked | Continuity subset |
| Policy block | Location |
| Evidence reuse | If a second intent runs in-session, SIM swap evidence `EVIDENCE_REUSED` |
| Outcome | `STEP_UP` or `PROCEED` depending on seed (script: STEP_UP on swap) |

Shows **same intent family, different enterprise config** — configuration-driven, not a new engine.

---

## 10.5 CityCare Health — Age gate (consent-sensitive catalogue)

| Field | Value |
|-------|-------|
| Enterprise | CityCare Health |
| Application | Pharmacy |
| Agent | Pharmacy Eligibility Agent |
| Domain | Healthcare |
| Use case | Age-restricted dispensing |
| Intent | `verify_pharmacy_age_gate` |
| Runtime request | `{ "intent": "verify_pharmacy_age_gate", "subject": { "rxId": "RX-10442", "networkId": "+1-416-xxx-xxxx" }, "context": { "threshold": 18 } }` |
| Already known | Purpose `pharmacy_age_assertion`, Age Verification subscribed, DPA permits age assertion **not** KYC Match PII, autonomy RECOMMEND |
| Purpose | `pharmacy_age_assertion` |
| Policy | `verifyAge` permitted; `kyc-match` **BLOCKED_BY_POLICY** (agreement: no PII match) |
| Autonomy | Call Age Verification **ACT**; refuse dispense **RECOMMEND** (pharmacist owns) |
| Network APIs | `verifyAge` (**SB**); KYC Match listed as blocked |
| Outcome | `ELIGIBLE` / `NOT_ELIGIBLE` + `RECOMMEND` to pharmacist |

Proves catalogue **select vs block** inside the same family (Age vs Match).

---

# 11. API Catalog strategy

## 11.1 Substrate

Independently pin CAMARA OpenAPI YAML + a manifest into NetAware AX (`data/catalog/` or `openapi/`).

- Parse to Operations (`operationId`, path, method, api_name, version, maturity).
- Do not invent operations. Superseded DeviceStatus / KnowYourCustomer parent packs: keep for reference, **prefer split repos** (Meta_Demo policy).
- Annotate with capability IDs, privacy class, simulated cost/latency (TOOL_META pattern, recreated).

Count (~273 in Meta_Demo) is a **registry metric**, displayed on Catalog and on economy strips — not the Home headline.

## 11.2 Dual exploration

**Business → API:** Domain → Use Case → Intent → Capability → Operations.  
**API → Business:** Operation → Capability → Intents → Use Cases → Domains.

Deep traces always deep-link to the Catalog record.

## 11.3 Finder + routes

Telco Finder and API Finder stay first-class (Meta_Demo `discovery.py` pattern, new data).

Routes are data:

| Route | Meaning |
|-------|---------|
| DIRECT | NetAware → Network Provider |
| AGGREGATED | NetAware → Aggregator → Provider |
| HYBRID | Mix per API/region/config |
| EXISTING_ENTERPRISE_INTEGRATION | Enterprise already has a path; NetAware coordinates, **does not claim to proxy every call** |

Do not lock hosting (customer-hosted NetAware vs NetAware-hosted). Prototype shows **route types**, not a commercial topology decision.

---

# 12. Project architecture (NetAware AX)

Independent repo. **No runtime import, git submodule, or API call to Meta_Demo.**

```text
NetAware AX/
  README.md
  docs/
    ax-prototype-plan.md          ← this document
    cadences/                     ← one report per cadence (later)
  data/
    catalog/                      ← independently pinned OpenAPI + manifest
    model/                        ← domains, intents, capabilities, policies, enterprises
    worlds/                       ← seed worlds per deep scenario
  backend/
    app/                          ← FastAPI: catalog, intent runtime, traces, explore API
    scripts/                      ← validate_ax_cadenceN.py
  frontend/
    src/                          ← Demo + Explore (React + Vite, matching stack familiarity)
  tests/
```

Stack recommendation: **same family as Meta_Demo** (FastAPI + React/Vite, deterministic in-memory or file-backed state) so recreation is fast — implemented **anew**, not copied.

Simulation: operator mocks from seed worlds; domain/enterprise APIs as stub adapters with explicit `kind: DOMAIN|ENTERPRISE|NETWORK`.

---

# 13. Cadence plan (AX — independent numbering)

Small, testable, reversible. Each cadence has an explicit stop.

---

## AX Cadence 0 — Foundation lock

**Objective.** Repository skeleton, data shapes, independently pinned catalogue, no product UI yet.

**User-visible result.** README + plan; `GET /health` with `cadence: 0` and `registryLoaded: true`.

**Data/model.** Entity JSON schemas; copy/pin OpenAPI (independent files); capability ID map for operations used in §10.

**Frontend.** None (or static “planning” page — prefer none).

**Backend.** Registry parser; health; forbidden real-operator-name test (from Meta_Demo idea).

**Meta_Demo adapted.** Registry honesty; pin policy; no invented ops.

**New.** AX cadence numbering; fictional enterprise IDs.

**Acceptance.** Registry loads; operationIds ⊆ spec; health green.

**Tests.** `validate_ax_cadence0.py`

**Risks.** Catalogue copy drift vs Meta_Demo pin date — document pin date in manifest.

**Deferred.** UI, runtime, policies.

**Stop.** No Demo UI. No intent execution.

---

## AX Cadence 1 — Zero-context shell + Explorer graph (read-only)

**Objective.** Audience can enter a domain and see configured knowledge without running anything.

**User-visible result.** Home → pick Rocket Bank / High Flight / Acme. Briefing shows the 10 questions (9–10 marked “after run”). Explore: Domains, Intents, API Catalog reverse/forward for **mapped** rows only.

**Data/model.** 3 enterprises, 3 applications, 3 agents, ~15 intents (including 5 deep IDs), capability links for those intents.

**Frontend.** Home, briefing, Explore list/detail. No live trace yet.

**Backend.** Read APIs: `/explore/*`, `/enterprises/*`.

**Meta_Demo adapted.** Calm visual language; Catalog as first-class; **not** TRUST/EXPAND/ASSURE nav.

**New.** Agent vs Application; Domain/Enterprise/Network API labels.

**Acceptance.** Zero-context test for a newcomer on High Flight briefing. No real brands.

**Tests.** Explore fixtures resolve; every Explorer intent has ≥1 SB operation or is labeled NR.

**Risks.** Over-building Explore before a working run.

**Deferred.** Execution.

**Stop.** No POST /intents runtime.

---

## AX Cadence 2 — First live AX run (Rocket Bank)

**Objective.** One deep scenario, fully traced, deterministic.

**User-visible result.** Run Rocket Bank. Five tabs sync. Outcome `STEP_UP`. Economy strip. Expandable JSON.

**Data/model.** Seed world (continuity break; Wi-Fi access). Decision script.

**Frontend.** Deep workspace: Overview, Live Flow, Decisions, APIs, Policy (Policy may still be “all pass” except NV access-type).

**Backend.** `POST /intents`, step/stream, trace document.

**Meta_Demo adapted.** Stepwise agent, ToolActivity, DecisionTrace, LiveTrace, ToolDetail, WHY_SELECTED/NOT.

**New.** Tiny intent JSON; “already knows” panel; Agent actor; domain outcome card.

**Acceptance.** Same run twice → same outcome/states. Real operationIds on APIs tab. No Meta copy.

**Tests.** Golden trace for Rocket Bank.

**Risks.** Porting TRUST too literally (Instagram leftover).

**Deferred.** Consent block, airline, QoD loop.

**Stop.** Only one executable intent.

---

## AX Cadence 3 — Operational policy + replan

**Objective.** Policy changes the plan.

**User-visible result.** High Flight run: Location `BLOCKED_BY_POLICY` → REPLAN; QoD `NOT_REQUIRED`; outcome `AT_RISK` + approval. Policy tab shows consent miss. Complementary Domain/Enterprise APIs visible on Live Flow.

**Data/model.** ConsentRule + ConsentState; AutonomyRule ACT_WITH_APPROVAL; airline seed.

**Frontend.** Policy tab failures; replan marker on Live Flow and Decisions.

**Backend.** Policy evaluator in the shared interpreter.

**Meta_Demo adapted.** Replan beats; NOT INVOKED; **upgrade** from static governance cards.

**New.** BLOCKED_BY_POLICY state; domain API stubs.

**Acceptance.** Flipping consent in config (test fixture) changes Location from BLOCKED to SELECTED without code change.

**Tests.** Policy matrix golden.

**Risks.** Legal over-claim. Mitigation: “configured” copy only.

**Deferred.** Remaining deep scenarios.

**Stop.** Two executable intents (Bank + Airline).

---

## AX Cadence 4 — Closed loop + catalogue block (Acme + CityCare)

**Objective.** Observe → skip → replan → act → verify; plus API-family block (Age vs KYC Match).

**User-visible result.** Acme: QoD not invoked, then invoked, `ASSURED`. CityCare: `verifyAge` invoked, KYC Match blocked.

**Data/model.** Experience seed; age seed; hybrid route on Acme.

**Frontend.** Same workspace; autonomy ACT vs RECOMMEND chips.

**Backend.** ASSURE-like loop in generic interpreter (no dedicated “assure engine”).

**Meta_Demo adapted.** QoD history EARLIER/LATER; age intent; evidence verify `getSession`.

**New.** ACT_WITH_APPROVAL already on airline; ACT on plant QoD.

**Acceptance.** QoD NOT_REQUIRED then INVOKED in one execution. Match API never invoked.

**Tests.** Goldens for Acme + CityCare.

**Risks.** Fourth engine appearing. Mitigation: one interpreter.

**Deferred.** MegaMart; 40-intent Explore fill; EXPAND graph.

**Stop.** Four executable intents.

---

## AX Cadence 5 — Explorer breadth + MegaMart reuse

**Objective.** Configuration scale + EVIDENCE_REUSED.

**User-visible result.** Explorer populated ~40 intents with SB/INF/NR badges. MegaMart run reuses evidence. Reverse catalog navigation complete. Providers/Routes pages.

**Data/model.** Remaining catalogue mappings; MegaMart tenant clone of trust family; evidence TTL.

**Frontend.** Five graph visualizations (even simple node lists with links beat fake 3D).

**Backend.** Evidence store; reuse decisions.

**Meta_Demo adapted.** EVIDENCE_REUSED; capability families; playground as “run configured intent.”

**New.** Badge honesty; My Context.

**Acceptance.** Every Explorer intent cites real operationIds or is NR. Reuse golden.

**Tests.** Mapping coverage; no invented operationIds.

**Risks.** Fake-precise mappings. Mitigation: badges required in UI.

**Deferred.** MCP, self-service access, LLM, live operators, identity protocol.

**Stop.** No fifth engine. MegaMart is config clone + reuse.

---

## AX Cadence 6 — Presenter freeze

**Objective.** Demo script, reset, hosted-or-local runbook, honesty pass.

**User-visible result.** 7–10 min path: Home → Airline (wow complementarity + policy) → Bank (trust/autonomy) → Factory (closed loop) → Explore catalog. Optional CityCare.

**Data/model.** Freeze seeds.

**Frontend.** Polish, empty-state honesty, RESET.

**Backend.** `/reset`; build id.

**Meta_Demo adapted.** Presenter-runbook spirit; demo freeze discipline; **new** script (no Meta).

**New.** AX freeze doc.

**Acceptance.** Zero-context checklist (§ final quality check) passable by a colleague not in telecom.

**Tests.** Smoke + goldens still green.

**Risks.** Scope creep (EXPAND graph, stadium, MCP).

**Deferred.** Everything in “Questions deferred.”

**Stop.** **PRODUCT LOGIC FROZEN** pending feedback. No Cadence 7 in this plan.

---

# 14. Recommended first build (after approval)

**Implement AX Cadence 0 only**, then stop for review.

Concrete first implementation set (still not to be done until you approve):

1. Repo skeleton (`backend/`, `frontend/` placeholder, `data/catalog/`, `data/model/`, `scripts/`).  
2. Independently pin OpenAPI + manifest (document pin date; no Meta_Demo runtime).  
3. Registry loader + health.  
4. JSON schemas for Enterprise, Application, Agent, Intent, Capability, Operation.  
5. `validate_ax_cadence0.py`.  
6. Short `docs/cadences/ax-cadence-0.md` after it passes.

**Do not** start Home UI, traces, or Rocket Bank runtime until Cadence 0 is accepted.

Suggested sequence after that: **C1 shell → C2 Rocket Bank live → C3 High Flight policy** (airline is the AX thesis; bank is the proven Meta_Demo motion with new clothing). If a single live demo must land earlier, swap C2/C3 only with explicit approval — airline needs domain stubs, so bank is the safer first *runtime*.

---

# Final quality check (must be visible in the shipped prototype)

| Question | Where it is answered |
|----------|----------------------|
| What is my domain? | Home door + briefing |
| What systems/APIs do I already have? | Briefing · Overview · Live Flow (DOMAIN/ENTERPRISE) |
| How do Network APIs complement them? | Briefing split list + airline scenario |
| Who is my Agent? | Header + My Context |
| What does NetAware already know? | My Context + briefing “already known” |
| What am I sending at runtime? | Tiny JSON panel |
| What does Intent mean? | Home one-liner + briefing |
| Purpose? Policy? Consent/DPA/sovereignty/security? | Policy tab + Explore |
| What autonomy have I granted? | Briefing + per-action chips |
| Intent → Use Case → Capabilities → Catalog? | Overview + Explore + Decisions |
| Telco Finder? API Finder? Provider? Route type? | Live Flow + Resolution |
| Which CAMARA APIs considered / invoked / not / why? | APIs + Decisions |
| Blocked by policy? Evidence reused? Replan? | Decisions + Policy |
| Who called whom? What came back? | Live Flow + APIs |
| Why each decision? | Decisions |
| Final business outcome? | Outcome card + JSON |
| **Does it feel agentic?** | Loop is visible, policy can stop it, autonomy is bounded, plan changes, outcome is domain-native |

Audience conclusion we are designing for:

> I tell NetAware what outcome I need.  
> It understands my context and rules.  
> It figures out which network capabilities can complement my application.  
> It handles the complexity.  
> I can see exactly what it did and why.  
> My application gets back something it understands.

---

# Questions deferred (do not decide in Cadence 0–3)

- Production agent identity / delegation protocol  
- Hosting model (customer-hosted vs NetAware-hosted vs federated)  
- Whether NetAware proxies every call vs coordinates existing integrations  
- MCP / agent tool interface  
- LLM / NL intent mapping  
- Pricing, metering UI, SLA bidding  
- Real operators, real CAMARA, real enterprise IdP  
- Self-service access / sales motion  
- EXPAND-style device clustering as a hero (honesty: not a CAMARA graph API)  
- NV1 vs NV2 exact `operationId` binding for Wi-Fi (**NEEDS REVIEW** before C2 script freeze)

---

**STOP.** No application implementation until Cadence 0 is explicitly approved.
