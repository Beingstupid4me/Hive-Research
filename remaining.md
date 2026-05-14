**The Verdict:** We will use postgres from docker image to keep it light and clean.
---

## 🚀 What Remains? (The Final 10% to God-Tier)

Excluding the database and authentication, your core architecture is built. Here is exactly what is left to turn this from a "beautiful interface" into a "fully functioning automated fund."

#### 1. The True Agentic Brain (Replacing the Mocked LLM)
Your README outlines `/api/agent/stream/ws` and `agent_service.py`. Right now, it's likely streaming pre-written text or doing basic LLM calls.
*   **What's Left:** You need to implement **Actual Tool Use** using a framework like `LangChain` or `LlamaIndex`. 
*   **The Implementation:** You must give your LLM (Gemini/Llama3) strict access to your internal FastAPI functions. 
    *   *Tool 1:* `get_current_regime()`
    *   *Tool 2:* `get_top_alpha_rankings()`
    *   *Tool 3:* `get_portfolio_weights()`
*   When a user types *"Why are we holding so much defensive utility stock?"*, the Agent should autonomously trigger Tool 1 and Tool 3, realize the HMM regime is "Bear/High Volatility," and generate a live, mathematically accurate response.

#### 2. Live Paper Trading Broker Integration (The Ultimate Flex)
You have a brilliant local simulated ledger with transaction costs and slippage. But it's still local.
*   **What's Left:** Integrate a free Paper Trading API like **Alpaca** or **Interactive Brokers (TWS API)**. 
*   **The Implementation:** Add a toggle in your UI: `[ ] Local Simulated Execution | [x] Live Paper Execution`. When the optimizer generates rebalance deltas (e.g., "Buy 15 shares of MSFT"), your FastAPI backend pushes those exact market orders to the Alpaca API. Showing the panel your UI placing a *real* (paper) trade on a live exchange based on your Meta-Labeling logic is an instant A+.

#### 3. Dynamic Backtest Parameterization (Moving Beyond Static Artifacts)
Your `/api/backtest/latest` currently serves the artifacts from your Jupyter notebooks (`BTP/models_p3_metaquant`). This is great for a static view, but limits interactivity.
*   **What's Left:** Allow the user to change parameters dynamically from the Next.js UI and trigger a fast, in-memory backtest.
*   **The Implementation:** In the UI, add inputs for "Kelly Fraction Multiplier" (e.g., 0.5 to 1.0) and "Max Sector Weight" (e.g., 15%). When the user clicks "Run Backtest", FastAPI takes those parameters, runs the historical array through your vectorizer, and returns a brand new equity curve and Sharpe Ratio on the fly. 

#### 4. The MLOps "Continual Learning" Trigger (Cron / Orchestration)
Right now, your models are static `.pkl` files. A real quantitative system must update itself.
*   **What's Left:** You need a background task orchestrator.
*   **The Implementation:** Write a simple Python script using `APScheduler` or `Celery` inside your FastAPI app. 
    *   Every Friday at 5:00 PM, the script fetches the week's new OHLCV data.
    *   It checks the **Rolling 30-Day Rank IC**. 
    *   If the IC has dropped below `0.02` (Model Drift), it automatically triggers the LightGBM `init_model` incremental training loop to update the trees with the newest market data, saves the new `.pkl` file, and seamlessly reloads it into FastAPI memory.

### Summary of Your Next Steps

You have built the ultimate "chassis." It looks like a million bucks. 
1.  **Wire up LangChain/LlamaIndex** to your FastAPI endpoints so the Agent actually "thinks" using your data.
2.  **Set up the MLOps cron job** to prove the system can update itself over time.
