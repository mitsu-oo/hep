from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev

from .data import Candle
from .risk import RiskPolicy


@dataclass(frozen=True)
class StrategyConfig:
    short_window: int
    long_window: int

    def validate(self) -> None:
        if self.short_window < 2:
            raise ValueError("short_window must be >= 2")
        if self.long_window <= self.short_window:
            raise ValueError("long_window must be > short_window")


@dataclass(frozen=True)
class BacktestResult:
    config: StrategyConfig
    final_equity: float
    total_return: float
    sharpe_like: float
    max_drawdown: float
    trades: int


def _sma(values: list[float], window: int, idx: int) -> float:
    if idx + 1 < window:
        raise ValueError("insufficient points")
    segment = values[idx + 1 - window : idx + 1]
    return mean(segment)


def backtest(
    candles: list[Candle],
    config: StrategyConfig,
    initial_equity: float = 10_000.0,
    risk_policy: RiskPolicy | None = None,
) -> BacktestResult:
    config.validate()
    if len(candles) <= config.long_window:
        raise ValueError("not enough candles for long window")
    risk = risk_policy or RiskPolicy()

    prices = [c.close for c in candles]
    equity = initial_equity
    units = 0.0
    peak = initial_equity
    max_dd = 0.0
    daily_returns: list[float] = []
    trades = 0

    prev_mark_to_market = initial_equity

    for i in range(config.long_window, len(prices)):
        short_ma = _sma(prices, config.short_window, i)
        long_ma = _sma(prices, config.long_window, i)
        p = prices[i]

        if short_ma > long_ma and units == 0.0:
            target_units = risk.position_size(equity, p)
            cost = target_units * p
            if cost <= equity:
                units = target_units
                equity -= cost
                trades += 1
        elif short_ma < long_ma and units > 0.0:
            equity += units * p
            units = 0.0
            trades += 1

        mtm = equity + units * p
        ret = (mtm - prev_mark_to_market) / prev_mark_to_market if prev_mark_to_market else 0.0
        daily_returns.append(ret)
        prev_mark_to_market = mtm

        peak = max(peak, mtm)
        dd = (peak - mtm) / peak if peak else 0.0
        max_dd = max(max_dd, dd)

    final_equity = equity + units * prices[-1]
    total_return = (final_equity - initial_equity) / initial_equity

    if len(daily_returns) > 1 and pstdev(daily_returns) > 1e-12:
        sharpe_like = (mean(daily_returns) / pstdev(daily_returns)) * (252**0.5)
    else:
        sharpe_like = 0.0

    return BacktestResult(
        config=config,
        final_equity=round(final_equity, 2),
        total_return=round(total_return, 4),
        sharpe_like=round(sharpe_like, 4),
        max_drawdown=round(max_dd, 4),
        trades=trades,
    )


def optimize_strategy(
    candles: list[Candle],
    short_windows: range = range(5, 25, 5),
    long_windows: range = range(20, 101, 10),
) -> BacktestResult:
    best: BacktestResult | None = None
    for short_w in short_windows:
        for long_w in long_windows:
            if long_w <= short_w:
                continue
            res = backtest(candles, StrategyConfig(short_w, long_w))
            if best is None:
                best = res
                continue
            score = res.sharpe_like - res.max_drawdown
            best_score = best.sharpe_like - best.max_drawdown
            if score > best_score:
                best = res

    if best is None:
        raise ValueError("no valid parameter combinations")
    return best
