
# Stock Price Prediction & Portfolio Optimization - Project Roadmap

## Executive Summary
A comprehensive ML-driven project combining time-series forecasting with modern portfolio optimization across Indian (NIFTY 50) and global (S&P 500) markets. This document details our journey from data acquisition through advanced portfolio strategies.

---

## Phase 1: NIFTY 50 Market Analysis (Completed)

### Step 1: Data Acquisition & EDA
- ✅ Web scraping NIFTY 50 historical data
- ✅ Exploratory data analysis and preprocessing
- ✅ Data cleaning, normalization, and validation

**Outcome**: Clean dataset ready for multi-model experimentation

### Step 2: Price Prediction Models (Daily Prices)
10 distinct models trained and evaluated:

| Model | MSE | RMSE | MAE | R² | MAPE | Dir. Accuracy |
|-------|-----|------|-----|-----|------|---------------|
| Linear Regression | 23,981 | 154.86 | 117.67 | 0.9854 | 0.66% | 57.52% |
| ARIMA | 24,491 | 156.50 | 118.18 | 0.9851 | 0.67% | 56.50% |
| BiLSTM | 24,831 | 157.58 | 118.94 | 0.9849 | 0.67% | 57.52% |
| LSTM | 25,652 | 160.16 | 121.31 | 0.9844 | 0.68% | 57.52% |
| CNN-LSTM | 31,221 | 176.70 | 135.02 | 0.9810 | 0.75% | 57.52% |
| RNN | 42,748 | 206.76 | 163.01 | 0.9740 | 0.89% | 57.52% |
| Random Forest | 664,783 | 815.34 | 489.12 | 0.5954 | 2.53% | 33.94% |
| LightGBM | 919,074 | 958.68 | 585.10 | 0.4406 | 3.02% | 17.28% |
| BiLSTM-LightGBM | 919,074 | 958.68 | 585.10 | 0.4406 | 3.02% | 17.28% |
| SVM | 91.6M | 9,570.81 | 9,474.59 | -54.75 | 52.17% | 42.48% |

**Key Findings**: 
- Classical models (Linear Regression, ARIMA) and BiLSTM outperformed tree-based and ensemble methods
- Deep learning showed marginal improvements over classical approaches
- Tree-based models struggled with continuous price sequences

### Step 3: Return-Based Modeling (Shift in Focus)
Recognized that predicting directional movement (returns) is more practical than absolute prices.

#### Percentage Return Models:
| Model | MSE | MAE | R² | Dir. Accuracy |
|-------|-----|-----|-----|---------------|
| ARIMA | 0.000079 | 0.006595 | 0.001157 | 55.58% |
| Linear Regression | 0.000079 | 0.006656 | -0.003413 | 54.36% |
| Random Forest | 0.000085 | 0.006912 | -0.081240 | 53.55% |
| XGBoost | 0.000089 | 0.007017 | -0.125899 | 52.74% |

#### Log Return Models:
| Model | MSE | MAE | R² | Dir. Accuracy |
|-------|-----|-----|-----|---------------|
| ARIMA | 0.000079 | 0.006597 | 0.001185 | 55.17% |
| Linear Regression | 0.000079 | 0.006653 | -0.003335 | 54.77% |
| Random Forest | 0.000084 | 0.006866 | -0.068333 | 54.36% |
| XGBoost | 0.000087 | 0.006986 | -0.107948 | 53.35% |

**Key Findings**: 
- ARIMA emerged as best performer for both return types
- Percentage returns marginally outperformed log returns
- Directional accuracy plateau around 55%, indicating market efficiency challenges

### Step 4: Cross-Market Validation
Tested NIFTY 50 models on external US stocks to assess generalization:

#### AAPL Testing:
| Model | MSE | MAE | R² | Dir. Accuracy |
|-------|-----|-----|-----|---------------|
| XGBoost | 0.000327 | 0.012896 | -0.005354 | **53.12%** |
| Linear Regression | 0.003039 | 0.051725 | -8.350330 | 52.64% |
| LightGBM | 0.000355 | 0.013669 | -0.093091 | 47.36% |

#### GOOGL Testing:
| Model | MSE | MAE | R² | Dir. Accuracy |
|-------|-----|-----|-----|---------------|
| Linear Regression | 0.003218 | 0.052784 | -7.403429 | **54.01%** |
| XGBoost | 0.000383 | 0.014156 | -0.000673 | 54.01% |
| LightGBM | 0.000412 | 0.015008 | -0.075398 | 45.91% |

