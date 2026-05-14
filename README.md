# Hive

Hive is a contract-first quantitative research and simulated execution platform with two deployable services:

- `frontend/`: Next.js 16 terminal + marketing UI
- `AI-backend/`: FastAPI meta-quant API (macro, alpha, risk, execution, optimizer, agent)

The platform is environment-driven and fallback-safe:

- HTTP traffic from frontend goes through a local proxy (`/api/hive/*`)
- Real-time channels use WebSockets directly to backend (`/api/system/ping`, `/api/agent/stream/ws`)
- UI continues rendering from typed fallback payloads when backend is temporarily unavailable

## 1. Current System Capabilities

### 1.1 Intelligence Layer (Quant Core)

- Macro regime desk with state probabilities, transition matrix, latent factors, and transition log
- Alpha desk with cross-sectional ranking, decile visibility, feature importance, and execution log
- Risk desk with exposure, diversification, cluster allocations, and HRP dendrogram visualization
- Backtest desk with equity curve, trade log, and strategy diagnostics
- Optimizer desk with constrained solve, frontier, optimal point, and rebalance deltas

### 1.2 Execution and Friction Engine

- Local simulated ledger:
  - `cash`
  - `holdings`
  - `history`
- Transaction cost model at `5 bps` per trade
- Volume-aware market impact model:
  - Participation = order notional / ADV notional
  - Slippage penalty scales with participation
- Capital scalability analysis:
  - UI slider from `$10,000` to `$100,000,000`
  - Projected return and Sharpe degrade as friction rises

### 1.3 Real-Time and Transparency

- Live system latency indicator in terminal header via WebSocket ping/pong
- Token-by-token Fin-OSS agent streaming via WebSocket (ChatGPT-style progressive rendering)
- Dynamic SHAP-style attribution modal for selected alpha tickers
- Rolling 30-day Rank IC monitoring with model decay warning when threshold is breached

## 2. Architecture

```text
Browser
  -> Next.js Frontend (default :3000)
      -> HTTP Proxy Route (/api/hive/*)
          -> FastAPI Backend (/api/*, default :8000)
      -> Direct WebSocket Channels
          -> ws://<backend>/api/system/ping
          -> ws://<backend>/api/agent/stream/ws

FastAPI Backend
  -> Services (macro, alpha, risk, execution, optimizer, agent, metrics)
  -> Providers (historical/live data with fallback)
  -> Repositories (model artifacts + price history)
  -> In-memory app state (ledger, optimizer jobs, worker streams)

Data Dependencies
  -> BTP/models_p3_metaquant (artifacts, registries, diagnostics)
  -> BTP/sp500 (historical OHLCV CSV universe)
  -> BTP/extra_data (ticker metadata)
```

## 3. Repository Layout

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

## 4. Backend Deep Dive (AI-backend)

### 4.1 Runtime

- Entrypoint: `AI-backend/app/main.py`
- API root prefix: `/api`
- CORS configured from `ALLOW_ORIGINS`

### 4.2 Key Services

- `system_service.py`: shell status, clock, latency baseline, alerts, user badge
- `macro_service.py`: regime state machine, history, transitions, market context
- `alpha_service.py`: rankings, rolling IC, SHAP detail payloads, diagnostics/logs
- `risk_service.py`: exposure/diversification, clusters, dendrogram, active orders
- `execution_service.py`: order book/candles/orders/positions, ledger updates, friction/capacity
- `ledger_service.py`: local execution ledger state and fill accounting
- `agent_service.py`: briefing, worker stream, query reasoning, token stream helper
- `optimizer_service.py`: portfolio solve + in-memory job lifecycle
- `metrics_service.py`: merged snapshot payload for terminal agent view

### 4.3 API Surface

#### Health

- `GET /api/health`

#### System

- `GET /api/system/status`
- `WS /api/system/ping`

#### Landing / Public

- `GET /api/landing/overview`
- `GET /api/about`
- `GET /api/methodology`
- `GET /api/contact`
- `POST /api/contact`
- `GET /api/execute`

#### Macro

- `GET /api/macro/regime`
- `GET /api/macro/history`
- `GET /api/macro/latent-factors`
- `GET /api/macro/cross-asset`
- `GET /api/macro/transitions`
- `GET /api/macro/all`

#### Alpha

- `GET /api/alpha/summary`
- `GET /api/alpha/rankings`
- `GET /api/alpha/features`
- `GET /api/alpha/rolling-ic`
- `GET /api/alpha/shap/{ticker}`
- `GET /api/alpha/logs`
- `GET /api/alpha/all`

#### Risk

- `GET /api/risk/summary`
- `GET /api/risk/clusters`
- `GET /api/risk/dendrogram`
- `GET /api/risk/orders`
- `GET /api/risk/all`

#### Agent

- `GET /api/agent/brief`
- `GET /api/agent/stream`
- `POST /api/agent/query`
- `WS /api/agent/stream/ws`

#### Backtest

- `GET /api/backtest/{run_id}`

#### Execution

- `GET /api/execution/book`
- `GET /api/execution/candles`
- `GET /api/execution/positions`
- `GET /api/execution/orders`
- `POST /api/execution/order`
- `GET /api/execution/ledger`
- `GET /api/execution/capacity`
- `POST /api/execution/capacity`
- `GET /api/execution/all`

#### Optimizer

- `POST /api/optimizer/solve`
- `GET /api/optimizer/current`
- `GET /api/optimizer/{job_id}`

#### Snapshot

- `GET /api/metrics/snapshot`

### 4.4 WebSocket Event Contracts

#### `/api/system/ping`

Client -> Server:

```json
{ "client_ts": 1710000000000 }
```

Server -> Client:

