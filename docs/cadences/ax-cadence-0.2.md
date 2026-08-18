# AX Cadence 0.2 — Business-practical catalog correction

**Status:** Implemented and validated.  
**Cadence:** 0 / patch **0.2**  
**Execution engine:** not implemented  
**Demo UI:** not implemented  

Product story:

> A relatively small set of **current-focus** Network API / capability families can support many business intents across many industries when NetAware provides the Agentic Experience layer.

Cadence 0.1 made the active catalog technically clean, but used the **wrong criterion** for “practical today.” It treated practical as “only APIs whose CAMARA repository is non-experimental.” That is not the NetAware product test.

**PRACTICAL TODAY** = current NetAware / operator / aggregator / application **business focus**.

CAMARA specification maturity is **metadata**. It does **not** by itself decide catalog membership.

Three concepts remain separate:

1. **Business active catalog** — ~13 capability families relevant today (`businessStatus: CURRENT_FOCUS`)
2. **Technical operations** — real OpenAPI files and real `operationId`s
3. **Spec maturity** — incubating / experimental / etc.

Do not portray experimental maturity as production standardization.

Example the Explorer must be able to show:

> Device Identifier  
> Business status: CURRENT FOCUS  
> CAMARA maturity: EXPERIMENTAL

---

## Correction vs Cadence 0.1

| Cadence 0.1 (wrong test) | Cadence 0.2 (correct test) |
|--------------------------|----------------------------|
| Include iff CAMARA source is non-experimental | Include iff CURRENT_FOCUS for NetAware / customers today |
| Device Identifier, Recycling, Age, Insights removed | Restored, labelled experimental |
| 13 YAML files counted as “13 APIs” | 13 **business families**; 18 technical specs; 37 operations |
| QoD + QoS Profiles + QoS Provisioning counted as 3 product APIs | One family: **Quality on Demand** |
| NV1 and NV2 as two catalog rows on one API (correct) | Same: one **Number Verification** family; NV1/NV2 are operations |

The experimental **pin** is not back. Unrelated experimental APIs (IoT, slices, WebRTC, sponsored data, Tenure, …) stay out.

---

## BUSINESS ACTIVE CATALOG: **13 families**

Definition: `data/catalog/ax-active-catalog.yaml`  
Parser: `backend/app/registry.py` loads families → technicalSpecs → declared `operationId`s only.

All families: `businessStatus: CURRENT_FOCUS`.

### Identity / trust

| # | Business family | specMaturity | Source | operationIds | Capabilities |
|---|-----------------|--------------|--------|--------------|--------------|
| 1 | **Number Verification** | incubating | `openapi/camara/NumberVerification__number-verification.yaml` | `phoneNumberVerify` (NV1), `phoneNumberShare` (NV2, **NEEDS_REVIEW**) | number_possession_verification |
| 2 | **SIM Swap** | incubating | `openapi/camara/SimSwap__sim-swap.yaml` | `checkSimSwap`, `retrieveSimSwapDate` | sim_continuity |
| 3 | **Device Swap** | incubating | `openapi/camara/DeviceSwap__device-swap.yaml` | `checkDeviceSwap`, `retrieveDeviceSwapDate` | device_continuity |
| 4 | **Device Identifier** | **experimental** | `openapi/experimental/DeviceIdentifier__device-identifier.yaml` | `retrieveIdentifier`, `retrieveType`, `retrievePPID` | device_identifier |
| 5 | **Number Recycling** | **experimental** | `openapi/experimental/NumberRecycling__number-recycling.yaml` | `checkNumberRecycling` | number_recycling |
| 6 | **KYC Match** | incubating | `openapi/camara/KnowYourCustomerMatch__kyc-match.yaml` | `KYC_Match` | kyc_match |
| 7 | **Age Verification** | **experimental** | `openapi/experimental/KnowYourCustomerAgeVerification__kyc-age-verification.yaml` 0.2.1 | `verifyAge` | age_verification |

NV1 / NV2 are **not** two product families. They are two operations on the same CAMARA Number Verification API. NV1 is typically mobile-network possession (`phoneNumberVerify`). NV2 is the candidate Wi-Fi / share path (`phoneNumberShare`); access-type mapping is **NEEDS_REVIEW**.

### Location / context

| # | Business family | specMaturity | Source | operationIds | Capabilities |
|---|-----------------|--------------|--------|--------------|--------------|
| 8 | **Location Verification / Retrieval** | incubating | `DeviceLocation__location-verification.yaml`, `…location-retrieval.yaml`, `…geofencing-subscriptions.yaml` | `verifyLocation`, `retrieveLocation`, `createGeofencingSubscription` (+ list/get/delete in registry) | location_verification, location_retrieval, geofencing |
| 9 | **Device Reachability / Status** | incubating | `openapi/camara/DeviceReachabilityStatus__device-reachability-status.yaml` | `getReachabilityStatus` | device_reachability |
| 10 | **Roaming Status** | incubating | `openapi/camara/DeviceRoamingStatus__device-roaming-status.yaml` | `getRoamingStatus` | roaming_status |

Geofencing is a **technical** spec under Location, not a 14th business family.

### Experience / control

