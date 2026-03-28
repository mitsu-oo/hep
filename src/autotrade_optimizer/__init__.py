"""AutoTrade Optimizer package."""

from .engine import BacktestResult, StrategyConfig, optimize_strategy

__all__ = ["BacktestResult", "StrategyConfig", "optimize_strategy"]
