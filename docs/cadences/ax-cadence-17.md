# Cadence 17 — Visual intelligence

Status: complete. No further cadence started.

Cadence 17 does not add a product model, scenario, API family, or mapping database. It visualizes the decision already present in Cadences 8–16.

Live version remains `0.6.1-ax6.1`. Model cadence remains 7. UI cadence is **17**.

## 1. Use Case ↔ API Map

First-class surface `#/map`. Derived from the 17-row C12 portfolio, `mappings.yaml` intent↔capability links, and the 13-family catalog. GET `/map`. Presentation only.

## 2. Matrix

17 use cases × 13 families. States used only when the model supports them: REQUIRED, CONDITIONAL, FILTERED. Empty = NOT RELEVANT. Click a cell for why. FILTERED uses existing live governance behavior (e.g. CityCare KYC, Rocket Bank location), not invented mappings.

## 3. Reverse API traversal

API family or capability → intents → applications → use cases → enterprises → industries. Wording: configured demo use cases / configured demand. Not customers.

## 4. Application → Intent → Capability

Enterprise graph: one enterprise, multiple applications, reusable capabilities (Rocket Bank identity stack; Acme inspection + OTA).

## 5–8. Discovery, governance, NV, finders

Discovery funnel narrows candidates using existing discovery events. Technical governance waterfall highlights the failing layer from provenance. NV decision tree remains Intent-stationary. Telco Finder, API Finder, and Fulfillment stay three distinct stages.

## 9–12. Topology, heatmap, supply-gap, Demand Map

Topology uses C13 DIRECT / AGGREGATED records for CA / DE / SG. Heatmap is Intent × provider from the same records. Supply-gap reverse traversal uses C14 enablement (ECS, Provider C roaming). Demand flow: industry → … → fulfilled/gap.

## 13–17. Story visuals

High Flight: bag → BRS → DCS → ramp → scanner → reachability → CONTINUE / SWAP DEVICE, with the enterprise-inventory boundary. Acme inspection is a loop; 201 is not success. OTA funnel unchanged (simulated fleet). CityCare two-path minimization. Evidence reuse graph: 0 new network invocations.

## 18–22. DX→AX, agentic loop, configured vs runtime, provenance, close

Split-screen DX vs AX. Agentic loop with existing proof points. Configured knowledge vs runtime discovery. Provenance badges in Technical View. Demand ↔ supply close strengthened.

## 23–24. Meeting Mode and Explorer

C16 Meeting Mode kept. Technical paths link to the map. Explorer overview adds visual entry points into the same graph.

## 25–26. Performance and regression

No new graph libraries. CSS/SVG-free components. `validate_ax_cadence17.py` nests 0–16.

## 27. Remaining visual issues

Explorer catalog tables remain dense. The 17×13 matrix uses compact labels (REQ/COND/FILT). Presentation polish adds selected-use-case / selected-API filters, row/column highlight, sticky labels, and Projector focus. Hosted `frontend/dist` refreshes on deploy.

**PRODUCT MODEL: UNCHANGED**

**RUNTIME BEHAVIOR: UNCHANGED**

**USE CASE PORTFOLIO: 17 — UNCHANGED**

**API CATALOG: 13 FAMILIES — UNCHANGED**

**CADENCE 17: VISUAL INTELLIGENCE COMPLETE**
