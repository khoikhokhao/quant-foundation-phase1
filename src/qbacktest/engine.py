from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd

from .utils import (
    calc_returns, equity_from_position, compute_drawdown, perf_summary, TradeLogger
)

@dataclass
class BacktestResult:
    equity: pd.Series          # equity curve
    returns: pd.Series         # daily pnl series used for metrics
    drawdown: pd.Series        # drawdown series
    trades: pd.DataFrame       # logged trades (optional)
    summary: dict              # metrics dict

class BaseStrategy:
    """
    Base class for simple daily backtests.
    Expect df with columns: 'timestamp','close' (others optional).
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.sort_values("timestamp").reset_index(drop=True).copy()
        if "timestamp" not in self.df or "close" not in self.df:
            raise ValueError("df must contain 'timestamp' and 'close'.")

    # ---- Overridable: produce raw (unshifted) signal in {-1,0,1} ----
    def generate_signal(self) -> pd.Series:
        raise NotImplementedError

    # ---- Position sizing ----
    @staticmethod
    def position_from_signal(signal: pd.Series, mode: str = "full", risk_pct: float = 0.2) -> pd.Series:
        """
        - 'full'      → position ∈ {-1,0,1}
        - 'fixed_pct' → weights ∈ {-k,0,k} (fraction of equity)
        """
        sig = signal.fillna(0.0)
        if mode == "full":
            return sig
        if mode == "fixed_pct":
            return risk_pct * np.sign(sig)
        raise ValueError("mode must be 'full' or 'fixed_pct'")

    # ---- Run backtest ----
    def run(self, signal: Optional[pd.Series] = None, mode: str = "full", risk_pct: float = 0.2) -> BacktestResult:
        """
        Compute daily PnL with yesterday's position/weight (no lookahead).
        """
        raw_sig = self.generate_signal() if signal is None else signal.astype(float)
        sig = raw_sig.shift(1).fillna(0.0)  # use today's signal tomorrow

        pos_or_w = self.position_from_signal(sig, mode=mode, risk_pct=risk_pct)
        rets = calc_returns(self.df, price_col="close")
        daily_pnl = pos_or_w.shift(1).fillna(0.0) * rets
        equity = (1.0 + daily_pnl).cumprod()

        dd = compute_drawdown(equity)["drawdown"]
        summary = perf_summary(daily_pnl)

        # ---- simple trade logging: when sign changes ----
        logger = TradeLogger()
        series = pos_or_w.fillna(0.0)
        prev = series.shift(1).fillna(0.0)
        changed = np.sign(series) != np.sign(prev)
        idx = np.where(changed)[0]
        for i in idx:
            action = "FLAT"
            if series.iloc[i] > 0 and prev.iloc[i] <= 0:
                action = "BUY"
            elif series.iloc[i] < 0 and prev.iloc[i] >= 0:
                action = "SELL"
            logger.log(self.df["timestamp"].iloc[i], action, float(self.df["close"].iloc[i]),
                       float(series.iloc[i]), float(equity.iloc[i]))

        return BacktestResult(
            equity=equity.rename("equity"),
            returns=daily_pnl.rename("daily_ret"),
            drawdown=dd.rename("drawdown"),
            trades=logger.to_frame(),
            summary=summary
        )

class SignalColumnStrategy(BaseStrategy):
    """Use an existing signal column (e.g., 'sig_sma') from df."""
    def __init__(self, df: pd.DataFrame, signal_col: str):
        super().__init__(df)
        self.signal_col = signal_col
        if self.signal_col not in self.df.columns:
            raise ValueError(f"Missing signal column: {self.signal_col}")

    def generate_signal(self) -> pd.Series:
        return self.df[self.signal_col].astype(float)

# ---- Optional: quick plotting helper (matplotlib) ----
def plot_equity_and_dd(res: BacktestResult, ax_eq=None, ax_dd=None):
    """Draw equity curve and drawdown using matplotlib (one figure with two axes if ax not provided)."""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    if ax_eq is None or ax_dd is None:
        fig, (ax_eq, ax_dd) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

    t = res.equity.index if isinstance(res.equity.index, pd.DatetimeIndex) else None
    x = res.equity.index if t is not None else range(len(res.equity))

    ax_eq.plot(res.equity.index if t is not None else res.equity.index, res.equity.values, label="Equity")
    ax_eq.set_title("Equity Curve"); ax_eq.set_ylabel("Equity"); ax_eq.legend()

    ax_dd.plot(res.drawdown.index if t is not None else res.drawdown.index, res.drawdown.values, label="Drawdown")
    ax_dd.set_title("Drawdown"); ax_dd.set_ylabel("DD"); ax_dd.set_xlabel("Date" if t is not None else "Index"); ax_dd.legend()

    if t is not None:
        ax_eq.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax_eq.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
        ax_dd.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax_dd.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))

    if ax_eq is None or ax_dd is None:
        plt.tight_layout(); plt.show()
