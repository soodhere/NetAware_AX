# Cadence 6.1 — Network API value clarity (presentation patch)

**Not Cadence 7.** Product behavior remains frozen. No catalog, policy, autonomy, or runtime logic changes.

## What changed

- Briefing structure: **My world → Network adds → NetAware AX → My intent** before Run
- **Observe / Verify / Act** labels on capabilities and catalog families
- Runtime **Overview** contribution strip: business evidence · network contribution · NetAware decision · outcome
- Decision trace shows **why relevant** and **what changed**
- Home, Close, and Explorer copy strengthened around complementarity
- **CAMARA labelling:** NetAware business status, CAMARA API version, API version maturity, and CAMARA project lifecycle are shown as separate dimensions. Repository Incubating is not presented as API-version immaturity.

## CAMARA dimensions (do not combine)

| Label | Meaning | Where shown |
| --- | --- | --- |
| NetAware CURRENT FOCUS | Catalog choice for the AX demo | Primary cards |
| CAMARA API (e.g. 2.1.0) | Pinned specification version | Primary cards |
| API version maturity | STABLE PUBLIC / INITIAL / PRE-STABLE / EXPERIMENTAL from pinned version + source | Primary cards when source-backed |
| CAMARA project lifecycle | Incubating / Experimental repository | Technical drill-down only |

Example: SIM Swap remains **Current Focus**, **CAMARA API 2.1.0**, **Stable public API**. Incubating, if shown, is **CAMARA project lifecycle**, not API readiness.

## High Flight opening hero assessment

High Flight remains first in demo order (Cadence 6 freeze). With 6.1 briefing copy, the Network contribution is explicit:

- Reachability and connectivity are **not** baggage position
- Network evidence helps determine whether the **network dimension** is limiting
- QoD stays NOT_REQUIRED when physical transfer is the limit

**Presenter recommendation:** Rocket Bank (VERIFY/OBSERVE) or Acme (ACT) are simpler zero-context openers if the audience is unfamiliar with airline operations.

## Validation

```powershell
cd backend
python scripts/validate_ax_cadence0.py
python scripts/validate_ax_cadence6.py
python scripts/validate_ax_cadence6.1.py
```
