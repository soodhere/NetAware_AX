# AX Sales Runbook

Cadence 17.1. One URL. Environment-driven Basic Auth. No tenant login.

## Sales handoff

Need only:

1. Hosted URL
2. Username / password (hosting secrets — not in this repository)
3. Stakeholder: Enterprise / Operator / Aggregator
4. Recommended path: **Start meeting → 3-minute executive**

Optional: 7-minute or Technical. Then `#/map` with Projector focus if the room cannot read the 17×13 matrix.

## Preflight

Footer should show **DEMO READY**. If not, check `/health` and `/preflight`. `/health` stays unauthenticated for hosting checks.

Confirm UI cadence 17, visual patch 17.1, version `0.6.1-ax6.1`, 13 families, 17 use cases. Footer: Cadence 17.1 · DEMO READY.

## Login

If hosted credentials are configured, the browser prompts for HTTP Basic. Username/password come from hosting secrets (`BASIC_AUTH_USERNAME` / `BASIC_AUTH_PASSWORD` or `DEMO_*`). They are not in the repository.

## Reset

Click **Reset Demo** in the footer before every meeting. It restores Business View, hides presenter cues, clears meeting depth, resets evidence store, and returns to Welcome. It does not change product configuration.

Runtime **Reset** / **Replay** / **Pause** / **Step** still work on a live scenario.

## Recommended click path (short demo)

1. Welcome → pick Enterprise / Operator / Aggregator.
2. **Start meeting**.
3. Stay on **3-minute executive**.
4. Follow the numbered steps. Last step is Close.
5. If asked “show me more,” switch to 7-minute or Technical deep dive. Same product.
6. Optional CTO beat: `#/map` then `#/map/matrix`. Use **Projector focus** if the room cannot read the 17×13 grid. Filter to one use case or one API family.

## What not to click in a 3-minute demo

- Explorer reverse mappings
- Raw policy matrices
- Catalog operationId drill-down
- Show presenter cues (keep hidden unless you need them)
- A second live run unless the first finished
- Full 17×13 matrix without projector focus

## If you get lost

- Footer **Change perspective** → Welcome.
- **Reset Demo**.
- Hash URLs are safe to refresh: `#/meet/enterprise/exec`, `#/meet/operator/exec`, `#/meet/aggregator/exec`, `#/map`, `#/close`.
- Brand mark returns to the current stakeholder landing.

## After the meeting

Portfolio, Explorer, Fulfillment, Demand, and Use Case ↔ API Map are the same product. Let a technical buyer drill without a second demo.
