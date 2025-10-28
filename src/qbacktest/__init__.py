"""
qbacktest — minimal, reproducible backtesting helpers.
"""
from .utils import (
    calc_returns, equity_from_position, compute_drawdown,
    annualize_return, annualize_vol, sharpe_ratio, perf_summary,
    Trade, TradeLogger, load_config
)
from .engine import (
    BacktestResult, BaseStrategy, SignalColumnStrategy, plot_equity_and_dd
)

__all__ = [
    "calc_returns","equity_from_position","compute_drawdown",
    "annualize_return","annualize_vol","sharpe_ratio","perf_summary",
    "Trade","TradeLogger","load_config",
    "BacktestResult","BaseStrategy","SignalColumnStrategy","plot_equity_and_dd"
]
__version__ = "0.1.0"
