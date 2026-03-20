# **Project Blueprint: The Multi-Scale Decompositional Attention Network (MS-DAN) Quantitative System**

## **I. Guiding Philosophy & Core Principles**

This document outlines the architecture for a complete, end-to-end quantitative trading system. Its purpose is to move beyond simple point forecasting to a sophisticated, risk-aware probabilistic framework. The system is founded on three core principles:

1.  **Hierarchical Decomposition:** We believe financial time series are a composite of signals at different frequencies (long-term trends, mid-term cycles, and short-term noise). Our system will explicitly model these components separately to achieve a more robust understanding of market dynamics.

2.  **Separation of Concerns (State vs. Policy):** We will architecturally separate the task of understanding the market from the task of making a decision.
    *   **The Encoder (State Expert):** A deep learning model whose sole job is to process all available information and produce a rich, numerical representation of the current market "state."
    *   **The Policy Head (Decision Expert):** An interchangeable module that takes this "state" and translates it into an actionable forecast or trading decision. This modularity is our key to future-proofing the system.

3.  **Robustness over Overfitting:** Every design choice prioritizes stability, generalization, and risk management over chasing potentially spurious high scores on historical data. We will inject strong, financially-relevant inductive biases into our models and validate our strategy under realistic, friction-inclusive conditions.

---

## **II. The 6-Layer System Architecture**

The system is organized into six distinct, modular layers, from data ingestion to live adaptation.

## **Layer 1: The Data Foundation**

*   **Objective:** To create a centralized, clean, validated, and reliable source of market data.
*   **Data Sources:**
    *   **Primary:** Daily OHLCV (Open, High, Low, Close, Volume) data for our target universe (e.g., S&P 500 components).
    *   **Future Expansion:** The system will be designed to be asset-agnostic, allowing for the future integration of FX, futures, and crypto data.
*   **Data Integrity Pipeline:**
    1.  **Ingestion:** Automated scripts to download and update data from reliable sources.
    2.  **Cleaning:** Handle missing values, outlier detection, and zero-volume days.
    3.  **Adjustment:** Crucially adjust historical prices for stock splits and dividends to create a continuous series for accurate return calculation.
*   **Storage:** A high-performance, queryable format (e.g., Parquet files or a TimescaleDB instance) to ensure fast and efficient data retrieval.

## **Layer 2: The Signal Processing Engine**

*   **Objective:** To transform raw data into a rich set of predictive features and targets, while rigorously preventing any form of look-ahead bias.
*   **Core Feature Generation:**
    1.  **Technical & Statistical Indicators:** A comprehensive library of standard indicators (Momentum, Volatility, Mean-Reversion, etc.).
    2.  **GARCH Volatility Forecast:** A GARCH(1,1) model is fit on a rolling window of historical returns. The forecast for day `T` is generated using data only up to `T-1`. This provides our main model with a strong, pre-processed signal about statistically expected risk.
*   **Target Generation (Multi-Horizon):** We explicitly choose **Direct Forecasting** over the error-prone iterative "sand castle" approach. We pre-calculate our three primary prediction targets for every time step `T`:
    1.  `Return_T+1` (Short-Term)
    2.  `Return_T+5` (Mid-Term / Weekly)
    3.  `Return_T+30` (Long-Term / Monthly)
    *   **Note:** Returns will be calculated as log returns (`ln(Price_t / Price_t-1)`) for their desirable statistical properties (e.g., additivity).

## **Layer 3: The Predictive Engine (The "Brain")**

*   **Objective:** To implement our core "State Expert" (the MS-DAN Encoder) and our initial "Decision Expert" (the Probabilistic Policy Head).

*   **A. The Encoder (State Expert) Architecture: MS-DAN**
    *   **Input & Decomposition:** The primary price series is first decomposed into distinct streams: **Trend, Seasonality, and Residuals**. This allows us to apply a specialized encoder to each signal component.
    *   **Positional Information:**
        *   **Absolute Encoding:** A single, **shared** sinusoidal positional encoding is added to the inputs of **all three towers**. This provides a consistent, absolute "timestamp" for all components, which is critical for the LSTM and for the final fusion.
        *   **Relative Encoding:** The MHA-based towers use **T5-style Bucketed & Shared Relative Position Embeddings (RPEs)**. We choose this learnable, bucketed approach over a fixed one (like Alibi) because it allows the model to learn complex, non-linear temporal relationships (like seasonality) directly from the data in a highly scalable and parameter-efficient manner.
    *   **Parallel Encoder Towers (Heterogeneous Design):**
        1.  **Residual/Daily Tower:** `MHA (with T5 RPE) + Conv1D`. Specialist for high-frequency microstructure.
        2.  **Seasonality/Weekly Tower:** `Sparse MHA (with T5 RPE) + Conv1D`. Specialist for mid-term cyclical patterns.
        3.  **Trend/Monthly Tower:** `LSTM`. Specialist for long-term, auto-correlated trend memory.
    *   **Fusion Head:** Gated Residual Networks (GRNs) for conditioning on static features (e.g., stock ticker embeddings), followed by Cross-Attention and a final Self-Attention block to produce the final, rich **state vector**.

