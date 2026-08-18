# AX Cadence 0.1 — Curated practical catalog

**Status:** Implemented, then **superseded on inclusion criterion** by Cadence 0.2.  
**Cadence:** 0 / patch **0.1**  
**Execution engine:** not implemented  
**Demo UI:** not implemented  

Cadence 0.1 treated “practical today” as **non-experimental CAMARA only**. That was the wrong test. Cadence 0.2 keeps this report as history and restores CURRENT_FOCUS APIs with honest `specMaturity`. See [`ax-cadence-0.2.md`](ax-cadence-0.2.md). 

Product story:

> A relatively small set of practical Network APIs can support many business intents across many industries when NetAware provides the Agentic Experience layer.

Not: “NetAware has hundreds of APIs.”

---

## ACTIVE AX API CATALOG: **13 APIs** · **27 operations**

All sources are non-experimental CAMARA specs. NV1 / NV2 are two operations on **one** API.

| # | API name | Version | operationId(s) | Capabilities |
|---|----------|---------|----------------|--------------|
| 1 | Number Verification | 2.1.0 | `phoneNumberVerify` (NV1), `phoneNumberShare` (NV2) | number_possession_verification |
| 2 | SIM Swap | 2.1.0 | `checkSimSwap`, `retrieveSimSwapDate` | sim_continuity |
| 3 | Device Swap | 1.0.0 | `checkDeviceSwap`, `retrieveDeviceSwapDate` | device_continuity |
| 4 | Know Your Customer Match | 0.4.0 | `KYC_Match` | kyc_match |
| 5 | Device Location Verification | 3.0.0 | `verifyLocation` | location_verification |
| 6 | Device Location Retrieval | 0.5.0 | `retrieveLocation` | location_retrieval |
| 7 | Device Geofencing Subscriptions | 0.5.0 | `createGeofencingSubscription` (+ list/get/delete in registry) | geofencing |
| 8 | Device Reachability Status | 1.1.0 | `getReachabilityStatus` | device_reachability |
| 9 | Device Roaming Status | 1.1.0 | `getRoamingStatus` | roaming_status |
| 10 | Quality-On-Demand | 1.1.0 | `createSession`, `getSession`, `deleteSession`, `extendQosSessionDuration`, `retrieveSessionsByDevice` | quality_on_demand |
| 11 | QoS Profiles | 1.1.0 | `retrieveQoSProfiles`, `getQosProfile` | quality_on_demand |
| 12 | QoS Provisioning | 0.3.0 | `createQosAssignment`, `getQosAssignmentById`, `revokeQosAssignment`, `getQosAssignmentByDevice` | quality_on_demand |
| 13 | Simple Edge Discovery | 2.0.1 | `readClosestEdgeCloudZone` | edge_discovery |

Definition: `data/catalog/ax-active-catalog.yaml`  
Parser: `backend/app/registry.py` loads **only** these files/operationIds.

Full CAMARA pin remains under `openapi/` for reference. It is **not** in `/catalog`, not in mappings, not a planner candidate.

---

## Multiplication (Explorer configuration, not execution)

| Layer | Count |
|-------|------:|
| Active APIs | **13** |
| Active operations | **27** |
| Supported capabilities | **11** |
| Mapped intents | **19** |
| Mapped use cases | **19** |
| Mapped domains | **11** |

Evidence rows: SOURCE_BACKED **23** · INFERRED **39** · NEEDS_REVIEW **1**

Reverse examples (live):

- `checkSimSwap` / SIM continuity → transaction trust, recovery, checkout trust, claim trust → Financial / Retail / Insurance  
- `createSession` / QoD → inspection, telehealth, broadcast, warehouse scan, stadium, turnaround, site uplink, baggage (considered) → **8 domains**  
- `verifyLocation` → baggage, fraud, equipment, shipment, claim, visit, airside → **7 domains**

`GET /catalog/apis` returns API → capabilities → intents → use cases → domains for every active API.

---

## Deep-demo revalidation (configuration only)

### Rocket Bank — `assess_network_trust`
Still supported with NV, SIM Swap, Device Swap, Roaming, Location (considered).  
**Gaps vs Cadence 0:** Device Identifier, Number Recycling, Tenure (experimental — not filled).

### High Flight Airlines — `ensure_baggage_connection`
Still supported with Location Verification, Reachability, QoD (considered).  
**Gaps vs Cadence 0:** Connectivity Insights (experimental). Domain/enterprise APIs unchanged.

### Acme Manufacturing — `maintain_inspection_experience`
Still supported with QoD, QoS Profiles/Provisioning, Edge Discovery, Reachability (observe substitute).  
**Gaps vs Cadence 0:** Application Profiles, Connectivity Insights (experimental — not filled).

---

## Capability gaps (not filled with experimental APIs)

| Wanted capability | Why absent from AX_ACTIVE_CATALOG |
|-------------------|-----------------------------------|
| Device Identifier | Experimental spec in this pin |
| Number Recycling | Experimental |
| KYC Tenure | Experimental |
| Connectivity Insights | Experimental |
| Application Profiles | Experimental |
| Age Verification | Preferred split repo is experimental; superseded `KnowYourCustomer__` pack not used |

---

## NEEDS_REVIEW

- **`phoneNumberShare` (NV2)** as the Wi-Fi-suitable Number Verification path. Real `operationId` on Number Verification 2.1.0; access-type claim is not SOURCE_BACKED.

Explorer intent→capability rows for non-hero domains are **INFERRED** (same APIs, new businesses).

---

## APIs intentionally excluded

- Entire experimental/WIP pin (Device Identifier, Insights, Age Verification split, IoT, slices, WebRTC, …)  
- Superseded DeviceStatus__ and KnowYourCustomer__ parent packs  
- Other camara specs outside current practical scope (Population Density, OTP SMS, Call Forwarding, …)

---

## Validation

`python backend/scripts/validate_ax_cadence0.py`

**Cadence 0 PASSED (31 checks)** including active-catalog size, no experimental registry/mappings, Rocket Bank / High Flight / Acme remap, reverse multi-domain QoD/Location, 404 on `retrieveIdentifier`.

---

**STOP.** Do not start Cadence 1 until explicitly approved.
