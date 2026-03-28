from autotrade_optimizer.data import generate_mock_candles
from autotrade_optimizer.engine import StrategyConfig, backtest, optimize_strategy


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