*   **B. The Policy Head (Decision Expert) Implementation:**
    *   **Initial Implementation (Probabilistic Forecasting):**
        *   **Architecture:** A **Multi-Horizon Mixture of Experts (MoE)-style Head**. It consists of three separate, parallel MLP branches that take the state vector as input, with each branch being an "expert" for a specific horizon (`T+1`, `T+5`, `T+30`).
        *   **Output:** Each expert head outputs a set of **quantiles** (e.g., 5th, 25th, 50th, 75th, 95th). This provides a full probabilistic forecast, not just a single point.
        *   **Training:** The entire system is trained end-to-end using the **Pinball Loss**. This loss function allows the model to learn to predict quantiles from single-point historical data by applying a controlled, asymmetric penalty.

## **Layer 4: Strategy & Portfolio Construction**

*   **Objective:** To translate the model's rich, probabilistic forecasts into a single, optimal, risk-managed portfolio.
*   **Signal Derivation (from the `T+30` quantile outputs):**
    1.  **Directional Forecast (Expected Return):** The median (50th percentile) quantile prediction.
    2.  **Volatility Forecast (Risk):** The width of the quantile range (e.g., the interquartile range: 75th - 25th percentile).
    3.  **Confidence Score:** The model's estimated probability of a positive return, derived from the full quantile distribution.
*   **Position Sizing:** We will use the **Kelly Criterion** as a guide. It uses the Confidence Score (as probability of success) and the quantile range (to estimate the win/loss ratio) to determine an optimal bet size for each asset. This will be capped to prevent over-concentration.
*   **Portfolio Optimization:** The final, sized positions are fed into a formal portfolio optimizer (e.g., Mean-Variance Optimization or Risk Parity). The optimizer's goal is to find the final portfolio weights that maximize expected return for a given level of risk, considering the correlations between assets.

## **Layer 5: Realistic Simulation**

*   **Objective:** To rigorously and honestly validate the entire end-to-end strategy under realistic market conditions.
*   **Framework:** An event-driven backtester (e.g., `Backtrader` or `Zipline`).
*   **Frictions:** The simulation **must** include realistic models for **transaction costs** and **price slippage**. Results without these are considered invalid.
*   **Methodology:** A rigorous **Walk-Forward Validation** will be the primary method.
    *   **Process:** Train the model on an initial "burn-in" period (e.g., 5 years). Test on the next year. Then, slide the window forward by one year and repeat. This simulates how the system would have performed in real life.
*   **Key Metrics:** Performance will be judged on risk-adjusted metrics, primarily the **Sharpe Ratio, Calmar Ratio, and Maximum Drawdown**.

## **Layer 6: Live Operations & Adaptation**

*   **Objective:** To safely deploy, monitor, and evolve the system over time in a live or paper-trading environment.
*   **Rebalancing vs. Prediction:** The MS-DAN model will generate predictions daily. However, the portfolio will be rebalanced on a slower, strategic cadence (e.g., monthly) based on the `T+30` forecast to minimize transaction costs and portfolio churn.
*   **Deployment Framework:** A **Champion/Challenger** system will be used. A newly retrained "Challenger" model is only promoted to the live "Champion" if it demonstrates a statistically significant improvement in a key metric on a held-out validation set.
*   **Monitoring & Alerting:** A live dashboard will track performance. Automated alerts will be triggered by **Model Drift** (a statistical degradation in predictive accuracy), signaling the need for investigation and potential retraining.
*   **Hyperparameter Tuning:** All model tuning will be performed using **Bayesian Optimization**, implemented with a modern framework like Optuna, to efficiently search the vast parameter space and leverage its trial-pruning capabilities.