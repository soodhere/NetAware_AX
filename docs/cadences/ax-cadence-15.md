# Cadence 15 — Stakeholder sales experience

Status: complete. Cadence 16 not started.

Cadence 12–14 built product depth (problems, fulfillment, qualified demand). Cadence 15 does **not** add another major product model. It answers:

**How does a salesperson show the right NetAware AX story to the right person in a few minutes?**

Live version remains `0.6.1-ax6.1`. Model cadence remains 7. UI cadence is **15**. Stakeholder choice is presentation context only. Runtime, policy, discovery, coverage, demand, catalog, and Intent execution are unchanged.

## 1. Stakeholder entry model

After access, `#/` is **Welcome to NetAware AX**, not the old Home dump.

Primary statement: **NetAware connects enterprise demand to network supply.**

Three perspectives plus Explore the product. Selection is stored in `sessionStorage` (`netaware-ax-stakeholder`). It changes starting page, recommended story, headlines, and CTA. It is not authorization, tenant isolation, personalization, or a different engine.

## 2. Enterprise experience

Headline: *Start with your application, not a Network API.* Cards for Digital Identity, Connected Device Operations, Baggage Operations, Quality Inspection. Primary CTA: *See how an application uses network intelligence.*

## 3. Operator experience

Headline: *Turn network capabilities into enterprise outcomes.* Three questions: enable today, qualified demand, readiness gap. Capability tiles consume C13 + C14.

## 4. Aggregator experience

Headline: *Turn fragmented network supply into consistent enterprise fulfillment.* Regions → providers → capabilities → routes → Intents. Wording: routed through / normalized through / available via. Aggregator A does not own operator APIs.

## 5. Recommended story for each

- Enterprise: Rocket Bank Mobile Sign-In
- Operator: Number Verification / NV1–NV2 / ECS
- Aggregator: multi-region capability fulfillment via Aggregator A

Then: Explore more use cases. Core story vs optional drill-downs are identified. No timers. Meeting Mode is not implemented.

## 6. Shared-product architecture

One product, one Explorer, one coverage engine, one demand model, one runtime. Landings are hash routes (`#/start/enterprise|operator|aggregator`) over the same APIs.

## 7. Business / Technical views

Internal lens remains BASIC / ADVANCED (sessionStorage, no rerun). Presented as **BASIC — Business View** and **ADVANCED — Technical View**. Coverage and Demand use the same Business / Technical labels.

## 8. Rocket Bank Enterprise story

Application asks to verify this mobile number — not NV1/NV2/ECS/`operationId`. Cellular NV1, Wi-Fi NV2, Wi-Fi plus readiness gap = capability unavailable. One Intent, different network conditions, NetAware selects the feasible path.

## 9. NV Operator story

Provider A fulfills configured cellular and Wi-Fi demand. Provider B cannot fulfill configured Wi-Fi demand because ECS is not ready. API exposure is only one part of fulfillment. Enablement impact, not revenue opportunity.

## 10. Acme OTA story

Enterprise: NetAware does not install firmware; it adds network readiness to the OTA decision. Supply: Provider C Reachability available, Roaming not available → 500-device simulated qualified-demand gap. Not 500 sales.

## 11. High Flight story

BRS / DCS / ramp assignment already exist. Network adds DATA reachability. Network does not track or move the bag. CONTINUE or SWAP DEVICE.

## 12. Aggregator multi-region story

Telco Finder → API Finder → direct / aggregated supply → normalized capability. Example: Aggregator A → Germany → Provider B → Device Reachability → aggregated route → configured applications including Northstar Claims.

## 13. Capability Discovery presentation

Application/Intent → potentially relevant → configured eligibility → runtime feasibility → select / call / reuse / skip / filter / unavailable. Business View summarizes; Technical View shows fields. Same engine.

## 14. Explorer integration

No Enterprise/Operator/Aggregator Explorers. Contextual links into the same graph: applications/intents/motions; capabilities/demand/coverage; providers/regions/routes.

## 15. Fulfillment integration

Operator and aggregator CTAs land on Coverage. C13 remains fulfillment truth.

## 16. Demand integration

Operator tiles and NV recommended story land on Demand Map. C14 remains demand source.

## 17. Product map

BUSINESS → PORTFOLIO → INTENT → DISCOVERY → FULFILLMENT → OUTCOME. Explorer = product knowledge. Demand Map = demand/supply intelligence.

## 18. Why NetAware story

Per audience, then shared chain: Intent → capability demand → governed discovery → operator/aggregator supply → fulfillment → outcome. Close: NetAware connects enterprise demand to network supply.

## 19. DX → AX treatment

Home still tells DX → AX. Welcome adds: AX sits above and complements Network API DX. Developers do not disappear.

## 20. Agentic Experience treatment

Existing scenarios prove the loop (Rocket Bank, High Flight, Acme inspection, CityCare, OTA, NV). No new agent framework. Intent consumers can include applications or authorized agents. No live MCP claim.

## 21. TMF931 treatment

Technical copy may say TMF931-aligned onboarding context where the existing mapping supports it. Not a full TMF931 compliance claim.

## 22. DPV treatment

Business View: human purpose. Technical View: DPV identifier. DPV is governance provenance, not the story.

## 23. Basic Auth implementation

Existing server-side HTTP Basic middleware. Protects frontend and API except `/health`. No user accounts, SSO, OAuth, RBAC, or tenant login.

## 24. Credential/environment configuration

Reads `BASIC_AUTH_USERNAME` / `BASIC_AUTH_PASSWORD`, falling back to `DEMO_USERNAME` / `DEMO_PASSWORD`. If unset, local bypass remains (gate off). Hosting secrets via Render `sync: false`. Credentials are never committed, logged, or bundled in JavaScript.

## 25. Perspective switching

Footer **Change perspective** returns to Welcome. No logout, no new credentials, no execution reset, no data reset.

## 26. Reset/replay behavior

Runtime Reset / Replay / Step / Pause, NV selectors, High Flight selectors, OTA reassessment, and evidence reuse are untouched. Stakeholder UI does not call `/intents`.

## 27. Deployment compatibility

Same single-service host. No database, Redis, IdP, or second web service.

## 28. Regression tests

`backend/scripts/validate_ax_cadence15.py` nests Cadence 0–14. Live heroes, 17 use cases, 13 families unchanged.

## 29. Known gaps

- Stakeholder choice does not filter Explorer or hide surfaces.
- No Meeting Mode, timers, or presenter automation.
- No MCP/A2A, revenue, TAM, CRM, or Cadence 16.
- Configured demo coverage only. Fictional providers.

**STOP. Do not start Cadence 16.**
