# AX Cadence 11 — Device fleet / OTA readiness

**Status:** Complete  
**UI cadence:** 11  
**Model cadence:** 7  
**Live demo baseline:** `0.6.1-ax6.1` (unchanged)  
**Product behavior:** Rocket Bank STEP_UP, recovery CONTINUITY_ALIGNED, Acme inspection ASSURED, CityCare ELIGIBLE, NV path selection, High Flight CONTINUE / SWAP_DEVICE unchanged.

**STOP. Do not start Cadence 12.** No generic interpreter, Demand Map, Fulfillment Coverage UI, catalog expansion, or MCP/A2A.

---

## 1. OTA business story

Acme Manufacturing · Connected Device Operations · critical firmware 8.4 campaign. The enterprise OTA platform already knows the target firmware, compatible models, and which devices require the update. NetAware answers: which of those devices are network-suitable to update **now**?

## 2. Existing enterprise systems

Device Management / OTA Platform, inventory, device twin, firmware campaign, compatibility, device health. Simulated enterprise operations: `listDevices`, `getTwin`, `getPackage`, `addDevicesToCampaign`. Not CAMARA.

## 3. Network Decision Gap

The OTA platform does not independently have current operator-network knowledge for every cellular device needed to decide cohort membership for this rollout window.

Network adds: Device Reachability; Roaming Status where material, interpreted by configured enterprise policy.

## 4. Intent Profile

`prepare_ota_cohort` · ADVANCED_AGENTIC · networkContributionTier **A** · purpose `firmware_rollout` (`dpv:ImproveExistingProductsAndServices`). Working alias `rollout_firmware_safely` is documentation only.

## 5. Fleet size

**SIMULATED FLEET** 10,000 campaign devices. 8,400 enterprise firmware/model eligible. 1,600 not eligible (enterprise-owned; no network).

## 6. Fleet funnel

10,000 campaign → 8,400 enterprise eligible → 7,100 network evaluation required (1,300 fresh evidence reused) → 5,900 ROLL OUT NOW / 2,500 DEFER.

## 7. Provider distribution

Telco Finder on the campaign: Provider A Canada 5,000 · Provider B Germany 3,300 · Provider C Singapore 1,700. Eligible: A 4,200 · B 2,800 · C 1,400.

## 8. Telco Finder behavior

Groups the simulated fleet by serving network. Does not evaluate Reachability or Roaming. Visually separate from API Finder.

## 9. API Finder behavior

Provider A DIRECT: Reachability yes, Roaming yes. Provider B via Aggregator A: Reachability yes, Roaming yes. Provider C DIRECT: Reachability yes, Roaming unavailable.

## 10. Network APIs selected

`getReachabilityStatus` (primary). `getRoamingStatus` where advertised. Representative samples only; aggregate volume is labelled SIMULATED DEMO VOLUME.

## 11. APIs considered / not required

QoD, Location, Number Verification, SIM Swap, Device Swap: not required and not invoked. Connectivity Insights remains experimental / not invoked; not silently added to the required set. Catalog stays 13 families.

## 12. Policy behavior

CONFIGURED POLICY. DATA reachable → eligible. Not DATA reachable → DEFER / RETRY. Network supplies roaming state; enterprise policy defers roaming on this campaign. Roaming is not automatically bad.

## 13. Initial cohort

5,900 ROLL OUT NOW.

## 14. Deferred reasons

1,200 unreachable (API successfully reported not DATA reachable — fulfilled demand). 800 roaming under configured policy. 500 Provider C Roaming Status gap (unfulfilled qualified demand).

## 15. Reassessment behavior

Same Intent, later observation. 400 previously unreachable + 200 previously roaming become ready → 6,500 ROLL OUT NOW / 1,900 still deferred.

## 16. Enterprise OTA action

`addDevicesToCampaign` — SIMULATED ENTERPRISE API. Not a CAMARA operationId. Submits the network-qualified cohort.

## 17. Autonomy

Read campaign / gather readiness / segment / recommend: ACT. Submit cohort: ACT_WITH_APPROVAL. Install firmware: NOT_AUTHORIZED / outside NetAware.

## 18. Provider / routes

HYBRID: one enterprise Intent → Provider A DIRECT, Provider B AGGREGATED via Aggregator A, Provider C DIRECT → one normalized cohort outcome.

## 19. Simulated API volume

Prepare: 7,100 live Reachability + 4,900 live Roaming + 1,300 reused. Reassess: +400 Reachability + 600 Roaming. Labelled SIMULATED DEMO VOLUME. No revenue.

## 20. Business View

Acme Connected Device Operations funnel, cohort tiles (ROLL OUT NOW / DEFER unreachable / DEFER roaming policy / UNFULFILLED API gap), movement on reassess, three-sentence close, firmware disclaimer.

## 21. Technical View

Existing AX machinery plus fleet subject resolution, Telco Finder groups, API Finder per route, Reachability / Roaming, policy interpretation, autonomy, simulated enterprise OTA action. Drill-down, not giant tables by default.

## 22. Explorer linkage

Manufacturing / IoT → Fleet Firmware Rollout → `prepare_ota_cohort` → Device Reachability / Roaming Status. Quality Inspection remains the other Acme live demo. Demand Map / Fulfillment Coverage UI not built.

## 23. Regression tests

`python backend/scripts/validate_ax_cadence11.py` nests Cadence 10 (which nests 0–9). Existing Acme ASSURED, NV, High Flight, Rocket Bank, CityCare unchanged.

## 24. Known realism gaps

- Fleet counts, operator responses, and API volume are simulated  
- Provider C roaming gap is configured, not a live operator readiness claim  
- Evidence reuse is a secondary demonstration, not production TTL math  
- `rollout_firmware_safely` remains a documentation alias  
- Generic interpreter / BASIC field engine remains Cadence 12  
