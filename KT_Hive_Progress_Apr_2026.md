# Hive Project Knowledge Transfer (KT)

Date: 2026-04-21
Scope: Complete handover of work done so far across research, backend, and frontend.

---

## 1. Executive Summary

You have completed a substantial end-to-end quantitative platform foundation with:

- Multi-phase quant research (NIFTY50 -> S&P500 -> Meta-Quant pipeline).
- A production-structured FastAPI backend consuming research artifacts.
- A Next.js frontend with terminal-style desks wired to backend routes via proxy.
- Fallback-safe operation in both historical and live-data modes.

Current state is not a prototype-only notebook effort; it is a deployable architecture with a working contract between model artifacts, APIs, and UI.

---

## 2. Repository-Level Work Breakdown

## 2.1 Top-Level Tracks

- `BTP/`: Research and model development pipeline.
- `AI-backend/`: FastAPI service layer exposing quant outputs.
- `frontend/`: Next.js UI and terminal desks.
- Root docs (`README.md`, `Roadmap.md`, `remaining.md`): Product direction, architecture, and pending items.

## 2.2 Product Vision Work Already Captured

From roadmap and product docs:

- 3-pillar product concept is defined:
  - Marketplace (objective market view)
  - Personal Place (portfolio state)
  - Future Dreams (AI forecasting + reasoning)
- Tri-service architecture has been laid out and partially implemented:
  - Frontend (renderer)
  - AI backend (compute + quant surfaces)
  - Orchestrator/service boundary planning (future expansion)

---

## 3. Detailed Chronological KT (What Was Built, Step by Step)

## 3.1 Phase 1: NIFTY50 Foundation (Completed)

### Step 1: Data Collection and EDA

Work done:

- NIFTY50 historical data scraping and ingestion.
- EDA notebooks created (`nifty50_Set/data_collection.ipynb`, `nifty50_Set/data_exploration.ipynb`).
- Preprocessing, cleaning, normalization, and validation performed.

Outcome:

- Clean training-ready dataset for multi-model benchmarking.

### Step 2: Daily Price Prediction Benchmarking

Models trained and evaluated:

1. Linear Regression
2. ARIMA
3. BiLSTM
4. LSTM
5. CNN-LSTM
6. RNN
7. Random Forest
8. LightGBM
9. BiLSTM-LightGBM
10. SVM

Documented findings:

- Linear Regression / ARIMA / BiLSTM gave strongest results among this set.
- Tree models and SVM underperformed for direct price forecasting.

### Step 3: Return-Based Reformulation

Why this step happened:

- Shifted focus from predicting absolute price to predicting returns/direction (more actionable for trading).

Models tested for returns/log-returns:

- ARIMA
- Linear Regression
- Random Forest
- XGBoost

Observed behavior:

- ARIMA emerged as best among tested return models.
- Directional accuracy plateau around mid-50% range.

### Step 4: Cross-Market Generalization Test

Work done:

- NIFTY-trained logic tested on US names (AAPL, GOOGL).

Outcome:

- Directional behavior remained in similar range (~53-54%), indicating limited but non-random transferable structure.

---

## 3.2 Phase 2: S&P500 + Portfolio Research (Completed)

### Step 1: S&P500 Data Foundation

Work done:

- Built S&P500 historical universe dataset (`BTP/sp500/*.csv`).
- Created mapping metadata (`BTP/extra_data/ticker_to_company_mapping.csv/json`).

Outcome:

- Scalable cross-sectional universe for portfolio research and service integration.

### Step 2: Baseline Modeling + Initial Portfolio Construction

Work done:

- Multiple model variants benchmarked per company.
- Early portfolio generation with MPT and related optimization variants.

### Step 3: Simulation-Driven Portfolio Strategy Comparison

Work done:

- Large simulation campaign (10,000 Monte Carlo in phase docs).
- Compared multiple portfolio optimization strategies under risk metrics.

Outcome:

- Strategy rankings and robustness characteristics documented.

---

## 3.3 Phase 3: Meta-Quant Pipeline (Implemented and Artifacted)

Pipeline notebooks:

1. `01_feature_factory.ipynb`
2. `02_alpha_models.ipynb`
3. `03_meta_labeling.ipynb`
4. `04_regime_detection.ipynb`
5. `05_hrp_portfolio.ipynb`
6. `06_full_pipeline_backtest.ipynb`

### Step 1: Feature Factory (`01_feature_factory.ipynb`)

