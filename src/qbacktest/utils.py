from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Dict, Optional
import numpy as np
import pandas as pd

# ---------- Returns & Equity ----------

def calc_returns(df: pd.DataFrame, price_col: str = "close") -> pd.Series:
    """Simple daily return r_t = P_t / P_{t-1} - 1 (filled NaN->0)."""
    r = df[price_col].pct_change()
    return r.fillna(0.0)

def equity_from_position(returns: pd.Series, position: pd.Series, initial_equity: float = 1.0) -> pd.Series:
    """
    Build equity curve using yesterday's position (no lookahead).
    position may be {-1,0,1} (full) or weights in [-k, k] (fixed-%).
    """
    pnl = position.shift(1).fillna(0.0) * returns.fillna(0.0)
    return (1.0 + pnl).cumprod() * initial_equity

# ---------- Drawdowns & Metrics ----------

def compute_drawdown(equity: pd.Series) -> pd.DataFrame:
    """Return DataFrame with equity, running peak, drawdown."""
    eq = equity.fillna(method="ffill").fillna(1.0)
    peak = eq.cummax()
    dd = eq / peak - 1.0
    return pd.DataFrame({"equity": eq, "peak": peak, "drawdown": dd})

def annualize_return(daily_ret: pd.Series, freq: int = 252) -> float:
    """CAGR estimated from a series of daily returns."""
    daily_ret = daily_ret.fillna(0.0)
    equity = (1.0 + daily_ret).cumprod()
    n = len(daily_ret)
    if n <= 1:
        return 0.0
    return float(equity.iloc[-1] ** (freq / n) - 1.0)

def annualize_vol(daily_ret: pd.Series, freq: int = 252) -> float:
    return float(daily_ret.std(ddof=0) * np.sqrt(freq))

def sharpe_ratio(daily_ret: pd.Series, rf_daily: float = 0.0, freq: int = 252) -> float:
    """Annualized Sharpe; if vol≈0 -> 0."""
    er = daily_ret.fillna(0.0) - rf_daily
    vol = er.std(ddof=0)
    if vol == 0 or np.isnan(vol):
        return 0.0
    return float((er.mean() * np.sqrt(freq)) / vol)

def perf_summary(daily_ret: pd.Series) -> Dict[str, float]:
    """Convenient dict of key performance metrics."""
    eq = (1.0 + daily_ret.fillna(0.0)).cumprod()
    dd = compute_drawdown(eq)["drawdown"]
    return {
        "CAGR": annualize_return(daily_ret),
        "Vol_Ann": annualize_vol(daily_ret),
        "Sharpe": sharpe_ratio(daily_ret),
        "MaxDD": float(dd.min()) if len(dd) else 0.0,
        "EquityEnd": float(eq.iloc[-1]) if len(eq) else 1.0,
        "Ndays": int(len(daily_ret)),
    }

# ---------- Trade Logger ----------

@dataclass
class Trade:
    timestamp: pd.Timestamp
    action: str           # 'BUY', 'SELL', 'FLAT'
    price: float
    size: float           # position or weight after action
    equity_after: float

@dataclass
class TradeLogger:
    records: list[Trade] = field(default_factory=list)

    def log(self, timestamp, action, price, size, equity_after):
        self.records.append(Trade(timestamp, action, float(price), float(size), float(equity_after)))

    def to_frame(self) -> pd.DataFrame:
        if not self.records:
            return pd.DataFrame(columns=["timestamp","action","price","size","equity_after"])
        return pd.DataFrame([t.__dict__ for t in self.records])

# ---------- Config I/O (YAML/JSON) ----------

def load_config(path: str) -> Dict:
    """
    Load YAML or JSON config into dict. Example keys:
    data.path, indicators.sma_short, backtest.mode, backtest.risk_pct, ...
    """
    if path.lower().endswith((".yml", ".yaml")):
        try:
            import yaml  # optional dependency
        except ImportError as e:
            raise ImportError("pyyaml not installed. `pip install pyyaml`") from e
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    elif path.lower().endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError("Unsupported config format. Use .yaml/.yml or .json")
