from __future__ import annotations

import argparse
import json

from .data import generate_mock_candles, load_csv
from .engine import optimize_strategy


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="AutoTrade Optimizer CLI")
    p.add_argument("--csv", help="Path to CSV with timestamp,close columns")
    p.add_argument("--points", type=int, default=365, help="Mock data points if CSV is omitted")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    candles = load_csv(args.csv) if args.csv else generate_mock_candles(args.points)
    best = optimize_strategy(candles)

    print(
        json.dumps(
            {
                "short_window": best.config.short_window,
                "long_window": best.config.long_window,
                "final_equity": best.final_equity,
                "total_return": best.total_return,
                "sharpe_like": best.sharpe_like,
                "max_drawdown": best.max_drawdown,
                "trades": best.trades,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