Core work completed:

- Feature engineering panel creation (`features_panel.parquet`).
- IC analysis and feature filtering (`feature_ic_summary.csv`).
- Feature metadata export (`feature_meta.json`).
- Dimensionality tools persisted (`scaler.pkl`, `pca.pkl`).

Key configuration from artifacts:

- Study period: 2010-01-01 to 2022-12-31.
- Forward horizon: 5 days.
- IC threshold: 0.02.
- Selected features: 45.
- PCA components: 20.
- Scaler: StandardScaler.

Representative selected feature families:

- Momentum: `mom_5`, `mom_10`, `mom_21`, `mom_63`, `mom_126`, `mom_252`.
- Volatility: `vol_5`, `vol_10`, `vol_21`, `vol_63`, volume/volatility ratios.
- Technicals: RSI, MACD, Bollinger stats, MA ratios, ATR-normalized range.
- Cross-sectional variants: `xs_rank_*`, `xs_z_*`.

### Step 2: Alpha Model Stack (`02_alpha_models.ipynb`)

Models built:

- `model_lgb_momentum.pkl`
- `model_lgb_volatility.pkl`
- `model_lgb_technical.pkl`
- `model_lgb_combined.pkl`
- Ensemble output (`pred_ensemble`)

Training setup captured:

- Walk-forward style folds: 5.
- Train/Test split regime per fold: 4 years train, 1 year test.
- Embargo days: 10.
- Hyperparameter tuning: Optuna (200 trials).

Registered model package:

- `model_registry.json` with version `02-alpha-lgb-ensemble-v1`.
- Feature-group composition:
  - Momentum: 22 features
  - Volatility: 16 features
  - Technical: 7 features
  - Combined: 45 features

Performance artifact (`alpha_model_performance.csv`):

- `pred_lgb_combined` is best standalone model in this table (Sharpe 1.954, Annual Return 54.64%, Max Drawdown -35.33%).
- Ensemble (`pred_ensemble`) shows balanced but lower than combined in return terms.

### Step 3: Meta-Labeling Layer (`03_meta_labeling.ipynb`)

Work completed:

- Meta model artifact: `meta_model.pkl` (+ `meta_scaler.pkl`).
- Success-probability output: `p_success.parquet`.
- Meta diagnostics persisted in `meta_model_meta.json`.

Meta model details captured:

- Type: Logistic Regression (per metadata).
- Decision threshold: `p_success_threshold = 0.55`.
- Vertical barrier: 5.
- Volatility window: 21.
- Stored metrics: test AUC and Brier score.

Note on doc mismatch:

- `final_model_registry.json` mentions "Calibrated Random Forest" in one section, but `meta_model_meta.json` records logistic regression. Latest artifact-level truth appears to be logistic regression.

### Step 4: Regime Detection (`04_regime_detection.ipynb`)

Work completed:

- Regime artifacts: `hmm_model.pkl`, `hmm_scaler.pkl`, `gmm_model.pkl`, `regime_states.parquet`.
- Regime metadata: `regime_meta.json`.

Modeling details:

- Primary regime model: Gaussian HMM.
- Number of regimes: 3.
- Regime names mapped: Bull / Transition / Bear.
- Regime feature set includes rolling vol/return, dispersion, drawdown.
- GMM comparison included (`gmm_bic_optimal_n` recorded).

### Step 5: Portfolio Construction (`05_hrp_portfolio.ipynb`)

Work completed:

- Portfolio method built: HRP + Meta filter + Kelly scaling + regime leverage.
- Portfolio logs and summaries exported (`weights_log.csv`, `portfolio_performance_comparison.csv`).
- Dashboard and comparison plots generated.

Portfolio controls encoded:

- Rebalance cadence: 5 days (from final registry).
- Max position cap: 15%.
- Transaction cost assumption: 5 bps one-way.

### Step 6: End-to-End Backtest (`06_full_pipeline_backtest.ipynb`)

Work completed:

- Full stitched pipeline backtest and OOS diagnostics.
- Registry finalization in `final_model_registry.json`.
- Additional diagnostics: Monte Carlo Sharpe distribution, equity curves, stability visuals.

Key OOS snapshot in final registry:

- Sharpe: ~0.697
- Annual return: ~14.44%
- Annual vol: ~20.74%
- Max drawdown: ~-23.30%
- Win rate: ~54.03%

---

## 4. Models Inventory (Complete)

## 4.1 Research Model Families Built So Far

