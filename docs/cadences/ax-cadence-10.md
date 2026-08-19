# AX Cadence 10 — Decision Gap + High Flight baggage evolution

**Status:** Complete  
**UI cadence:** 10  
**Model cadence:** 7 (Intent Profiles added as configuration; discovery enums unchanged)  
**Live demo baseline:** `0.6.1-ax6.1` (unchanged)  
**Product behavior:** Rocket Bank STEP_UP, recovery CONTINUITY_ALIGNED, Acme ASSURED, CityCare ELIGIBLE, NV path selection unchanged. High Flight featured story evolved.

**STOP. Do not start Cadence 11.** No OTA, fleet visualization, Demand Map, Fulfillment Coverage Explorer, field/delivery live scenario, MCP, A2A, SalesScenarioProfile loader, Meeting Mode, or catalog expansion.

---

## 1. Universal Decision Gap model

Every live Intent now has an onboarded `decisionGap` on its Intent Profile, attached to the execution trace:

You already have → You need to decide → Network Decision Gap → Network adds → NetAware AX → Outcome.

Business View renders this as a causal strip, not six equal text cards.

## 2. Decision Gap for every live scenario

| Intent | Already have | Decide | Network adds | Outcome |
| --- | --- | --- | --- | --- |
| `verify_mobile_number` | CIAM / IAM / claimed number | Silent verify? | Number Verification | VERIFIED / CAPABILITY_UNAVAILABLE |
| `assess_network_trust` | Payments / fraud | Proceed or step up? | Possession + SIM/device/roaming | STEP_UP |
| `assess_recovery_continuity` | IAM recovery | Normal recovery? | Continuity, including reuse | CONTINUITY_ALIGNED |
| `maintain_inspection_experience` | MES / QMS / SLO | Can network restore the objective? | Observe + QoD when useful | ASSURED |
| `verify_pharmacy_age_gate` | Pharmacy + age threshold | Minimum age met? | Age assertion (KYC filtered) | ELIGIBLE |
| `ensure_baggage_connection` | BRS / DCS / assignment | Can assigned scanner complete the custody scan? | DATA reachability | CONTINUE / SWAP_DEVICE |

## 3. IntentProfile schema

`data/schemas/intent-profile.json` — configured/onboarded knowledge. Not a runtime request body. Not a second planner.

## 4. Live Intent profiles

`data/model/intent-profiles.yaml` covers all six executable Intents. HTTP `/intents` body remains `{intent, subject, context}`.

## 5. Scenario complexity model

`BASIC | COMPOSED | ADVANCED_AGENTIC` on the profile (`scenarioComplexity` on the trace).

UI lens remains Basic / Advanced. Trace documents:

- BASIC lens = Business View  
- ADVANCED lens = Technical View  

These are different dimensions.

## 6. NV presenter-context clarification

Variant control is labelled **Simulate runtime context**:

- Cellular / Provider A  
- Wi-Fi / Provider A  
- Wi-Fi / Provider B  

Strip: Application chooses Intent → NetAware resolves context → NetAware chooses NV1/NV2 path.

Engine semantics unchanged (NV1 / NV2 / ECS gap).

## 7. High Flight evolved business story

Featured live story is **baggage handling / ramp device operability**. Bag HF123456 and load-close stay on screen. `EXPEDITE_TRANSFER` is no longer the network-driven outcome. Executable id remains `ensure_baggage_connection` (alias `assure_ramp_scan_capability` is documentation only).

## 8. BRS / DCS / Ground Operations model

Domain/enterprise APIs:

- `getBaggageJourney` — BRS custody/load event  
- `getFlightStatus` — DCS HF281 / load-close  
- `getRampAssignment` — worker + scanner HF-HDL-0192  

## 9. Scanner network-subject mapping

Bag / worker → assigned scanner HF-HDL-0192 → network identifier. Telco Finder uses the scanner, not the suitcase.

## 10. High Flight deterministic states

One runner (`backend/app/hf_runtime.py`), presenter control **Simulate operational context**:

| State | Reachability API | Outcome |
| --- | --- | --- |
| Assigned scanner reachable | success, reachable | CONTINUE |
| Assigned scanner not reachable | success, unreachable | SWAP_DEVICE |

## 11. High Flight Network contribution

Device DATA reachability. Location and QoD are NOT_REQUIRED by default. Connectivity skipped unless it would change CONTINUE vs SWAP (it does not in these seeds). Network Location is not used as bag tracking.

## 12. High Flight outcomes

Featured: CONTINUE · SWAP_DEVICE. Alternate scanner `HF-HDL-0208` is assigned via **enterprise handheld inventory** (`assignAlternateScanner`), not a Network API. Flight-plan change remains NOT_AUTHORIZED. Network does not move bags.

## 13. Unfulfilled-demand distinction

Unreachable READY-fail is **API successfully reported unreachable**. `demandFulfilled: true`, `apiSuccessfullyReportedUnreachable: true`. That is not unfulfilled qualified demand.

## 14. Governance provenance labels

Existing policy evaluations emit `layer` (AGENT DELEGATION, INTENT, PURPOSE / DATA, COMMERCIAL, AUTONOMY, RUNTIME). No new policy engine.

Technical View shows Relevant / Available / Entitled / Permitted / Needed → CALL / REUSE / SKIP / FILTER / UNAVAILABLE from the Cadence 8 discovery array.

## 15. Shared interpreter spike

`backend/app/interpreter_spike.py` reads CityCare Intent Profile (Age CALL, KYC FILTER). Not wired into `execute_intent`. Live runner still produces ELIGIBLE.

## 16. Visual changes

- Decision Gap strip on every live run (Overview + Discovery)  
- NV who-chooses strip + simulation labels  
- High Flight baggage-world chain (Bag → BRS → DCS → Ramp → Scanner)  
- Two-state High Flight selector  

## 17. Regression tests

`python backend/scripts/validate_ax_cadence10.py` nests Cadence 9 (which nests 0–8).

## 18. Known gaps

- Intent id `ensure_baggage_connection` kept for compatibility; working alias is not executable  
- DPV for ramp ops remains NEEDS_REVIEW (`dpv:FulfilmentOfContractualObligation`)  
- Historical AT_RISK / EXPEDITE graph examples may still appear in Explorer as catalog history  
- Business / Technical rename of the lens control is deferred to the sales-freeze cadence  
- Interpreter spike is CityCare-only and not a generic BASIC engine yet  
