# 🏛️ Project Blueprint: The Meta-Quant Trading System
**Version:** 2.0 (The Institutional Pivot)
**Core Philosophy:** *Feature Engineering > Complex Architectures. Risk Management > Return Chasing. Ensembles > Monoliths. Glass Box > Black Box.*

## Executive Summary: The Institutional Pivot
Academic deep learning (predicting exact prices using LSTMs/Transformers on raw OHLCV data) fails in live markets due to an overwhelmingly low signal-to-noise ratio. To win, we are adopting the strategies of International Quant Olympiad winners and elite prop shops:
1.  **Cross-Sectional Ranking:** We predict relative outperformance, not absolute price.
2.  **Meta-Labeling:** We separate the "Signal" (Alpha model) from the "Bet Sizing" (Meta-model).
3.  **Hierarchical Risk Parity (HRP):** We abandon the fragile Modern Portfolio Theory (MPT) in favor of machine-learning-driven risk clustering.
4.  **Agentic Overlay:** We use a Small Language Model (SLM) strictly as a translation layer to convert complex math into human-readable institutional briefs.

---

## Phase 1: The Research & Data Foundation (Layer 1)
*We cannot build a robust model on fragile data. This phase establishes our "Quant Sandbox."*

*   **The Industry Standard:** Quants spend 80% of their time cleaning data. Prices must be adjusted for splits and dividends to calculate true returns. Databases must support fast, vectorized time-series queries.
*   **Our Architecture:**
    *   **Storage:** PostgreSQL with the **TimescaleDB** extension (or purely local `.parquet` files for rapid prototyping).
    *   **Data Universe:** S&P 500 and NIFTY 50 (to test across different market microstructures).
    *   **Vectorization Engine:** `Pandas` and `NumPy` for all transformations. NO `for` loops in time-series processing.
*   **🧪 Experimentation Zone:**
    *   Evaluate data ingestion APIs (Yahoo Finance vs. Alpha Vantage vs. custom scrapers).
    *   Test handling of survivorship bias (how do we handle stocks that fell out of the S&P 500?).

## Phase 2: The Alpha Factory (Feature Engineering & Selection)
*Feeding raw prices to a model is a rookie mistake. We must transform data into stationary, uncorrelated signals.*

*   **The Industry Standard:** Hedge funds use hundreds of weak signals. They evaluate them using the Information Coefficient (IC) and orthogonalize them to prevent multicollinearity.
*   **Our Architecture:**
    *   **Feature Classes to Generate:**
        1.  *Cross-Sectional Momentum:* (Stock's 30-day return) minus (Sector's 30-day mean return).
        2.  *Volatility Ratios:* 10-day realized volatility / 60-day realized volatility.
        3.  *Microstructure Proxies:* Bid-ask bounce approximations, volume-weighted price trends.
    *   **Feature Selection Pipeline:**
        *   Calculate the **Rank IC (Spearman Correlation)** between the feature and the Forward 5-Day Return.
        *   **Orthogonalization:** Use Principal Component Analysis (PCA) or Gram-Schmidt to strip out overlapping information between highly correlated features.
*   **🧪 Experimentation Zone:**
    *   Build a pipeline that generates 100+ features and automatically drops those with a Rolling Rank IC below a specific threshold (e.g., 0.02).
    *   Test different time horizons for feature lookbacks (e.g., 10-day vs 20-day vs 50-day momentum).

## Phase 3: The Meta-Quant Engine (Machine Learning Layer)
*This is the core paradigm shift. We use multiple specialized models, applying the Lopez de Prado Meta-Labeling framework.*

### Step 3A: The "Actors" (Primary Alpha Models)
*   **The Industry Standard:** Gradient Boosting Trees (LightGBM, XGBoost, CatBoost) are the undisputed kings of tabular financial data because they naturally handle non-linearities and are robust to outliers.
*   **Our Architecture:**
    *   **Target Variable:** Forward 5-Day Cross-Sectional Rank (Decile 1 to 10).
    *   **Models:** An ensemble of **LightGBM** models, each trained on distinct feature subsets (e.g., one model trained only on momentum, another only on mean-reversion).
    *   **Output:** A raw continuous signal [-1.0 to 1.0] indicating directional conviction.

### Step 3B: The "Critic" (Meta-Labeling Model)
*   **The Industry Standard:** Don't let the Alpha model size the bet. Train a secondary model to learn when the primary model is wrong.
*   **Our Architecture:**
    *   **Labeling (The Triple-Barrier Method):**
        *   Calculate a stock's rolling daily volatility ($\sigma$).
        *   Set dynamic barriers: Upper Profit (e.g., $+1.5\sigma$), Lower Stop-Loss (e.g., $-1.0\sigma$), Vertical Time Limit (e.g., 5 days).
        *   Simulate the Primary Actor's trade. If it hits the Upper Barrier first, label = `1` (Success). Otherwise, label = `0` (Failure).
    *   **The Meta-Model:** A Random Forest or highly regularized Logistic Regression.
    *   **Input:** The Actor's Signal + Current Market Volatility + Macro Indicators.
    *   **Output:** The Probability of Success `P(Success)`.