**Outcome**: Models showed ~53-54% accuracy, confirming market-independent behavior patterns

---

## Phase 2: Global Market & Portfolio Optimization (Completed)

### Experiment 1: S&P 500 Foundation
- ✅ Built new scraping pipeline for S&P 500 (through 2022)
- ✅ Performed comprehensive EDA on 500+ stocks
- ✅ Trained 4 baseline prediction models per company
- ✅ Generated initial portfolio allocations using Modern Portfolio Theory (MPT)

### Experiment 2: Advanced Portfolio Strategies (10,000 Monte Carlo Simulations)
Tested 10 distinct portfolio optimization methodologies over 252-day horizon:

| Strategy | Mean Return | Volatility | VaR (95%) | Profit Probability |
|----------|-------------|-----------|----------|-------------------|
| Stochastic Programming | 21.16% | Optimal | $8,711 | 81.5% |
| Robust Optimization | 20.18% | Low | $8,989 | 84.8% |
| MPT - Max Sharpe | 19.75% | Balanced | $9,005 | 83.8% |
| Post-MPT - Max Sortino | 19.84% | Downside-focused | $8,989 | 84.0% |
| Factor Investing | 18.97% | Factor-based | $9,078 | 84.4% |
| ML-Based | 18.33% | ML-optimized | $8,861 | 82.4% |
| Risk Parity | 17.60% | Equal risk | $8,826 | 81.5% |
| Black-Litterman | 18.38% | View-integrated | $8,403 | 77.5% |
| MPT - Min Variance | 16.99% | Minimal | $8,929 | 82.2% |
| Post-MPT - Min CVaR | 16.83% | CVaR-minimized | $8,967 | 82.5% |

**Key Insights**:
- Stochastic programming delivered highest expected returns (21.16%)
- Robust optimization achieved best risk-adjusted profile (84.8% profit probability)
- 9 of 10 strategies achieved >80% profit probability
- Trade-off between return maximization and risk minimization validated

---

## Phase 3: Enhanced Price Prediction (Current - In Progress)

### Discoveries from Phase 2:
- ✅ Identified that predicting absolute price changes failed
- ✅ Confirmed return-based prediction is more effective
- ✅ Multi-timeframe analysis (weekly, monthly) shows promise
- ✅ Ensemble approaches combining classical + ML models yield better results

### Objective 1: Advanced Forecasting Pipeline (Current Focus)
- [ ] Engineer 50+ features: technical indicators, volatility measures, correlations
- [ ] Build multi-timeframe ensemble (daily → weekly → monthly predictions)
- [ ] Implement adaptive models that adjust to market regimes
- [ ] Test hybrid approaches (ARIMA-LSTM combinations)
- [ ] Target: Achieve >60% directional accuracy on validation set
- [ ] Timeline: 4-6 weeks

### Objective 2: Prediction-Driven Portfolio Allocation
- [ ] Integrate price predictions as input to portfolio optimization
- [ ] Dynamic weight adjustment based on forecast confidence scores
- [ ] Risk-adjusted position sizing via Kelly Criterion
- [ ] Implement semi-daily rebalancing triggers
- [ ] Timeline: 3-4 weeks (post-Objective 1)

---

## Next Steps & Timeline

### Immediate (Weeks 1-2):
1. Design feature engineering pipeline
2. Build multi-timeframe model architecture
3. Establish baseline ensemble performance

### Short-term (Weeks 3-6):
1. Hyperparameter optimization across models
2. Backtest on 2-year holdout set
3. Validate directional accuracy targets

### Medium-term (Weeks 7-10):
1. Integrate predictions with portfolio strategies
2. Run end-to-end backtesting with transaction costs
3. Compare against buy-and-hold benchmarks

### Deployment Phase:
1. Live prediction pipeline on new data
2. Real-time portfolio rebalancing system
3. Performance monitoring dashboard



suggested baseline - 
1 - simple day to day linear regression but predicting on for 30 days
2 - lstm with decomposition predicting and trained for 30 days
3 - garch + classifier(up or down) for 30 days
4 - multi head transformer with decomposition for 30 days
5 - cnn + lstm with decomposition trained for 30 days
6 - separate bi - lstm chains for each component of decomposition, then combining them to get reslut for 30 day prediction

