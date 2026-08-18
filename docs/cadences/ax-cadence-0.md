# AX Cadence 0 — Foundation

**Status:** Implemented and validated.  
**Cadence:** 0  
**Execution engine:** not implemented  
**Demo UI:** not implemented  

Stop here. Do not start Cadence 1 without explicit approval.

---

## Architecture created

```
NetAware AX/
  README.md
  .gitignore
  openapi/                         independently pinned CAMARA specs
    AX_PIN.yaml
    manifest.yaml
    camara/
    experimental/
  data/
    schemas/                       entity + evidence-grade notes
    model/                         configuration graph (YAML)
  backend/
    requirements.txt
    app/                           FastAPI: health, catalog, graph reads
    scripts/validate_ax_cadence0.py
  frontend/README.md               deferred — no UI in Cadence 0
  docs/
    ax-prototype-plan.md
    cadences/ax-cadence-0.md       this file
```

There is **no runtime dependency** on Meta_Demo. Specs were independently copied into this repository.

---

## Catalog source / pinning

| Item | Value |
|------|--------|
| Source org | [camaraproject](https://github.com/camaraproject) |
| Acquisition date | 2026-08-15 |
| Pin policy | Latest public GitHub release when present; otherwise default-branch API definitions |
| Local copies | `openapi/camara` (29 YAML) · `openapi/experimental` (62 YAML) |
| Manifest | `openapi/manifest.yaml` |
| AX pin record | `openapi/AX_PIN.yaml` |

Parser: `backend/app/registry.py` reads OpenAPI `paths` and keeps only operations that already have an `operationId`. **No invented IDs.**

Duplicate `operationId`s (31 IDs) are expected when superseded parent packs and split APIs both exist, or when different APIs reuse a name (`createSession` on Quality-on-Demand vs Session Insights vs WebRTC). Mappings always disambiguate with `source` (file path).

Preferred sources for seed mappings are listed in `openapi/AX_PIN.yaml`.

---

## Catalog statistics

| Metric | Count |
|--------|------:|
| Operations parsed (all files) | 273 |
| Excluding superseded parent packs | 255 |
| Unique `operationId`s | 240 |
| Spec files contributing operations | 91 |
| Maturity (non-superseded) | camara 45 · experimental 210 |

Family labels are derived from API title/path (catalog metadata), not from invented operations.

---

## Entity model

Configuration YAML under `data/model/`:

Domain, UseCase, Intent, Purpose, Capability, Enterprise, Application, Agent, Policy, PolicyRule, ConsentRule, Agreement, AutonomyRule, Subscription, Entitlement, Provider, Route.

Execution placeholders only (`data/model/execution-placeholders.yaml`): RuntimeContext, Evidence, Plan, PlanStep, Decision, Invocation, Outcome.

Agent is distinct from Application (`actsOnBehalfOf`, `allowedIntents`, autonomy rules). Identity is `simulated_placeholder`. Production auth/delegation is not locked.

Route types present: `DIRECT`, `AGGREGATED`, `HYBRID`, `EXISTING_ENTERPRISE_INTEGRATION`. These are execution-path labels, not a hosting decision. Telco Finder / API Finder are **not** executed.

---

## Mapping model

All Domain ↔ Catalog links live in `data/model/mappings.yaml`. Python only indexes that file (`backend/app/graph.py`). Relationships are **not** hardcoded in control flow.

Forward:

```
Domain → UseCase → Intent → Capability → API Catalog Operation
```

Reverse:

```
Operation → Capability → Intent → UseCase → Domain
```

Every mapping row has an evidence grade:

| Grade | Meaning |
|-------|---------|
| `SOURCE_BACKED` | Catalog operation exists in the pin; or the intent→capability pairing is grounded in prior executed Network Intent behaviour (financial continuity / manufacturing experience). |
| `INFERRED` | Real catalog operations, but the **business** pairing (airline baggage → those capabilities) is a product inference, not a CAMARA-defined use case. |
| `NEEDS_REVIEW` | Must not be treated as fact until spec review. |

Cadence 0 mapping counts (intentCapabilities + capabilityOperations rows):

| Grade | Count |
|-------|------:|
| SOURCE_BACKED | 29 |
| INFERRED | 4 |
| NEEDS_REVIEW | 1 |

---

## Sample forward mappings

### 1. Financial → assess_network_trust

```
financial
  → high-value-payment-protection
    → assess_network_trust
      → number_possession_verification, number_recycling, tenure,
        sim_continuity, device_continuity, device_identifier,
        roaming_status, location_verification (considered)
        → phoneNumberVerify, phoneNumberShare (NEEDS_REVIEW),
          checkNumberRecycling, checkTenure,
          checkSimSwap, retrieveSimSwapDate,
          checkDeviceSwap, retrieveDeviceSwapDate,
          retrieveIdentifier, getRoamingStatus, verifyLocation
```

Intent→capability evidence: **SOURCE_BACKED** (continuity assessment family).  
11 catalog operations resolved.

### 2. Airlines → ensure_baggage_connection

```
High Flight Airlines
  ↓
Baggage Operations          (existing Application)
  ↓
Baggage Operations Agent    (authorized Agent; actsOnBehalfOf Baggage Operations)
  ↓
ensure_baggage_connection   (Intent — configuration only, not executed)
  ↓
baggage-connection          (Use Case)
  ↓
required / considered capabilities
  · location_verification     INFERRED
  · device_reachability       INFERRED
  · connectivity_insights     INFERRED
  · quality_on_demand         INFERRED
  ↓
real API Catalog operations (SOURCE_BACKED ids, preferred sources)
  · verifyLocation              Device Location Verification
  · getReachabilityStatus       Device Reachability Status
  · checkNetworkQuality         Connectivity Insights
  · retrieveQoSProfiles         QoS Profiles
  · createSession               Quality-On-Demand
  · getSession                  Quality-On-Demand
```

Complementary **domain/enterprise** APIs (not CAMARA): Baggage Journey, Flight Status, Ground Operations — modeled as `EXISTING_ENTERPRISE_INTEGRATION` routes.

6 catalog operations resolved. **This is data traversal, not runtime selection.**

### 3. Manufacturing → maintain_inspection_experience

```
manufacturing
  → critical-inspection-camera
    → maintain_inspection_experience
      → application_profiles, connectivity_insights,
        edge_discovery, quality_on_demand
        → createApplicationProfile, checkNetworkQuality,
          readClosestEdgeCloudZone, retrieveQoSProfiles,
          createSession, getSession
```

Intent→capability evidence: **SOURCE_BACKED** (experience / SLO family).  
6 catalog operations resolved.

---

## Sample reverse mappings

### `verifyLocation`

Device Location Verification → capability `location_verification` → intents `assess_network_trust` **and** `ensure_baggage_connection` → use cases High-value payment protection **and** Baggage connection → domains Financial **and** Airlines.

### `createSession`

Quality-On-Demand (canonical source `QualityOnDemand__quality-on-demand.yaml`; other APIs also define `createSession`) → capability `quality_on_demand` → intents `ensure_baggage_connection` **and** `maintain_inspection_experience` → Airlines **and** Manufacturing.

Additional reverse check: `phoneNumberVerify` → Financial only; `getReachabilityStatus` → Airlines only.

---

## API endpoints (Cadence 0)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Cadence 0, registryLoaded, no execution engine |
| GET | `/catalog` | Full parsed catalog |
| GET | `/catalog/{operationId}` | Operation variants + reverse graph |
| GET | `/domains` | Domain list |
| GET | `/domains/{domainId}` | Forward graph from a domain |
| GET | `/intents` | Intent list |
| GET | `/intents/{intentId}` | Use case, capabilities, catalog operations |
| GET | `/capabilities` | Capability list |
| GET | `/capabilities/{capabilityId}` | Operations + intents |

**Not implemented:** `POST /intents`, planning, execution, policy evaluator, Telco/API Finder runtime, replan, Demo UI.

Run locally:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
```

```powershell
python scripts/validate_ax_cadence0.py
```

---

## Validation results

`python backend/scripts/validate_ax_cadence0.py`

**Cadence 0 PASSED (24 checks)** including:

1. SOURCE_BACKED operationId+source exists in pin  
2. Duplicate operationIds explained by distinct sources  
3. Intents → valid capabilities  
4. Capabilities → valid operations or explicit NEEDS_REVIEW  
5. Use cases → valid intents  
6. Domains → valid use cases  
7. Reverse traversal  
8. Forward traversal (three sample intents)  
9. Agent allowedIntents valid; Agent ≠ Application  
10. Route/provider refs valid  
11. Backend Python does not reference Meta_Demo or Jigyasa  
12. HTTP foundation endpoints  

---

## NEEDS_REVIEW items

1. **`phoneNumberShare` as Wi-Fi-suitable Number Verification (NV2)**  
   Catalog operation is real (`NumberVerification__number-verification.yaml`).  
   Mapping to “NV2 instead of NV1 on Wi-Fi” is **not** treated as SOURCE_BACKED. Spec review required before Cadence 2 script freeze.

No other NEEDS_REVIEW rows in Cadence 0 seed mappings.

---

## Known gaps

- Full CAMARA catalogue is pinned; only 18 operations are linked into the three seed intents.  
- Family bucket `OTHER` is large (unmapped APIs) — expected until Explorer breadth (Cadence 5).  
- Policy/consent/autonomy records exist but are **not evaluated**.  
- Domain/enterprise APIs are named stubs, not simulated call implementations.  
- Duplicate `createSession` across APIs requires callers to use `source` for canonical QoD.  
- Frontend is a README placeholder only.

---

## Questions deferred

- Production agent identity / delegation  
- Hosting model  
- Whether NetAware proxies every call  
- MCP, LLM, live operators  
- NV1 vs NV2 exact binding  
- Policy evaluator, Telco Finder, API Finder execution  
- Cadence 1 UI  

---

## Boundary confirmation

| Repo | This cadence |
|------|----------------|
| **NetAware AX** | Write target — all new files |
| **Meta_Demo** | Read-only source of pin conventions; not modified for this cadence |
| **Jigyasa** | Not used |

---

## Cadence 0.2 / 1 / 2 follow-up

Cadence 0.2 is the business catalog: [`ax-cadence-0.2.md`](ax-cadence-0.2.md).  
Cadence 1 is Home + Explore: [`ax-cadence-1.md`](ax-cadence-1.md).  
Cadence 2 is the first live run: [`ax-cadence-2.md`](ax-cadence-2.md). Full OpenAPI files remain on disk for reference only.
