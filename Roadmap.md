
# Product Blueprint: AI-Powered Portfolio SaaS

## 1. Product Vision: The "Three Pillars" Experience
We are building a consumer-facing financial platform. Unlike standard brokers that only show what *has* happened, our platform focuses on what *will* happen. The user journey is divided into three distinct zones:

### Pillar 1: The Marketplace (The Objective Reality)
*   **What it is:** A standard, high-quality market overview similar to TradingView or Robinhood.
*   **Key Features:**
    *   Searchable dashboard of global assets (Stocks, Crypto, Indices).
    *   Real-time or near real-time market data (Price, Volume, Order Depth).
    *   News aggregation and sentiment indicators.
*   **Data Source:** Integration with external APIs (e.g., Yahoo Finance, AlphaVantage) via the Node.js backend.

### Pillar 2: The Personal Place (The User Reality)
*   **What it is:** The user’s specific footprint in the market.
*   **Key Features:**
    *   **Portfolio Tracking:** Current holdings, P&L, and historical performance.
    *   **Exposure Analysis:** Visualizing risk (e.g., "You hold 60% in Tech stocks").
    *   **Action Center:** Where users execute decisions based on insights.

### Pillar 3: Future Dreams (The AI Reality)
*   **What it is:** The core USP. This is where we visualize our AI's intelligence.
*   **Key Features:**
    *   **Confidence Cones:** Instead of a single line chart, we render a probabilistic cone showing the 5th (Bear), 50th (Base), and 95th (Bull) percentile outcomes for the next 3-7 days.
    *   **The "Why" (Agentic Reasoning):** A text stream where an AI Agent explains the prediction (e.g., *"Technicals are strong, but upcoming Fed interest rate news increases risk"*).
    *   **Strategic Signals:** Buy/Sell/Hold recommendations with a confidence score.

---

## 2. The "Proxy" Development Strategy
**Crucial Note for the Team:** The core proprietary AI models (**MS-DAN** for statistics and **Fin-R1** for reasoning) are currently in deep R&D. **We will not wait for them.**

We will build the entire product using a **Simulator/Proxy approach**. The platform will be fully functional, but the "Brain" will be simulated initially. Later, we will perform a "Brain Transplant" to swap the simulators for the real models without breaking the frontend.

---

## 3. System Architecture: The Tri-Service Model

The system is decoupled into three separate services.

### Service A: The Frontend (The Product)
*   **Tech:** Modern JS Framework (e.g., Next.js).
*   **Role:** The "Dumb" Renderer. It does **zero** financial math. It simply visualizes the JSON data sent by the backend.
*   **Key Requirement:** It must handle real-time rendering of the "Confidence Cones" (shaded chart areas) and stream the Agent's text response to look like it is "thinking."

### Service B: The Orchestrator (Backend 1)
*   **Tech:** Node.js Environment.
*   **Role:** The Manager & Data Aggregator.
*   **Responsibilities:**
    *   **Daily Cron Job:** Runs every day at market close. It pulls real EOD data for all assets and sends it to the Python Service for processing.
    *   **The SSM (Structured State Map):** Manages the Database (PostgreSQL). It stores the "Daily Snapshot" of predictions.
    *   **User Management:** Auth, Portfolio storage.
    *   **API Gateway:** The only backend the Frontend talks to.

### Service C: The AI Core (Backend 2)
*   **Tech:** Python Environment.
*   **Role:** The Intelligence Engine (Currently in Simulator Mode).
*   **Responsibilities:**
    *   **Stateless Compute:** Receives a Ticker/Context, runs logic, returns JSON.
    *   **MS-DAN Simulator:** *Note: The real MS-DAN model is unfinished.* For now, this service will use basic math (Random Walk or simple LSTM) to generate "Mock Cones" that look like the final output.
    *   **Fin-R1 Simulator:** *Note: The real Fin-R1 model requires heavy GPUs we don't have yet.* For now, this service will wrap a public LLM API (like Gemini or GPT) to act as the "Agent" and generate reasoning text.

---

## 4. Data Strategy: The Structured State Map (SSM)

To keep the system fast and robust, we are avoiding complex Graph Databases for this phase. Instead, we use a Relational approach called the **Structured State Map**.

**The Workflow:**
1.  **Ingestion:** Node.js pulls real market data.
2.  **Processing:** Node.js sends this data to the Python Simulator.
3.  **Synthesis:** Python returns a structured JSON payload (The Forecast & Reasoning).
4.  **Storage:** Node.js saves this JSON into the Postgres Database.
5.  **Retrieval:** When a user logs in, Node.js serves the *stored* JSON instantly.

---

## 5. The API Contract (The "Bridge")
To allow the Frontend and Backend teams to work in parallel, we adhere to this strict JSON structure. The Python service must output this format, and the Frontend must expect it.

**The `Asset_State` Object:**

```json
{
  "ticker": "AAPL",
  "date": "2024-05-20",
  "current_price": 185.50,

  "market_context": {
    "volume": 72_000_000,
    "volatility_regime": "medium",
    "order_book_imbalance": 0.12,
    "spread": 0.03
  },

  "forecast": {
    "dates": ["2024-05-21", "2024-05-22", "2024-05-23"],
    "quantile_5": [184.00, 183.50, 182.00],
    "quantile_50": [186.00, 187.00, 188.50],
    "quantile_95": [188.00, 190.00, 192.00],
    "forecast_volatility": 0.22
  },

  "model_metadata": {
    "model_version": "ms-dan-v3.1",
    "model_timestamp": "2024-05-20T14:30:00Z",
    "data_freshness_sec": 12,
    "drift_score": 0.08
  },

  "agent_inference": {
    "signal": "BUY",
    "confidence": 0.85,
    "confidence_breakdown": {
      "model_confidence": 0.90,
      "macro_confidence": 0.80,
      "technical_confidence": 0.70,
      "ensemble_agreement": 0.88
    },
    "reasoning": "MS-DAN predicts a steady uptrend. Macro stable.",
    "macro_factors_considered": ["Inflation: Low", "Tech Sector: Bullish"]
  },

  "risk_context": {
    "current_position": "flat",
    "position_size": 0,
    "max_position_allowed": 0.15,
    "stop_loss": 178.00,
    "take_profit": 195.00,
    "risk_limit_hit": false
  },

  "events": {
    "upcoming_events": ["Earnings in 3 days"],
    "news_sentiment_score": 0.62,
    "news_sentiment_trend": "rising"
  }
}

```

---

## 6. Execution Roadmap

### Phase 1: The Shell & The Simulators
*   **Team Node:** Set up the Orchestrator, Database (SSM), and Yahoo Finance integration.
*   **Team Python:** Build the FastAPI service. Implement the "Mock MS-DAN" (randomized cones) and "Mock Fin-R1" (Gemini wrapper).
*   **Result:** A working API that returns "Real" prices but "Simulated" predictions.

### Phase 2: The Frontend Build
*   **Team Frontend:** Build the Dashboard.
*   **Focus:** Implement the Charting library to visualize the `quantile_5` to `quantile_95` area (The Cone). Make the Agent text look nice.
*   **Integration:** Connect to the Node API.

### Phase 3: The "Brain Transplant" (Future)
*   **Team Research:** Finish the actual MS-DAN model (`.pth` file) and the Fin-R1 model.
*   **Team Python:** Update the internal logic of the Python Service to load these models instead of the Simulators.
*   **Impact:** The Frontend and Node Backend **do not change**. The predictions just become real and accurate.