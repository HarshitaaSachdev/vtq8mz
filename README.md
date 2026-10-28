# Wind Forecast Monitor

A web app that helps a UK energy supplier's day-ahead trading team understand **how reliable national wind generation forecasts are** when they buy power on the day-ahead market.

- **Live app:** https://vtq8mz.vercel.app
- **Video walkthrough:** _link added after recording_

![stack](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61dafb) ![stack](https://img.shields.io/badge/backend-Python%20%2B%20FastAPI-009688) ![stack](https://img.shields.io/badge/run-Docker-2496ed)

---

## The problem

Power for tomorrow must be bought **the day before**. Wind is a large, weather-dependent share of supply, so the team relies on wind forecasts to decide how much power to buy from other sources. This app answers two questions for purchase decisions made in **January 2026**:

1. **What did the latest forecast say at the moment the decision was made?**
2. **How wrong are those forecasts, in numbers we can plan around?**

## What the app shows

| Section | What it tells the user |
|---|---|
| **Actual vs forecast chart** | Real wind generation (blue) against the forecast that was available at decision time (orange). Hover to see when each forecast was published and how many hours ahead it was. |
| **Day-ahead decision view** | Uses only forecasts published by the chosen decision time (default 09:00 UK) on the day before delivery, exactly what the trader would have seen. |
| **Fixed horizon view** | Uses forecasts made at least *N* hours ahead (0–48h), to study how accuracy changes with lead time. |
| **KPI cards** | Mean absolute error, **P90 shortfall buffer** (in 90% of hours wind was at most this far below forecast), bias, worst hour, RMSE. |
| **Error vs horizon chart** | How error grows the further ahead a forecast is made; the day-ahead range (16–40h) is shaded. |
| **Error distribution** | Histogram of forecast minus actual, showing whether forecasts lean optimistic or pessimistic. |

### Key findings (January 2026, 09:00 day-ahead decision)

- Average error **≈ 2.0 GW** (~18% of average wind output of 11.3 GW).
- Forecasts were **systematically optimistic by ≈ 1.7 GW**.
- To be covered in 90% of hours, plan for **≈ 4.2 GW less wind** than forecast.
- Error grows from ≈ 1.7 GW (0h ahead) to ≈ 2.3 GW (48h ahead). Because the error is already large at 0h, part of it looks systematic rather than weather-driven (e.g. curtailment or a difference in what the two datasets measure). Worth investigating next.

---

## Architecture

```
React (Vite, Recharts)  ──/api──►  FastAPI (Python)  ◄── Elexon BMRS API
  charts + controls                 • loads & caches data   (FUELHH, WINDFOR)
                                    • selects forecasts
                                    • computes error metrics
```

- **Backend** owns all business logic, so it is tested in one place. The frontend only fetches and displays.
- **Data** for January 2026 is historical and immutable, so it is snapshotted to `backend/data/*.json`. The app falls back to fetching live from Elexon if the snapshot is missing.

### Core rule: no look-ahead

For each target half-hour, the app uses the **latest forecast published at or before a cutoff**:

- *Day-ahead view:* cutoff = decision time (UK local) on the day before delivery.
- *Horizon view:* cutoff = target time − N hours.

Forecasts published after their own target time are discarded. This rule is covered by unit tests, because using a forecast the trader could not have seen would make forecasts look better than they are.

### Data notes

- "Decisions made in January 2026" → delivery days **2 Jan – 1 Feb 2026**.
- Actuals (FUELHH, `fuelType = WIND`) are half-hourly; forecasts (WINDFOR) are hourly. Errors are measured on the hour only (no interpolation).
- Error = forecast − actual. Positive means less wind than forecast, so the buyer is short.
- All times are handled in UTC internally and displayed in UK local time (`Europe/London`), so GMT/BST changes are handled correctly.

---

## Project structure

```
.
├── backend/                     Python API
│   ├── app/
│   │   ├── config.py            Dates, decision time, constants
│   │   ├── elexon.py            Client for the Elexon FUELHH and WINDFOR endpoints
│   │   ├── data.py              Loads snapshot (or live data), builds in-memory dataset
│   │   ├── forecasts.py         Forecast selection: cutoffs and "latest before cutoff"
│   │   ├── metrics.py           MAE, RMSE, bias, percentiles, P90 shortfall
│   │   └── main.py              FastAPI routes under /api
│   ├── data/                    Snapshot of January 2026 Elexon data (JSON)
│   ├── scripts/snapshot.py      Re-downloads the snapshot from Elexon
│   ├── tests/                   Unit and API tests (pytest)
│   ├── requirements.txt         Runtime dependencies
│   ├── requirements-dev.txt     Runtime + test dependencies
│   └── Dockerfile
├── frontend/                    React app
│   ├── src/
│   │   ├── App.jsx              Page layout, settings state, data fetching
│   │   ├── api.js               All calls to the backend
│   │   ├── format.js            UK time and MW/GW formatting
│   │   ├── styles.css
│   │   └── components/          Controls, KpiCards, ForecastChart, HorizonChart, ErrorHistogram
│   ├── nginx.conf               Serves the built app and proxies /api in Docker
│   ├── vite.config.js           Dev server with /api proxy to the backend
│   └── Dockerfile               Multi-stage: build with Node, serve with nginx
├── vercel.json                  Vercel Services config: frontend + backend, /api routing
├── docker-compose.yml           Runs backend + frontend together
└── README.md
```

## API

| Endpoint | Description |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/meta` | Date range, defaults, data counts |
| `GET /api/series?mode=decision&decision_time=09:00&start=&end=` | Actual vs selected forecast per half-hour, plus metrics |
| `GET /api/series?mode=horizon&horizon_hours=24&start=&end=` | Same, using a fixed forecast horizon |
| `GET /api/accuracy/by-horizon?start=&end=` | Metrics for horizons 0–48h |

Interactive API docs: `/docs` (generated by FastAPI).

---

## Running the app

### Option 1: Docker (recommended)

Requires Docker Desktop.

```bash
docker compose up --build
```

Open http://localhost:8080 (API on http://localhost:8000/docs).

### Option 2: Run locally

**Backend** (Python 3.11+):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend** (Node 20.19+), in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### Tests

```bash
cd backend
python -m pytest -q
```

### Refreshing the data snapshot

```bash
cd backend
python -m scripts.snapshot
```

---
### Deployment (Vercel)

Deployed with [Vercel Services](https://vercel.com/kb/guide/vercel-services): `vercel.json` declares two services, the Vite frontend (`frontend/`) and the FastAPI backend (`backend/`, entrypoint `app.main:app`). Requests to `/api/*` are routed to the backend with the path unchanged, and everything else is served by the frontend. The frontend therefore uses the same `/api` paths locally (Vite proxy), in Docker (nginx) and in production.


## Limitations and next steps

- Scope is national wind only, January 2026, Elexon data only (as required).
- Investigate the systematic positive bias (e.g. curtailment, embedded vs transmission-connected wind).
- Add solar and demand forecasts to estimate the full residual volume to procure.
- Error breakdown by time of day and by wind level; probabilistic (quantile) bands on the main chart.
- Frontend tests (e.g. Vitest + React Testing Library) and CI on every push.

## Use of AI tools

As permitted by the brief, I used **Claude (Anthropic)** as an AI pair-programmer during this project. It helped me get up to speed on the UK day-ahead market and the Elexon datasets, accelerated writing the backend and frontend code, helped troubleshoot local environment issues, and assisted in drafting documentation.

I set up and ran the project end to end, reviewed and tested the code, verified the results against live Elexon data, and made the final calls on scope, design and presentation. 

