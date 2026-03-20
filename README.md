# Hive

Hive is a two-service quantitative research and execution platform:

- `frontend/`: Next.js terminal + marketing experience
- `AI-backend/`: FastAPI meta-quant API (regime, alpha, risk, execution, optimizer, agent)

The current implementation is intentionally environment-driven and contract-first. Frontend surfaces read backend payloads through a local proxy (`/api/hive/*`) so backend host changes do not require code edits.

## 1. System Overview

### Architecture

```text
Browser
  -> Next.js Frontend (frontend, default :3000)
    -> Next Proxy Route (/api/hive/*)
      -> FastAPI Backend (AI-backend, default :8000)
        -> Services / Providers / Repositories
          -> Local model artifacts (BTP/models_p3_metaquant)
          -> Local market history (BTP/sp500)
          -> Optional live APIs (Yahoo Finance + CoinGecko)
```

### Key Design Principles

- Configurable by env vars, not hardcoded URLs
- Frontend and backend connected by explicit response contracts
- Fallback-safe rendering (frontend continues working if backend is temporarily unavailable)
- Dual backend data mode:
  - `HISTORICAL_DATA=true`: deterministic local data
  - `HISTORICAL_DATA=false`: live data with historical fallback

## 2. Repository Layout

```text
Hive/
  README.md
  AI-backend/
    app/
      main.py
      api/
      core/
      providers/
      repositories/
      schemas/
      services/
      utils/
    .env.example
    requirements.txt
  frontend/
    src/
      app/
      components/
      lib/
      types/
    .env.example
    package.json
  BTP/
    models_p3_metaquant/
    sp500/
    extra_data/
```

## 3. Backend (AI-backend) Deep Dive

## 3.1 Runtime Entry

- App entrypoint: `AI-backend/app/main.py`
- FastAPI app initialization includes:
  - CORS middleware (from `ALLOW_ORIGINS`)
  - API router mounted at `/api`
  - root metadata endpoint at `/`

## 3.2 Core Configuration

- Settings model: `AI-backend/app/core/config.py`
- Important behavior:
  - Loads from `.env`
  - Resolves relative dataset/artifact paths against repo root
  - Exposes parsed CORS origins list

### Important backend env vars

- `APP_ENV`: environment label (default `dev`)
- `HOST`: bind host (default `0.0.0.0`)
- `PORT`: bind port (default `8000`)
- `HISTORICAL_DATA`: `true`/`false`
- `SP500_DATA_DIR`: optional path to price CSV universe
- `MODEL_DATA_DIR`: optional path to model artifact folder
- `TICKER_MAPPING_FILE`: optional ticker metadata path
- `ALLOW_ORIGINS`: comma-separated frontend origins
- `MAX_UNIVERSE_SIZE`: alpha/risk universe cap
- `DEFAULT_USER_INITIALS`: shell user badge value
- `BASE_NOTIONAL_USD`: portfolio/risk notional baseline

## 3.3 API Surface

Router registration: `AI-backend/app/api/router.py`

### Route groups

- Health:
  - `GET /api/health`
- System:
  - `GET /api/system/status`
- Landing:
  - `GET /api/landing/overview`
- Marketing/public:
  - `GET /api/about`
  - `GET /api/methodology`
  - `GET /api/contact`
  - `POST /api/contact`
  - `GET /api/execute`
- Macro:
  - `GET /api/macro/regime`
  - `GET /api/macro/history`
  - `GET /api/macro/latent-factors`
  - `GET /api/macro/cross-asset`
  - `GET /api/macro/transitions`
  - `GET /api/macro/all`
- Alpha:
  - `GET /api/alpha/summary`
  - `GET /api/alpha/rankings`
  - `GET /api/alpha/features`
  - `GET /api/alpha/logs`
  - `GET /api/alpha/all`
- Risk:
  - `GET /api/risk/summary`
  - `GET /api/risk/clusters`
  - `GET /api/risk/orders`
  - `GET /api/risk/all`
- Agent:
  - `GET /api/agent/brief`
  - `GET /api/agent/stream`
  - `POST /api/agent/query`
- Backtest:
  - `GET /api/backtest/{run_id}`
- Execution:
  - `GET /api/execution/book`
  - `GET /api/execution/candles`
  - `GET /api/execution/positions`
  - `GET /api/execution/orders`
  - `POST /api/execution/order`
  - `GET /api/execution/all`
- Optimizer:
  - `POST /api/optimizer/solve`
  - `GET /api/optimizer/current`
  - `GET /api/optimizer/{job_id}`
- Snapshot:
  - `GET /api/metrics/snapshot`

## 3.4 Service Layer

Services live in `AI-backend/app/services/` and aggregate into API payload contracts.

- `system_service.py`: shell metrics (latency, EST clock, status, unread alerts, user initials)
- `landing_service.py`: homepage protocol/hero/market tape/onboarding blocks
- `marketing_service.py`: about/methodology/contact/execute content + contact submit handler
- `macro_service.py`: regime state/probabilities/history/transitions/cross-asset context
- `alpha_service.py`: ranking table, feature importance, model confidence/decay and logs
- `risk_service.py`: exposure/diversification/clusters/active orders
- `backtest_service.py`: KPIs, equity curve, trade log, decomposition stats, model params
- `execution_service.py`: L2 book, candles, positions, order log, order placement
- `optimizer_service.py`: constrained solve, frontier, optimal point, rebalance table, job state
- `agent_service.py`: daily brief, heatmap, tools, worker stream, query answers
- `metrics_service.py`: deep merge snapshot of all desks/pages into one payload

