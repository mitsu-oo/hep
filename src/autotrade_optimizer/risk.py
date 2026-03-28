from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskPolicy:
    max_risk_per_trade: float = 0.01
    stop_loss_pct: float = 0.02

    def position_size(self, equity: float, entry_price: float) -> float:
        if equity <= 0 or entry_price <= 0:
            return 0.0
        risk_amount = equity * self.max_risk_per_trade
        unit_risk = entry_price * self.stop_loss_pct
        if unit_risk <= 0:
            return 0.0
        return max(0.0, risk_amount / unit_risk)
