# NetAware AX

**From Developer Experience (DX) to Agentic Experience (AX).**

Network Intent is the abstraction that lets an enterprise application or authorized agent express an **outcome**. NetAware handles discovery, governance, execution and verification underneath, and returns a **business outcome** the caller understands.

> SIMPLE OUTSIDE. SOPHISTICATED AND FULLY TRACEABLE INSIDE.

## Status

**Cadence 6 complete.** Presentation freeze — product behavior frozen. See presenter docs.

| Document | Path |
|----------|------|
| Demo script | [`docs/AX-DEMO-SCRIPT.md`](docs/AX-DEMO-SCRIPT.md) |
| Demo runbook | [`docs/AX-DEMO-RUNBOOK.md`](docs/AX-DEMO-RUNBOOK.md) |
| FAQ | [`docs/AX-FAQ.md`](docs/AX-FAQ.md) |
| Cadence 6 freeze | [`docs/cadences/ax-cadence-6.md`](docs/cadences/ax-cadence-6.md) |
| Cadence 5 Explorer | [`docs/cadences/ax-cadence-5.md`](docs/cadences/ax-cadence-5.md) |

Do not start Cadence 7 until explicitly approved.

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

```powershell
cd backend
python scripts/validate_ax_cadence0.py
python scripts/validate_ax_cadence1.py
python scripts/validate_ax_cadence2.py
python scripts/validate_ax_cadence3.py
python scripts/validate_ax_cadence4.py
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
