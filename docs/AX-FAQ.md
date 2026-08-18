# AX FAQ

Accurate to the NetAware AX prototype (Cadence 6). Not production claims.

## What is AX?

**Agentic Experience** — the application or authorized agent expresses an **outcome** (Intent). NetAware understands context, applies governance, discovers capabilities, plans, executes, observes, replans, and verifies using complementary Network APIs where useful. The caller receives a **business outcome**.

## What is Intent?

The outcome the application or agent wants — **without** specifying which Network APIs should be called. Intent is not a use case, API bundle, policy, prompt, or workflow.

## Why not just call APIs directly?

Direct calls work when you know the operation, provider, policy context, and orchestration. AX reduces application burden: configured context is reused, capabilities are selected minimally, policy is enforced, and traces are unified.

## Does Intent replace CAMARA?

No. Intent sits above CAMARA operations. The active catalog still exposes real `operationId`s. Intent chooses *when* and *whether* to invoke them under governance.

## How does NetAware know the context?

From **onboarding / configuration**: enterprise, application, agent, purpose, subscriptions, entitlements, policy, consent, DPA, routes, autonomy. The runtime request stays small.

## Where does Purpose come from?

From **configured application / intent profile** — resolved from policy and intent defaults, not inferred from raw transaction data at runtime.

## Who configures Policy?

**Configured demo policy** in the prototype (YAML). Evaluated at runtime. Not a universal legal conclusion.

## How is Consent handled?

**Configured demo consent rules** — e.g. location may be required but unavailable, producing `BLOCKED_BY_POLICY`. Not a real consent platform.

## What does DPA mean here?

**Configured agreement** referencing permitted purposes and data residency for the demo enterprise. Not legal advice.

## What is Autonomy?

The envelope of what the agent may do: OBSERVE, RECOMMEND, ACT_WITH_APPROVAL, ACT, NOT_AUTHORIZED. Example: Rocket Bank may recommend STEP_UP but not decline payment.

## Is the agent another Application?

No. The **agent** is an authorized principal acting on behalf of an **application**. Identity/delegation is **simulated** in the prototype.

## Does this need an LLM?

No. The prototype is deterministic scenario execution. LLM/MCP are intentionally unresolved.

## Does this use MCP?

Not in this prototype.

## Who hosts this?

**Unresolved / topology-neutral.** Routes show DIRECT, AGGREGATED, HYBRID without claiming commercial hosting.

## Direct operators or aggregators?

Both appear as generic **Network Provider A/B** and **Aggregator A**. Route type is inspectable; hosting model is not locked.

## Why Telco Finder?

When the subject is a phone number, NetAware must resolve which network holds the subscription before API discovery.

## Why API Finder?

Maps required capabilities to available operations on the selected network/provider.

## Why are some CAMARA APIs experimental?

**CAMARA maturity** is metadata. **Business status** (CURRENT_FOCUS) is separate. Experimental specs can still be current-focus for the demo catalog.

## Does NetAware make the final fraud/business decision?

**No.** Rocket Bank owns the financial decision. High Flight owns operational approval. CityCare pharmacist owns dispensing. NetAware returns assessments and recommendations within autonomy.

## What is simulated?

Operator responses, domain/enterprise APIs, identity/delegation, consent availability, and provider coverage.

## What is production-ready vs prototype?

**Frozen product behavior** is demo-ready. Production auth, live operators, legal automation, durable evidence store, and hosting are **not** claimed.

## How does evidence reuse work?

After `assess_network_trust`, normalized evidence is stored. `assess_recovery_continuity` checks tenant, subject, purpose compatibility, TTL, and policy. Matching evidence → `EVIDENCE_REUSED`, API skipped, source execution linked.

## What prevents unnecessary API calls?

Mapping ≠ invocation. Policy blocks, NOT_REQUIRED decisions, minimum capability selection (CityCare), and evidence reuse reduce API economy.

## How does this increase Network API adoption?

**Small practical catalog (13 families)** → many domains/use cases/intents. Explorer shows forward and reverse leverage. Demos prove business outcomes, not API counts.