Classical/statistical:

- Linear Regression
- ARIMA

Deep learning:

- RNN
- LSTM
- BiLSTM
- CNN-LSTM

Tree/boosting:

- Random Forest
- LightGBM
- XGBoost

Hybrid/ensemble:

- BiLSTM-LightGBM
- LightGBM specialist ensemble (momentum, volatility, technical, combined, ensemble)

Meta and market-state:

- Meta-labeling classifier (logistic regression artifact)
- Gaussian HMM regime model
- GMM comparison model

Portfolio/risk layer:

- HRP portfolio allocator
- Half-Kelly sizing + regime-based leverage
- MPT / Robust / Stochastic comparisons (research stage)

## 4.2 Planned/Concept Models vs Current Production Artifacts

Planned in product roadmap:

- MS-DAN as future core forecasting model.
- Fin-R1 as future reasoning model.

Current implemented production-facing stack:

- LightGBM ensemble + meta-labeling + HMM regime + HRP/Kelly in artifact pipeline.
- Agent output is currently template/heuristic backed, not yet tool-using autonomous LLM agent.

---

## 5. How Models Are Used Today (Operational Flow)

This is the current real usage path from artifacts to UI:

1. Data/artifacts are read by backend repositories.
2. Service-layer computes desk payloads.
3. API routes expose each payload.
4. Frontend calls routes via `/api/hive/*` proxy.
5. If request fails, typed fallback payloads keep screens live.

## 5.1 Artifact Ingestion

`ArtifactRepository` loads:

- `feature_ic_summary.csv`
- `alpha_model_performance.csv`
- `portfolio_performance_comparison.csv`
- `weights_log.csv`
- `model_registry.json`
- `final_model_registry.json`
- `feature_meta.json`
- `fold_params.json`
- `regime_meta.json`
- `meta_model_meta.json`

## 5.2 Alpha Desk Runtime Usage

How backend uses models/artifacts in practice:

- Uses S&P500 historical bars to compute cross-sectional alpha score proxy (`ret_63 / vol_30d`).
- Uses feature IC file to choose and display top drivers.
- Uses model performance file to populate long/short return stats.
- Uses final registry diagnostics to compute confidence/health/IC metadata.
- Provides SHAP-style per-ticker explanation payload using top features.

Frontend usage:

- `/alpha/all`, `/alpha/shap/{ticker}`, `/alpha/rolling-ic`, etc.
- Renders rankings, feature bars, rolling IC warning state, and execution log.

## 5.3 Macro Desk Runtime Usage

How backend uses artifacts:

- Reads `weights_log.csv` regime sequence and computes transition matrix.
- Reads `regime_meta.json` for regime volatility context and latent factors.
- Builds regime history + transition event stream.
- In live mode, enriches with external quotes (`^VIX`, etc.); otherwise historical proxies.

Frontend usage:

- `/macro/all` for state probabilities, transitions, latent factors, cross-asset context.

## 5.4 Risk Desk Runtime Usage

How backend uses artifacts:

- Parses top holdings from latest `weights_log.csv` row.
- Buckets holdings into sectors/clusters.
- Computes diversification and risk contribution estimates.
- Uses `portfolio_performance_comparison.csv` to anchor expected vol/status.
- Creates dendrogram graph payload for HRP visualization.

Frontend usage:

- `/risk/all`, `/risk/clusters`, `/risk/dendrogram`, `/risk/orders`.

## 5.5 Backtest Runtime Usage

How backend uses artifacts:

- Builds return matrix from S&P500 close history.
- Uses leverage path from `weights_log.csv` to modulate strategy returns.
- Uses registry target annual return for edge alignment.
- Uses fold params from `fold_params.json` for model-parameter disclosure in payload.

Frontend usage:

- `/backtest/{run_id}` used for equity curve, trade table, KPI panels.

## 5.6 Optimizer Runtime Usage

How backend works currently:

- Pulls top long candidates from alpha rankings.
- Runs Monte Carlo dirichlet weight sampling under constraints:
  - target return
  - volatility cap
  - max asset weight
- Selects max-Sharpe feasible point and outputs frontier + rebalance deltas.

Frontend/API usage:

- `/optimizer/solve`, `/optimizer/current`, `/optimizer/{job_id}`.

## 5.7 Execution Runtime Usage

How backend works:

- Simulated ledger with seeded orders and holdings.
- Transaction cost fixed at 5 bps.
- Slippage modeled from participation rate vs ADV notional.
- Capacity projection degrades expected return and Sharpe as AUM and slippage rise.

