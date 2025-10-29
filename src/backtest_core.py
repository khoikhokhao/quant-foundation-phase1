# backtest_core.py
# A Python-based modular backtesting script capable of evaluating multiple strategies.
# Dependencies: numpy, pandas (matplotlib optional only for plot_equity).

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Iterable
import numpy as np
import pandas as pd

# ===== Strategy Interface =====================================================

class Strategy(ABC):
    """
    Abstract strategy interface.
    Input:  df (index=datetime, must contain 'close' float)
    Output: DataFrame with a column 'signal' indicating desired position for next bar.
            Convention (long-only): signal ∈ {0, 1}
            Optional long/short:    signal ∈ {-1, 0, 1}
    NOTE: The engine applies positions at t based on signal at t-1 (no lookahead).
    """
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        ...

# ===== Backtest Engine ========================================================

class Backtester:
    """
    Vectorized backtester (close-to-close).
      - Position at day t is signal_{t-1}.
      - net_ret_t = pos_{t-1} * ret_t - 1{trade_t} * (fee + slippage)
    """
    def __init__(self, fee_bps: float = 5.0, slippage_bps: float = 2.0, start_cash: float = 10_000.0):
        self.fee = fee_bps / 10_000.0
        self.slip = slippage_bps / 10_000.0
        self.start_cash = float(start_cash)

    def run(self, df_with_signal: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
        df = df_with_signal.copy()
        if "close" not in df.columns or "signal" not in df.columns:
            raise ValueError("Input must contain columns: ['close', 'signal'].")

        # Clean & returns
        df = df.dropna(subset=["close"])
        df["ret"] = df["close"].pct_change().fillna(0.0)

        # Positions & trades
        df["pos"] = df["signal"].fillna(0).astype(float)
        df["pos_prev"] = df["pos"].shift(1).fillna(0.0)
        df["trade"] = (df["pos"] - df["pos_prev"]).abs()

        # PnL
        gross = df["pos_prev"] * df["ret"]
        cost = df["trade"] * (self.fee + self.slip)
        df["net_ret"] = gross - cost
        df["equity"] = (1.0 + df["net_ret"]).cumprod() * self.start_cash

        # Metrics
        daily = df["net_ret"].replace([np.inf, -np.inf], 0).fillna(0)
        cumret = (1 + daily).prod() - 1
        sharpe = np.sqrt(252) * (daily.mean() / (daily.std(ddof=0) + 1e-12))
        roll = (1 + daily).cumprod()
        mdd = (roll / roll.cummax() - 1).min()
        trades = int(df["trade"].sum())

        report = {
            "Cumulative Return": float(cumret),
            "Sharpe (daily,252)": float(sharpe),
            "Max Drawdown": float(mdd),
            "Trades": trades,
        }
        return df, report

    @staticmethod
    def plot_equity(df: pd.DataFrame, title: str = "Equity Curve") -> None:
        import matplotlib.pyplot as plt  # optional
        ax = df["equity"].plot(figsize=(8,3), title=title)
        ax.set_xlabel("Time"); ax.set_ylabel("Equity")
        plt.show()

# ===== Batch evaluation =======================================================

def evaluate_strategies(
    price_df: pd.DataFrame,
    strategies: Dict[str, Strategy],
    engine: Backtester
) -> Dict[str, Dict[str, float]]:
    """
    Run multiple strategies on the same price series.
    Returns {strategy_name: report_dict}
    """
    if "close" not in price_df.columns:
        raise ValueError("price_df must have a 'close' column.")
    if not isinstance(price_df.index, pd.DatetimeIndex):
        raise ValueError("price_df index must be a DatetimeIndex (UTC recommended).")

    results = {}
    for name, strat in strategies.items():
        sig_df = strat.generate_signals(price_df[["close"]])
        # enforce presence of 'close' (if strategy dropped it)
        if "close" not in sig_df.columns:
            sig_df = sig_df.join(price_df[["close"]], how="left")
        _, report = engine.run(sig_df)
        results[name] = report
    return results

# ===== Minimal example strategy (for smoke test) ==============================
# Bạn có thể xóa phần này; để lại cho __main__ dùng kiểm chứng khung.

class AlwaysHold(Strategy):
    """Hold 100% exposure; engine will shift to avoid lookahead."""
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["signal"] = 1
        out["signal"] = out["signal"].shift(1).fillna(0).astype(int)
        return out

# ===== Helpers (optional) =====================================================

def read_price_csv(
    path: str,
    ts_candidates=("timestamp","time","date","datetime"),
    close_candidates=("close","adj close","adj_close","c"),
    dayfirst: bool = True
) -> pd.DataFrame:
    """
    Read CSV → DataFrame(index=datetime, cols=['close']).
    Only for convenience; you can provide your own loader.
    """
    raw = pd.read_csv(path)
    cols_lower = {c.lower(): c for c in raw.columns}

    def pick(cands: Iterable[str]) -> str | None:
        for c in cands:
            if c in cols_lower: return cols_lower[c]
        return None

    ts_col = pick(ts_candidates); cl_col = pick(close_candidates)
    if ts_col is None or cl_col is None:
        raise ValueError("Cannot find timestamp/close columns in CSV.")

    df = raw[[ts_col, cl_col]].copy()
    df.columns = ["timestamp", "close"]

    if np.issubdtype(df["timestamp"].dtype, np.number):
        is_ms = df["timestamp"].astype("int64").astype(str).str.len().median() > 10
        unit = "ms" if is_ms else "s"
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit=unit, utc=True)
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, dayfirst=dayfirst, errors="coerce")

    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["timestamp","close"]).query("close > 0")
    df = df.sort_values("timestamp").set_index("timestamp")
    df = df[~df.index.duplicated(keep="last")]
    return df[["close"]]

# ===== Script demo ============================================================

if __name__ == "__main__":
    # Tiny synthetic demo (no indicators, just to smoke-test the engine)
    n = 250
    close = 100 * (1 + pd.Series(np.random.normal(0, 0.02, n))).cumprod().values
    price = pd.DataFrame({"close": close}, index=pd.date_range("2023-01-01", periods=n, tz="UTC"))

    engine = Backtester(fee_bps=5, slippage_bps=2, start_cash=10_000)
    results = evaluate_strategies(price, {"AlwaysHold": AlwaysHold()}, engine)
    print("Smoke test reports:", results)