## 3.5 Data Providers and Repositories

### Providers (`AI-backend/app/providers`)

- `historical.py`: loads quotes/candles/volume from local datasets
- `live.py`: live quote/candle/volume calls with fallback to historical provider

### Repositories (`AI-backend/app/repositories`)

- `sp500.py`: ticker list, historical series, close matrix helpers
- `artifacts.py`: model/performance/feature registries from `BTP/models_p3_metaquant`

## 4. Frontend (Next.js) Deep Dive

## 4.1 Runtime and Routing

- App router root: `frontend/src/app/`
- Main page groups:
  - Marketing/public: `/`, `/about`, `/methodology`, `/contact`, `/execute`
  - Terminal desks: `/terminal/*`

## 4.2 Layout Structure

- Marketing shell:
  - `frontend/src/components/layout/MarketingHeader.tsx`
  - `frontend/src/components/layout/MarketingFooter.tsx`
- Terminal shell:
  - `frontend/src/components/layout/TerminalLayout.tsx`
  - `frontend/src/components/layout/Header.tsx`
  - `frontend/src/components/layout/Sidebar.tsx`

Terminal header/sidebar show live shell metrics from `/api/system/status`.

## 4.3 Frontend API Integration Layer

### Proxy route

- File: `frontend/src/app/api/hive/[...path]/route.ts`
- Behavior:
  - Receives frontend calls at `/api/hive/*`
  - Forwards to `${HIVE_BACKEND_URL}/api/*`
  - Preserves query strings and selected headers

### API utilities

- `frontend/src/lib/api/http.ts`
  - Client-side `apiGet`, `apiPost`, query builder, typed API errors
- `frontend/src/lib/api/server.ts`
  - Server-side `serverGet`, `serverPost` for SSR routes
- `frontend/src/lib/api/types.ts`
  - Typed response/request contracts
- `frontend/src/lib/api/fallbacks.ts`
  - Safe fallback payloads for offline/degraded mode
- `frontend/src/lib/hooks/useApiResource.ts`
  - Client polling hook with refresh interval + error + fallback handling

## 4.4 Page-to-Endpoint Mapping

### Marketing/public pages

- `/` -> `GET /api/landing/overview`
- `/about` -> `GET /api/about`
- `/methodology` -> `GET /api/methodology`
- `/contact` -> `GET /api/contact` + `POST /api/contact`
- `/execute` -> `GET /api/execute`

### Terminal desks

- `/terminal/macro-desk` -> `GET /api/macro/all`
- `/terminal/alpha-factory` -> `GET /api/alpha/all`
- `/terminal/risk-desk` -> `GET /api/risk/all`
- `/terminal/backtest` -> `GET /api/backtest/latest`
- `/terminal/execution` -> `GET /api/execution/all` + `POST /api/execution/order`
- `/terminal/portfolio` -> `GET /api/optimizer/current` + `POST /api/optimizer/solve`
- `/terminal/agent` -> `GET /api/metrics/snapshot` + `POST /api/agent/query`

## 4.5 Frontend env vars

- `HIVE_BACKEND_URL`: backend base URL for proxy target
- `NEXT_PUBLIC_HIVE_PROXY_PREFIX`: frontend proxy prefix (default `/api/hive`)

File template: `frontend/.env.example`

## 5. How Frontend and Backend Are Connected

## 5.1 Read flow

1. A page or component requests data from `/api/hive/<group>/<route>`
2. Next proxy route forwards to `${HIVE_BACKEND_URL}/api/<group>/<route>`
3. FastAPI route calls the service container and returns payload
4. Frontend renders typed payload; on failure, uses fallback contract data

## 5.2 Action flow

Example: order submission

1. UI collects order form values in `/terminal/execution`
2. Client posts to `/api/hive/execution/order`
3. Backend validates `OrderRequest`, simulates route/acceptance
4. UI displays order feedback and refreshes execution payload

## 5.3 Contract alignment

The main contract source for frontend display requirements is:

- `frontend/metrics.md`

Backend route groups and payloads are aligned to that contract.

## 6. Local Development

## 6.1 Start backend

```powershell
cd AI-backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 6.2 Start frontend

```powershell
cd frontend
npm install
npm run dev
```

## 6.3 Verify

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/api/health`
- Snapshot: `http://localhost:8000/api/metrics/snapshot`

## 7. Build and Quality Checks

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Backend (manual smoke):

- Open `/docs`
- Call `/api/health`
- Call `/api/metrics/snapshot`

## 8. Known Behaviors and Troubleshooting

- If backend is down, frontend still renders using fallback payloads.
- Execution chart requires valid candle OHLC values; no-data state is handled in `PriceChart`.
- If live mode external APIs fail, backend providers automatically fall back to historical data where possible.

## 9. Historical Research Assets

`BTP/` contains research notebooks and model artifacts used by backend services.

Important folders:

- `BTP/sp500/`: ticker CSV histories
- `BTP/models_p3_metaquant/`: model registry/performance/features/weights
- `BTP/extra_data/`: ticker/company mapping files

These are operational dependencies for deterministic historical-mode backend responses.

## 10. Notes

- This repository previously documented a different multi-service stack at root level. The root README now reflects the current implemented architecture (`frontend` + `AI-backend`).
- For service-specific setup details, also see:
  - `frontend/README.md`
  - `AI-backend/README.md`
