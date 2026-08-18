# AX Cadence 1 — Zero-context shell + Explorer

**Status:** Implemented and validated.  
**Cadence:** 1  
**Execution engine:** Cadence 2 adds a Rocket Bank run; Explore remains configuration traversal.  
**Demo UI:** Home + Explore (read-only graph)

Product story:

> FROM DEVELOPER EXPERIENCE TO AGENTIC EXPERIENCE  
> Network Intent is the abstraction enabling AX.

A person with no CAMARA background can start in their business, see systems they already have, express an outcome as Intent, and understand that NetAware will later handle Network API complexity underneath.

See [`ax-cadence-2.md`](ax-cadence-2.md) for the first live run.

---

## Views

| View | Route | Purpose |
|------|-------|---------|
| Home | `#/` | DX → AX. Equation: My world + Network capabilities + Intent = Agentic Experience. Start Demo / Explore. |
| Domain entry | `#/demo` | Financial Services / Airlines / Manufacturing via Rocket Bank, High Flight, Acme. |
| Use case pick | `#/demo/{enterprise}` | Recognizable use cases from Cadence 0.2 config. |
| **Your World** | `#/demo/{enterprise}/{useCase}` | Complementarity, Intent, configured knowledge vs runtime request, Agent, policy/autonomy preview, mapping chain. |
| Explore hub | `#/explore` | Configuration graph counts. |
| Domains / Use cases / Intents / Capabilities | `#/explore/...` | Forward and reverse cross-links. |
| API Catalog | `#/explore/catalog` | **13 business families**, not 37 YAML files. |
| Family / operation drill-down | `#/explore/catalog/{id}`, `#/explore/operations/{operationId}` | Actual `operationId`s, business status vs CAMARA maturity. |

Navigation is Home / Start Demo / Explore. Not TRUST / EXPAND / ASSURE.

---

## Data used

All reads come from Cadence 0.2 configuration + `data/model/demo-briefings.yaml` presentation:

- `AX_ACTIVE_CATALOG` — 13 CURRENT_FOCUS families, 18 technical specs, 37 operations
- Enterprises, applications, authorized agents
- Domains, use cases, intents, capabilities, mappings
- Policy / consent / autonomy / agreement **previews** (not evaluated on Explore)

---

**STOP for Cadence 1.** Live execution is Cadence 2.
