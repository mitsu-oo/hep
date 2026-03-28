import pytest

from autotrade_optimizer.data import Candle, generate_mock_candles
from autotrade_optimizer.engine import BacktestResult, StrategyConfig, backtest, optimize_strategy


def test_backtest_basic_metrics_shape():
    candles = generate_mock_candles(300, seed=7)
    result = backtest(candles, StrategyConfig(short_window=5, long_window=30))

    assert result.final_equity > 0
    assert -1.0 <= result.total_return <= 10.0
    assert 0.0 <= result.max_drawdown <= 1.0


def test_optimizer_returns_valid_config():
    candles = generate_mock_candles(320, seed=11)
    result = optimize_strategy(candles, range(5, 15, 5), range(20, 50, 10))

    assert result.config.long_window > result.config.short_window
    assert result.trades >= 0


def test_optimizer_weight_validation():
    candles = generate_mock_candles(120, seed=3)
    with pytest.raises(ValueError):
        optimize_strategy(candles, profit_weight=0)
    with pytest.raises(ValueError):
        optimize_strategy(candles, risk_penalty=-0.1)


def test_optimizer_targets_positive_sharpe():
    candles = generate_mock_candles(365, seed=42)
    result = optimize_strategy(candles, require_positive_sharpe=True)
    assert result.sharpe_like > 0


def test_optimizer_raises_when_positive_sharpe_unavailable(monkeypatch: pytest.MonkeyPatch):
    candles = [Candle(ts=f"day-{i}", close=100.0 + i) for i in range(1, 120)]

    def _always_negative(*args, **kwargs):
        cfg = args[1]
        return BacktestResult(
            config=cfg,
            final_equity=9500.0,
            total_return=-0.05,
            sharpe_like=-0.4,
            max_drawdown=0.2,
            trades=3,
        )

    monkeypatch.setattr("autotrade_optimizer.engine.backtest", _always_negative)

    with pytest.raises(ValueError, match="positive sharpe_like"):
        optimize_strategy(candles, require_positive_sharpe=True)


def test_optimizer_skips_invalid_window_pairs():
    candles = generate_mock_candles(60, seed=9)
    # long_window=200 is invalid for this candle length, but optimizer should skip it and continue.
    result = optimize_strategy(
        candles,
        short_windows=[5, 10],
        long_windows=[20, 200],
        require_positive_sharpe=False,
    )
    assert result.config.long_window == 20