| # | Business family | specMaturity | Source | operationIds | Capabilities |
|---|-----------------|--------------|--------|--------------|--------------|
| 11 | **Quality on Demand** | incubating | QoD + QoS Profiles + QoS Provisioning YAMLs | `createSession`, `getSession`, `deleteSession`, `extendQosSessionDuration`, `retrieveSessionsByDevice`, `retrieveQoSProfiles`, `getQosProfile`, `createQosAssignment`, `getQosAssignmentById`, `revokeQosAssignment`, `getQosAssignmentByDevice` | quality_on_demand |
| 12 | **Connectivity / QoD Insights** | **experimental** | `ConnectivityInsights__connectivity-insights.yaml`, `ApplicationProfiles__application-profiles.yaml` | `checkNetworkQuality`, `createApplicationProfile`, `readApplicationProfile`, `updateApplicationProfile`, `deleteApplicationProfile` | connectivity_insights, application_profiles |
| 13 | **Edge Discovery** | incubating | `openapi/camara/SimpleEdgeDiscovery__simple-edge-discovery.yaml` | `readClosestEdgeCloudZone` | edge_discovery |

Application Profiles is grouped under Connectivity / QoD Insights, not a 14th family.

---

## Technical vs business counts

| Concept | Count |
|---------|------:|
| Business families (Explorer “13–14”) | **13** |
| Technical OpenAPI specs in the active catalog | **18** |
| Declared operations in registry | **37** |
| Unique operationIds | **37** |
| Experimental-source operations (labelled) | **10** |

`GET /health` reports `catalog.businessFamilies`, not YAML-file count.

Full CAMARA pin remains under `openapi/` for reference. It is **not** Explorer/runtime input except via `AX_ACTIVE_CATALOG`.

---

## Multiplication (Explorer configuration, not execution)

| Layer | Count |
|-------|------:|
| Business families | **13** |
| Technical specs | **18** |
| Active operations | **37** |
| Supported capabilities | **16** |
| Mapped intents | **21** |
| Mapped use cases | **21** |
| Mapped domains | **11** |

Evidence rows: SOURCE_BACKED **32** · INFERRED **42** · NEEDS_REVIEW **1** (`phoneNumberShare` / NV2)

Reverse examples (live):

- `checkSimSwap` / SIM continuity → transaction trust, recovery, checkout trust, claim trust → Financial / Retail / Insurance
- `createSession` / QoD → inspection, telehealth, broadcast, warehouse scan, stadium, turnaround, site uplink, baggage (considered) → **8 domains**
- `verifyLocation` → baggage, fraud, equipment, shipment, claim, visit, airside → **7 domains**
- `retrieveIdentifier` → Rocket Bank network trust (CURRENT_FOCUS, experimental maturity)
- `checkNetworkQuality` → High Flight baggage (considered) and Acme inspection (required)

`GET /catalog/apis` returns family → `businessStatus` / `specMaturity` → capabilities → intents → use cases → domains.

---

## Gaps restored from Cadence 0.1

| Cadence 0.1 gap | Cadence 0.2 |
|-----------------|-------------|
| Device Identifier | **Restored.** CURRENT_FOCUS. specMaturity **experimental**. |
| Number Recycling | **Restored.** CURRENT_FOCUS. specMaturity **experimental**. |
| Age Verification | **Restored.** Preferred split repo 0.2.1. specMaturity **experimental**. Superseded parent pack not used. |
| Connectivity Insights | **Restored.** CURRENT_FOCUS. specMaturity **experimental**. |
| Application Profiles | **Restored as technical spec** under Connectivity / QoD Insights, not a 14th family. |

Still not in the business catalog (intentional):

- **KYC Tenure** — not in the current 13-family focus list
- Remaining experimental pin (IoT, slices, WebRTC, sponsored data, WIP, …)
- Superseded `DeviceStatus__` / `KnowYourCustomer__` parent packs
- Other incubating CAMARA specs outside current focus (Population Density, OTP SMS, Call Forwarding, …)

---

## Deep-demo revalidation (configuration only)

### Rocket Bank — `assess_network_trust`

Forward: financial → high-value-payment-protection → **10 operations**.

Supported: Number Verification, Number Recycling, SIM Swap, Device Swap, **Device Identifier (restored)**, Roaming, Location (considered).

Tenure remains a gap (not in the 13-family list). Location consent is stored as required/unavailable for later policy evaluation.

### High Flight Airlines — `ensure_baggage_connection`

Forward: airlines → baggage-connection → **7 operations**.

Supported: Location Verification (considered; consent later), Reachability (required), **Connectivity Insights restored (considered)**, QoD (considered). Domain/enterprise APIs (Baggage Journey, Flight Status) unchanged.

### Acme Manufacturing — `maintain_inspection_experience`

Forward: manufacturing → critical-inspection-camera → **8 operations**.

Supported: **Application Profiles + Connectivity Insights restored**, QoD, Edge Discovery, Reachability (considered). Insights/Profiles are CURRENT_FOCUS with **experimental** CAMARA maturity.

---

## NEEDS_REVIEW

- **`phoneNumberShare` (NV2)** as the Wi-Fi-suitable Number Verification path. Real `operationId` on Number Verification 2.1.0; access-type claim is not SOURCE_BACKED.

Explorer intent→capability rows for non-hero domains remain **INFERRED** (same APIs, new businesses).

---

## Validation

`python backend/scripts/validate_ax_cadence0.py`

**Cadence 0 PASSED (38 checks)** including:

- 13 business families, CURRENT_FOCUS on every operation
- specMaturity present; experimental sources labelled experimental
- restored Device Identifier / Recycling / Age / Insights
- unrelated experimental APIs not in the registry
- Rocket Bank / High Flight / Acme use restored CURRENT_FOCUS APIs
- `GET /catalog/retrieveIdentifier` → 200 with `spec_maturity: experimental`
- `GET /health` cadencePatch `0.2` reports `businessFamilies`

---

**STOP.** Do not start Cadence 1 until explicitly approved.