Frontend/API usage:

- `/execution/book`, `/execution/candles`, `/execution/order`, `/execution/capacity`, `/execution/all`.

## 5.8 Agent Runtime Usage

How backend works currently:

- Builds daily brief from macro + alpha + risk summaries.
- Supports token streaming over WebSocket (`/api/agent/stream/ws`).
- Query response currently rule/keyword-based recommendation logic.

Frontend usage:

- Worker stream and tokenized brief rendering in agent desk.

---

## 6. Data Modes and Provider Strategy

The backend supports two data modes:

- Historical mode (`HISTORICAL_DATA=true`): reads local S&P500 CSVs and model artifacts.
- Live mode (`HISTORICAL_DATA=false`): attempts Yahoo/CoinGecko; falls back to historical provider if needed.

Fallback proxy ticker mapping exists for non-equity symbols in historical fallback mode:

- `^GSPC -> AAPL`
- `DX-Y.NYB -> JPM`
- `GC=F -> JNJ`
- `^VIX -> XOM`

This prevents service breaks when non-equity symbols are requested but only equity CSVs exist.

---

## 7. Frontend Implementation Status

## 7.1 Route and Contract Layer

- Frontend proxies all API calls through `src/app/api/hive/[...path]/route.ts`.
- Shared API clients in `src/lib/api/http.ts` and `src/lib/api/server.ts`.
- Strongly typed fallback payloads in `src/lib/api/fallbacks.ts` keep pages rendering during backend downtime.

## 7.2 Implemented Terminal Surfaces

Terminal routes present:

- `/terminal/macro-desk`
- `/terminal/alpha-factory`
- `/terminal/risk-desk`
- `/terminal/backtest`
- `/terminal/execution`
- `/terminal/portfolio`
- `/terminal/agent`
- `/terminal/settings` (in-progress target route exists)

Implemented behavior already seen in code:

- 30s polling for key desk payloads.
- Fallback warning banners when data comes from local fallback object.
- Feature-rich visualization per desk (charts/tables/logs/shap/regime matrix/dendrograms).

---

## 8. Final Registry Snapshot (Current Pipeline Version)

`final_model_registry.json` records:

- Version: `2.0.0`
- Study period: 2014-03-07 to 2019-01-23
- Pipeline sequence: notebooks 01-05 (backtest in notebook 06)
- Portfolio method: HRP + Half-Kelly + Regime Leverage
- Rebalance: every 5 days
- Max position: 15%
- Cost assumption: 5 bps one-way
- Monte Carlo robustness diagnostics included

---

## 9. What Is Complete vs What Is Pending

## 9.1 Completed

- Full quant research lifecycle from EDA to OOS backtest artifacts.
- Multi-model experimentation and selection workflow.
- Production-ready artifact packaging.
- Backend service decomposition and endpoint exposure.
- Frontend terminal desks integrated to backend contract.
- Historical/live mode + fallback resiliency.

## 9.2 Pending (from your own `remaining.md` and architecture intent)

- Agentic tool-use LLM orchestration (not just templated/query-rules).
- Real paper broker integration toggle (Alpaca/IBKR).
- User-parameterized dynamic backtest from UI.
- Automated retraining/drift-triggered update loop.
- Database/auth stack (intentionally deferred in current phase).

---

## 10. Suggested KT Handover Walkthrough Script (For Team/Panel)

Use this sequence to present your completed work clearly:

1. Explain 3-phase research progression (NIFTY50 -> S&P500 -> Meta-Quant).
2. Show model evolution and why return/ranking/regime became core.
3. Walk notebook pipeline 01-06 and artifact outputs.
4. Open `final_model_registry.json` and summarize OOS metrics.
5. Show how backend repositories load these artifacts.
6. Show service-to-route mapping (`alpha`, `macro`, `risk`, `execution`, `optimizer`, `backtest`, `agent`).
7. Demo frontend desks pulling `/api/hive/*` with fallback resilience.
8. Conclude with pending items as explicit roadmap, not gaps.

---

## 11. Short Technical Truth Statement (Current System Reality)

Hive currently runs as a robust quant platform with real research artifacts in production-style APIs. It is already beyond a notebook-only setup. The next phase is not building from scratch; it is replacing specific simulated components (agent reasoning, paper broker routing, auto-retraining) with live operational intelligence while preserving the existing architecture.
