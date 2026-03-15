"""Order placer — places bets via platform APIs."""

from __future__ import annotations

from dataclasses import dataclass

from marginal.prediction.risk_guard import Placement


@dataclass
class ExecutionReceipt:
    """Receipt from a placed order."""

    placement: Placement
    order_id: str | None
    filled: bool
    fill_price: float | None
    error: str | None


async def place_order(placement: Placement, dry_run: bool = True) -> ExecutionReceipt:
    """Place an order on the target platform. No-op if dry_run."""
    raise NotImplementedError
