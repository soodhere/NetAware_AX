# AX Demo Script

Presentation paths for NetAware AX Cadence 6. Fictional enterprises only.

## 90-second cut — High Flight alone

1. **Home** — “Keep your application. Express the outcome.”
2. **Start Demo** → **High Flight Airlines** → **Baggage handling / ramp device operability**
3. **Briefing** — BRS / DCS / Ground Operations stay. Decision Gap is scanner operability, not bag tracking.
4. **Run** — presenter may simulate READY vs NOT REACHABLE. Skip to end if pacing tight.
5. **Overview** — Bag HF123456 is domain context. Scanner HF-HDL-0192 is the network subject. CONTINUE or SWAP_DEVICE.
6. **Stop** — “Network does not move bags. It tells the airline whether the assigned handheld can complete the connected custody scan.”

## 5-minute standard flow

1. **Home** (15s) — DX → AX equation.
2. **High Flight** — full run, Overview + Decisions (2 min).
3. **Rocket Bank** — quick compare: selective evidence, STEP_UP, enterprise owns decision (1 min).
4. **Acme** — observe → breach → QoD → verify ASSURED (45s).
5. **Explore → API Catalog** — 13 families, many domains (45s).
6. **Close** — coexistence of Direct API / Composed API / Intent (30s).

CityCare if time: minimum capability, KYC blocked, ELIGIBLE.

## 10–15 minute technical expansion

After 5-minute flow:

- **Rocket Bank** — Policy trace (location consent), Decisions (NOT_REQUIRED recycling).
- **High Flight** — BRS/DCS chain, scanner as network subject, CONTINUE vs SWAP_DEVICE.
- **Acme** — conditionChange, verification getSession.
- **CityCare** — minimum capability selection, dataUsed AGE_ASSERTION_ONLY.
- **Explorer** — reverse from `checkSimSwap`, `createSession`, `verifyLocation`, `verifyAge`. If asked about Incubating: it is CAMARA **project lifecycle**, not API-version maturity. SIM Swap 2.1.0 is a stable public API.
- **Providers / Routes** — DIRECT vs AGGREGATED vs HYBRID.
- **Evidence reuse** (secondary) — Rocket Bank recovery after trust; EVIDENCE_REUSED, zero invocations.

## Intent definition (say consistently)

> Intent is the outcome the application or agent wants — without specifying which Network APIs should be called.

## AX loop vocabulary

Understand → Govern → Discover → Plan → Execute → Observe → Replan → Verify

## Do not claim

- Production readiness
- Real operator coverage
- Hosting or commercial model
- LLM / MCP requirement