```json
{ "type": "pong", "client_ts": 1710000000000, "server_ts": 1710000000012 }
```

#### `/api/agent/stream/ws`

Server emits:

- `{ "type": "start", "channel": "brief" | "query" }`
- `{ "type": "token", "channel": "brief" | "query", "token": "..." }`
- `{ "type": "done", "channel": "brief" | "query", "suggested_command": "..." }`
- `{ "type": "error", "channel": "query", "message": "..." }`

Client query message:

```json
{ "query": "What is the current risk posture?" }
```

## 5. Frontend Deep Dive (Next.js)

### 5.1 App Structure

- Marketing pages: `/`, `/about`, `/methodology`, `/contact`, `/execute`
- Terminal pages: `/terminal/*`
- Shell components:
  - `TerminalLayout`
  - `Header`
  - `Sidebar`

### 5.2 Data Integration

- HTTP client layer:
  - `apiGet`, `apiPost`, server equivalents, typed contracts, fallback payloads
- Polling hook:
  - `useApiResource` for periodic sync and graceful degradation
- WebSocket hook:
  - `useWebSocket` for latency pings and token stream rendering

### 5.3 Frontend Page to Backend Mapping

- `/` -> `/api/landing/overview`
- `/about` -> `/api/about`
- `/methodology` -> `/api/methodology`
- `/contact` -> `/api/contact` (+ POST)
- `/execute` -> `/api/execute`
- `/terminal/macro-desk` -> `/api/macro/all`
- `/terminal/alpha-factory` -> `/api/alpha/all`, `/api/alpha/shap/{ticker}`
- `/terminal/risk-desk` -> `/api/risk/all`, `/api/risk/dendrogram`
- `/terminal/backtest` -> `/api/backtest/latest`
- `/terminal/execution` -> `/api/execution/all`, `/api/execution/order`, `/api/execution/capacity`
- `/terminal/portfolio` -> `/api/optimizer/current`, `/api/optimizer/solve`
- `/terminal/agent` -> `/api/metrics/snapshot`, `/api/agent/query`, `/api/agent/stream/ws`

## 6. Environment Configuration

### 6.1 Backend env vars (`AI-backend/.env`)

- `APP_ENV` (default `dev`)
- `HOST` (default `0.0.0.0`)
- `PORT` (default `8000`)
- `HISTORICAL_DATA` (`true`/`false`)
- `SP500_DATA_DIR` (optional)
- `MODEL_DATA_DIR` (optional)
- `TICKER_MAPPING_FILE` (optional)
- `ALLOW_ORIGINS` (comma-separated origins)
- `MAX_UNIVERSE_SIZE`
- `DEFAULT_USER_INITIALS`
- `BASE_NOTIONAL_USD`

### 6.2 Frontend env vars (`frontend/.env.local`)

- `HIVE_BACKEND_URL` (proxy target base URL)
- `NEXT_PUBLIC_HIVE_PROXY_PREFIX` (default `/api/hive`)
- `NEXT_PUBLIC_HIVE_WS_BASE` (optional explicit ws/wss base, example `ws://localhost:8000`)

If `NEXT_PUBLIC_HIVE_WS_BASE` is not set, frontend derives WS base from backend URL.

## 7. Local Development

### 7.1 Start backend

```powershell
cd AI-backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7.2 Start frontend

```powershell
cd frontend
npm install
npm run dev
```

### 7.3 Verify

- Frontend app: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/api/health`
- System status through proxy: `http://localhost:3000/api/hive/system/status`
- Unified snapshot: `http://localhost:8000/api/metrics/snapshot`

## 8. Quality Checks

### 8.1 Frontend

```powershell
cd frontend
npm run lint
npm run build
```

### 8.2 Backend

```powershell
cd AI-backend
python -m compileall app
python -c "from app.main import app; print(bool(app))"
```

Optional endpoint smoke checks can be run from `/docs` or with a script using FastAPI `TestClient`.

## 9. Data Assets and Dependencies

`BTP/` is the local research/artifact dependency used by backend services.

- `BTP/sp500`: historical ticker OHLCV CSVs
- `BTP/models_p3_metaquant`: model metadata, diagnostics, performance, weights logs
- `BTP/extra_data`: ticker/company mapping

Live mode (`HISTORICAL_DATA=false`) uses:

- Yahoo Finance via `yfinance` (quotes/candles)
- CoinGecko public API (aggregate 24h volume)

Backend automatically falls back to historical sources when live requests fail.

## 10. State and Persistence Notes

- Ledger state is process-local and in-memory (resets on backend restart)
- Optimizer jobs are in-memory (resets on backend restart)
- Agent worker stream is in-memory and bounded

For persistent production execution, move ledger and job state into durable storage.

## 11. Troubleshooting

### 11.1 `502` from `/api/hive/*`

Usually means frontend proxy cannot reach backend.

Checklist:

1. Confirm backend server is running on `HIVE_BACKEND_URL`
2. Check backend health endpoint directly
3. Verify `.env.local` values and restart frontend dev server

### 11.2 WebSocket not connecting

Checklist:

1. Confirm backend is reachable at ws/wss URL
2. Set `NEXT_PUBLIC_HIVE_WS_BASE` explicitly if reverse proxying
3. Verify CORS/network rules for backend host

### 11.3 Maximum update depth exceeded (frontend)

If seen after pulling updates:

1. Stop dev servers
2. Restart backend + frontend
3. Hard refresh browser to clear stale client bundle

### 11.4 Live mode instability

If external APIs rate-limit or fail, keep `HISTORICAL_DATA=true` for deterministic runs.

## 12. Additional Docs

- `frontend/README.md`
- `AI-backend/README.md`
- `frontend/metrics.md` (contract reference)
