# AX Cadence 5 — Product Explorer + Evidence Reuse

**Status:** Complete  
**Version:** `0.5.0-ax5`  
**Scope:** NetAware AX product coherence. No fifth hero scenario.

## Objective

Make NetAware AX feel like one connected product rather than four isolated demos:

- Full **Explorer** product knowledge surface (11 nav entities)
- Forward and reverse graph traversal with cross-links
- **Evidence reuse** across intents (Rocket Bank trust → recovery)
- All four hero demos unchanged

## Explorer navigation

| Entity | Endpoint |
|--------|----------|
| Domains | `/domains`, enriched detail |
| Use cases | `/use-cases`, enriched detail |
| Intents | `/intents`, enriched detail |
| Agents | `/explore/agents` |
| My Context | `/explore/my-context/{enterpriseId}` |
| Purposes | `/explore/purposes` |
| Policies | `/explore/policies` |
| Autonomy | `/explore/autonomy` |
| Capabilities | `/capabilities`, enriched detail |
| API Catalog | `/catalog/apis`, enriched detail |
| Providers / Routes | `/explore/providers` |

## Evidence reuse

1. Run `assess_network_trust` → normalized evidence persisted (`ax-rb-trust-001`)
2. Run `assess_recovery_continuity` → reuses `checkSimSwap`, `checkDeviceSwap`, `getRoamingStatus`
3. Eligibility checks: tenant, subject, purpose matrix, TTL, policy
4. Decisions marked `EVIDENCE_REUSED`; zero API invocations on second run

## Executable intents (5)

| Intent | Role |
|--------|------|
| `assess_network_trust` | Hero — Rocket Bank |
| `assess_recovery_continuity` | Reuse companion (not hero) |
| `ensure_baggage_connection` | Hero — High Flight |
| `maintain_inspection_experience` | Hero — Acme |
| `verify_pharmacy_age_gate` | Hero — CityCare |

## Validation

```bash
cd backend
python scripts/validate_ax_cadence5.py
```

Regression: Cadence 0–4 validators accept cadence 5.

## STOP

Cadence 6 not started.
