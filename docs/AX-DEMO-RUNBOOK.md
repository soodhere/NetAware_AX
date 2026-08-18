# AX Demo Runbook

## Start

### Backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

## Expected health

```powershell
curl http://127.0.0.1:8000/health
```

Expect:

- `cadence`: **6**
- `cadencePatch`: **6.1**
- `version`: **0.6.1-ax6.1**
- `executableIntents`: 5 (4 heroes + recovery reuse)
- `explorerProductSurface`: true

## Routes (hash router)

| Route | Purpose |
|-------|---------|
| `#/` | Home |
| `#/demo` | Scenario picker (High Flight first) |
| `#/demo/high-flight-airlines/baggage-connection` | High Flight briefing |
| `#/demo/high-flight-airlines/baggage-connection/run` | High Flight live run |
| `#/demo/rocket-bank/high-value-payment-protection/run` | Rocket Bank |
| `#/demo/acme-manufacturing/critical-inspection-camera/run` | Acme |
| `#/demo/citycare-health/pharmacy-age-gate/run` | CityCare |
| `#/demo/rocket-bank/account-recovery-anomaly/run` | Evidence reuse (secondary) |
| `#/explore` | Product Explorer |
| `#/close` | Product close |

## Reset procedure

1. On any **Runtime** screen, click **Reset**.
2. Calls `POST /executions/reset` — clears execution trace **and** evidence store.
3. Before evidence reuse demo, always reset or run trust first from recovery screen (auto-seeds trust).

## Runtime controls

- **Run** — execute intent
- **Pause / Resume** — stop animation
- **Step** — advance one beat
- **Replay** — replay current trace
- **Skip to end** — jump to outcome (90s cut)
- **Speed** — 1× / 2× / 4×

## Demo-safe checks

```powershell
cd backend
python scripts/validate_ax_cadence6.py
python scripts/validate_ax_cadence5.py
python scripts/validate_ax_cadence4.py
```

Frontend build:

```powershell
cd frontend
npm run build
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Failed to fetch` | Start backend on port 8000 |
| Stale outcome after switch enterprise | Click **Reset** |
| Evidence reuse shows invocations | Reset, run trust first, then recovery |
| Blank Runtime | Check enterprise/use-case pair matches hero list |
| Wrong cadence in footer | Restart backend after pull |

## Boundaries

- **Write:** NetAware AX only
- **Read-only:** Meta_Demo
- **Do not touch:** Jigyasa

Product behavior is **frozen** at Cadence 6. Presentation changes only.
