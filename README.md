# NetAware AX

**From Developer Experience (DX) to Agentic Experience (AX).**

Network Intent is the abstraction that lets an enterprise application or authorized agent express an **outcome**. NetAware handles discovery, governance, execution and verification underneath, and returns a **business outcome** the caller understands.

> SIMPLE OUTSIDE. SOPHISTICATED AND FULLY TRACEABLE INSIDE.

## Status

**Cadence 17.1 complete — Visual storytelling polish.** Live demo remains `0.6.1-ax6.1`. Product model and runtime are unchanged. Do not start Cadence 18 automatically.

| Document | Path |
|----------|------|
| Cadence 17.1 Visual storytelling | [`docs/cadences/ax-cadence-17.1.md`](docs/cadences/ax-cadence-17.1.md) |
| Cadence 17 Visual intelligence | [`docs/cadences/ax-cadence-17.md`](docs/cadences/ax-cadence-17.md) |
| Sales demo script | [`docs/AX-SALES-DEMO-SCRIPT.md`](docs/AX-SALES-DEMO-SCRIPT.md) |
| Sales runbook | [`docs/AX-SALES-RUNBOOK.md`](docs/AX-SALES-RUNBOOK.md) |
| Sales FAQ | [`docs/AX-SALES-FAQ.md`](docs/AX-SALES-FAQ.md) |
| External feedback | [`docs/AX-EXTERNAL-FEEDBACK.md`](docs/AX-EXTERNAL-FEEDBACK.md) |
| Cadence 16 Sales freeze | [`docs/cadences/ax-cadence-16.md`](docs/cadences/ax-cadence-16.md) |
| Demo script | [`docs/AX-DEMO-SCRIPT.md`](docs/AX-DEMO-SCRIPT.md) |
| Demo runbook | [`docs/AX-DEMO-RUNBOOK.md`](docs/AX-DEMO-RUNBOOK.md) |
| FAQ | [`docs/AX-FAQ.md`](docs/AX-FAQ.md) |
| Cadence 15 Stakeholder sales | [`docs/cadences/ax-cadence-15.md`](docs/cadences/ax-cadence-15.md) |
| Cadence 14 Demand Map | [`docs/cadences/ax-cadence-14.md`](docs/cadences/ax-cadence-14.md) |
| Cadence 13 Fulfillment Coverage | [`docs/cadences/ax-cadence-13.md`](docs/cadences/ax-cadence-13.md) |
| Cadence 12 Sales portfolio | [`docs/cadences/ax-cadence-12.md`](docs/cadences/ax-cadence-12.md) |
| Cadence 10 Decision Gap + High Flight | [`docs/cadences/ax-cadence-10.md`](docs/cadences/ax-cadence-10.md) |
| Cadence 9 Number Verification | [`docs/cadences/ax-cadence-9.md`](docs/cadences/ax-cadence-9.md) |
| Cadence 8 Discovery | [`docs/cadences/ax-cadence-8.md`](docs/cadences/ax-cadence-8.md) |
| Cadence 7 model alignment | [`docs/cadences/ax-cadence-7.md`](docs/cadences/ax-cadence-7.md) |
| Commercial evolution plan | [`docs/NetAware-AX-Commercial-Evolution-and-Cadence-Plan.md`](docs/NetAware-AX-Commercial-Evolution-and-Cadence-Plan.md) |
| Cadence 6 freeze | [`docs/cadences/ax-cadence-6.md`](docs/cadences/ax-cadence-6.md) |
| Cadence 5 Explorer | [`docs/cadences/ax-cadence-5.md`](docs/cadences/ax-cadence-5.md) |

Do not start another cadence automatically.

## Run locally

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
```

```powershell
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173

Optional hosted access gate (server-side HTTP Basic). Set `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD`, or the existing `DEMO_USERNAME` / `DEMO_PASSWORD`. `/health` stays unauthenticated. If neither pair is set, local development has no gate. Do not commit credential values.

```powershell
cd backend
python scripts/validate_ax_cadence0.py
python scripts/validate_ax_cadence1.py
python scripts/validate_ax_cadence2.py
python scripts/validate_ax_cadence3.py
python scripts/validate_ax_cadence4.py
python scripts/validate_ax_cadence6.py
python scripts/validate_ax_cadence6.1.py
python scripts/validate_ax_cadence10.py
python scripts/validate_ax_cadence13.py
python scripts/validate_ax_cadence14.py
python scripts/validate_ax_cadence15.py
python scripts/validate_ax_cadence16.py
python scripts/validate_ax_cadence17.py
python scripts/validate_ax_cadence17_1.py
```

## Boundaries

| Role | Project |
|------|---------|
| Write target | **NetAware AX** (this repository) |
| Read-only reference | Meta_Demo |
| Unrelated | Jigyasa — do not use |

This repository has **no runtime dependency** on Meta_Demo.

## Fictional enterprises (seed)

Rocket Bank · High Flight Airlines · Acme Manufacturing · CityCare Health