### Step 3C: Regime Detection
*   **The Industry Standard:** Markets have distinct states (Bull, Bear, Sideways). Models must know the current state.
*   **Our Architecture:** An unsupervised **Hidden Markov Model (HMM)** or Gaussian Mixture Model (GMM) trained on the VIX (Volatility Index) and broad market returns to output the current Regime State (0, 1, or 2).
*   **🧪 Experimentation Zone:**
    *   Test different LightGBM hyperparameter optimization methods (Optuna).
    *   Test different Triple-Barrier multipliers (e.g., is a $2\sigma$ profit target better than $1.5\sigma$ for training the Meta-Model?).

## Phase 4: Advanced Portfolio Construction (Layer 4)
*How we turn probabilities into dollar allocations without blowing up the account.*

*   **The Industry Standard:** Modern Portfolio Theory (MPT) is dead due to its reliance on normal distributions and inverted covariance matrices. Hierarchical Risk Parity (HRP) is the modern standard.
*   **Our Architecture:**
    1.  **Distance Metric:** Convert the correlation matrix ($\rho$) of the top predicted stocks into a distance matrix: $D = \sqrt{0.5 \times (1 - \rho)}$.
    2.  **Hierarchical Clustering:** Group the stocks into a tree (Dendrogram).
    3.  **Quasi-Diagonalization:** Reorder the covariance matrix so similar investments are grouped.
    4.  **Recursive Bisection:** Allocate capital inversely proportional to cluster variance.
    5.  **Kelly Sizing:** Scale the final HRP weights by the Confidence Score `P(Success)` generated by our Meta-Model.
*   **🧪 Experimentation Zone:**
    *   Test clustering algorithms for HRP: **Ward's Method** (minimizes variance) vs. **Complete Linkage**.
    *   Run Monte Carlo simulations (like in your Phase 1) comparing the Max Drawdown of HRP vs. MPT during the 2008 and 2020 crashes.

## Phase 5: MLOps & Continuous Learning
*Markets are non-stationary. The model must breathe and evolve.*

*   **The Industry Standard:** Models are constantly retrained as new data arrives to combat "concept drift."
*   **Our Architecture:**
    *   **Walk-Forward Validation:** Strict embargoing of data. Train on years 1-5, test on year 6. Slide the window. No random K-Fold cross-validation (which leaks future data in time-series).
    *   **Incremental Learning:** Every week, feed the new week's actual returns into the LightGBM models using the `init_model` parameter to gently update the trees without retraining from scratch.
*   **🧪 Experimentation Zone:**
    *   Determine the optimal retraining frequency (Weekly vs. Monthly).

## Phase 6: The Agentic Analyst & Institutional UI
*The "Glass Box" presentation layer.*

*   **Our Architecture:**
    *   **The Engine Backend:** **FastAPI** (Python). Asynchronous, high-performance, hosts the LightGBM, HMM, and HRP pipelines.
    *   **The UI:** **Next.js + Tailwind CSS + Tremor.so**. Institutional dark mode, monospaced data tables, high density.
    *   **The "Fin-OSS" Agent:** A Small Language Model (e.g., Llama-3-8B) accessed via API, constrained by LangChain. It is given Python "Tools" to read the HMM state and HRP weights, generating a human-readable daily market brief.
    *   **Interpretability (Crucial for the Panel):** Implement **SHAP (SHapley Additive exPlanations)**. Next to every stock recommendation in the UI, display a mini-bar chart showing exactly *which* features (e.g., momentum, volatility) drove the LightGBM's decision. This proves it is not a black box.

---

### 🚀 Immediate Next Steps for the Team:
1.  **Data Engineer:** Set up the Postgres/TimescaleDB environment and write the robust OHLCV ingestion scripts (adjusted for splits/dividends). We will do this at a later pint of time.
2.  **Quant Researcher 1:** Build the Feature Factory. Write the scripts to generate the technical features and the code to calculate the Rolling Rank IC.
3.  **Quant Researcher 2:** Build the Triple-Barrier labeling function and begin training the baseline LightGBM "Actor" model.
4.  **Frontend/Full-Stack Engineer:** Spin up the Next.js/Tremor repository and build the skeleton for the 4 Desks (Macro Regime, Alpha Factory, Risk Portfolio, Agent Feed).