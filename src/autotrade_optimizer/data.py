from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import random


@dataclass(frozen=True)
class Candle:
    ts: str
    close: float


def load_csv(path: str | Path) -> list[Candle]:
    p = Path(path)
    rows: list[Candle] = []
    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(Candle(ts=row["timestamp"], close=float(row["close"])))
    if not rows:
        raise ValueError("CSV has no data")
    return rows


def generate_mock_candles(n: int = 365, seed: int = 42) -> list[Candle]:
    if n < 3:
        raise ValueError("n must be >= 3")
    rng = random.Random(seed)
    out: list[Candle] = []
    price = 100.0
    for day in range(n):
        drift = 0.03
        shock = rng.uniform(-1.2, 1.2)
        price = max(1.0, price + drift + shock)
        out.append(Candle(ts=f"day-{day+1}", close=round(price, 4)))
    return out
