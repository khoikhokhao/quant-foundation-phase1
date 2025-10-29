# Phase 1 Report — Foundation in Quant & Programming

**Author:** Phạm Minh Khôi  
**Asset:** ETH-USD (Ethereum)  
**Timeframe:** 2020-10-27 → 2025-10-27  
**Date Generated:** 2025-10-27 15:04 UTC

---

## 1️⃣ Objectives and Scope
Phase 1 aims to build a complete quantitative workflow:
- Develop a **modular Python backtesting engine** using Pandas, NumPy, and OOP.
- Understand the pipeline: **Signal → Position → Execution → PnL → Metrics**.
- Implement two fundamental strategies:
  - **RSI (Mean Reversion)**
  - **SMA Crossover (Trend Following)**
- Evaluate performance using:
  - CAGR, Sharpe Ratio, Max Drawdown, Volatility, Total Return.
- Use **ETH-USD** data (daily, 5 years) retrieved via `yfinance`.

---

## 2️⃣ Data Collection and Preprocessing

**Source:** Yahoo Finance (`yfinance`)

- Interval: 1 Day  
- Period: 5 Years  
- Data points: 1827 rows  
- Missing values: 0  
- Duplicate timestamps: 0  
- Zero volume days: 0  

**Data cleaning process:**
1. Remove duplicated indices and non-positive prices.  
2. Forward-fill missing OHLC values.  
3. Normalize timezone to UTC.  
4. Store data as `/content/data/ETH-USD.csv`.

**Indicators added:**
- SMA(20), SMA(60), EMA(20)
- RSI(14)
- Bollinger Bands (mid, up, down)
- Daily returns `ret1`

All computed using **rolling windows without lookahead**.

---

## 3️⃣ Backtest Engine Architecture

A fully modular, OOP-based backtesting engine was implemented with the following design:

**Classes:**
- `StrategyBase`: defines structure for signal generation.
- `BacktestEngine`: executes backtests, applies fees, and computes metrics.

**Core metrics:**
- CAGR (Compound Annual Growth Rate)
- Sharpe Ratio
- Max Drawdown (MDD)
- Volatility
- Total Return

**Transaction assumptions:**
- Trading fee = 0.05%
- Slippage = 0.02%
- Execution uses **signal(t-1)** → return(t) (ensuring **no lookahead bias**)

---

## 4️⃣ RSI Strategy (Mean Reversion)

**Logic:**
- Buy when RSI < 30 (oversold)
- Exit when RSI > 70 (overbought)

| Metric | RSI | Buy & Hold |
|---------|------|------------|
| CAGR | 0.0355 | 0.5938 |
| Sharpe | 0.2413 | 0.8169 |
| MDD | -0.576 | -0.7935 |
| Vol | 0.3478 | 0.6598 |
| Total Return | 0.1907 | 9.281 |

**Interpretation:**
- RSI effectively **reduces drawdown** (-57% vs -79%) but sacrifices upside.
- Performance (CAGR ≈ 3.5%) is modest due to infrequent signals in trending markets.
- The strategy is defensive — suited for range-bound or volatile phases.

---

## 5️⃣ SMA Crossover Strategy (Trend Following)

**Logic:**
- Buy when SMA(20) > SMA(60)
- Exit when SMA(20) < SMA(60)

| Metric | SMA(20/60) | Buy & Hold |
|---------|-------------|------------|
| CAGR | 0.5797 | 0.5938 |
| Sharpe | 0.8896 | 0.8169 |
| MDD | -0.5829 | -0.7935 |
| Vol | 0.4883 | 0.6598 |
| Total Return | 8.8327 | 9.281 |

**Interpretation:**
- SMA Crossover **captures medium-term trends**, maintaining comparable returns to Buy & Hold.
- Sharpe ratio higher (0.89 vs 0.82) → better risk-adjusted performance.
- MDD lower (-58% vs -79%) → reduced risk exposure.

---

## 6️⃣ Comparative Summary

| Metric | RSI | SMA(20/60) |
|---------|------|-------------|
| CAGR | 0.0355 | 0.5797 |
| Sharpe | 0.2413 | 0.8896 |
| MDD | -0.576 | -0.5829 |
| Vol | 0.3478 | 0.4883 |
| Total Return | 0.1907 | 8.8327 |

**Observations:**
- RSI: Safe but underperforms in strong trends.
- SMA(20/60): Performs best overall with good Sharpe and lower drawdown.
- Both outperform Buy & Hold in risk management.

---

## 7️⃣ Conclusions and Next Steps

**Summary of Deliverables (Week 5):**
| Deliverable | Description | Status |
|--------------|--------------|---------|
| Backtest Engine | Python-based OOP engine with metrics & benchmark | ✅ |
| Strategy Reports | RSI & SMA notebooks with code, plots, and analysis | ✅ |
| Code Repository | Cleanly structured and documented code | ✅ |
| Weekly Logs | Comprehensive report (this document) | ✅ |

**Insights:**
- RSI provides downside protection, ideal for conservative strategies.
- SMA(20/60) balances return and risk, suitable for trend-driven markets.
- Backtest engine ready for scaling to multiple assets and risk models.

**Next Phase (Phase 2):**
- Portfolio-level backtesting with multiple crypto assets.
- Risk-adjusted allocation (e.g., volatility parity).
- Hyperparameter optimization (grid search, walk-forward testing).
- Implementation of Monte Carlo simulation for risk scenarios.

---

## 8️⃣ Leader Summary (for Review)

**Strengths:**
- Code modularity and reproducibility.
- Correct prevention of lookahead bias.
- Clear understanding of mean reversion vs trend following.
- Strong documentation and visualization.

**Improvements:**
- Add transaction summary logs for trade-level inspection.
- Explore short-side trades for RSI during downtrends.
- Extend to portfolio-level simulation.

**Final Verdict:** ✅ **Phase 1 completed successfully. Ready for Phase 2.**

---
