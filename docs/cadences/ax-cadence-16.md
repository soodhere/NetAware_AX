# Cadence 16 — Sales meeting mode + final demo freeze

Status: complete. Cadence 17 not started. No Cadence 17 plan.

This cadence does not add a product model. It makes NetAware AX presentable by a salesperson who did not build it.

Live version remains `0.6.1-ax6.1`. Model cadence remains 7. UI cadence is **16**. Runtime, discovery, policy, fulfillment, demand, catalog, and the 17-use-case portfolio are unchanged.

## 1. Meeting Mode implementation

Guided navigation overlay `#/meet/{enterprise|operator|aggregator}/{exec|sales|tech}`. Same product surfaces. Not a second runtime. No countdown timers.

## 2. 3-minute Executive paths

Five beats: customer problem, network decision gap, what NetAware does, outcome, why it matters. No operationIds, OAuth, DPV, or JSON by default. Close: NetAware connects enterprise demand to network supply.

## 3. 7-minute Sales paths

Adds discovery, governance, operator/aggregator supply, select/invoke/reuse/skip, commercial implication without protocol overload.

## 4. Technical Deep Dive

Progressive drill-down into existing machinery. Same trace. Lens switch does not rerun.

## 5. Enterprise recommended story

Rocket Bank passwordless mobile sign-in. Verify this mobile number. Cellular NV1, Wi-Fi NV2, Wi-Fi + ECS gap blocked.

## 6. Operator recommended story

Number Verification enablement. API available ≠ Intent fulfillable. Provider A vs Provider B ECS. Optional OTA 500-device qualified-demand gap.

## 7. Aggregator recommended story

Multi-region fulfillment. CA / DE / SG. Routed through / normalized through / available via. Does not own operator APIs.

## 8. Sales scenario recommender

Deterministic “What should I show?” selector. No AI. No salesperson profiles.

## 9–14. Story presentation

THIS PROVES cues on briefings. High Flight stays simple (no QoD/location in the default story). Acme inspection is the AX proof. CityCare is governance minimization. Evidence reuse stays secondary.

## 15–17. Discovery, fulfillment, Demand Map

Meeting technical path makes discovery the hero visual. C13 and C14 remain sources of truth.

## 18. Demand ↔ supply close

Left demand, center AX, right supply, business outcomes. Final screen for all three stakeholder paths (`#/close`).

## 19–20. DX → AX and why this is AX

Retained. AX builds on DX. Deterministic proofs only. No LLM theater.

## 21–22. Presenter cues and FAQ

Optional, hidden by default. Objection shortcuts match the sales FAQ.

## 23–25. Preflight, Reset Demo, deep links

`GET /preflight` → DEMO READY. Footer Reset Demo restores presentation state and evidence store, not product YAML. Hash routes survive refresh.

## 26–27. Basic Auth and deployment

Unchanged Cadence 15 HTTP Basic. Single-service host. `/health` unauthenticated.

## 28. Presenter documents

`docs/AX-SALES-DEMO-SCRIPT.md`, `docs/AX-SALES-RUNBOOK.md`, `docs/AX-SALES-FAQ.md`.

## 29. Regression

`backend/scripts/validate_ax_cadence16.py` nests Cadence 0–15. Live heroes, NV/ECS, High Flight, OTA, CityCare, evidence reuse unchanged.

## 30. Remaining presentation issues

- Explorer and catalog remain dense; use them only in technical depth.
- Portfolio still shows 17 cards; Meeting Mode is the short path so salespeople are not forced to choose among all of them first.
- Hosted frontend bundle refreshes on deploy; local `frontend/dist` may lag source until rebuild.

**PRODUCT FUNCTIONALITY: FROZEN**

**SALES PRESENTATION: FROZEN**

**NEXT STEP: EXTERNAL SALES / CTO / CUSTOMER FEEDBACK**

**CADENCE 17: NOT STARTED**
