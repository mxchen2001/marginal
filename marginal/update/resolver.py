"""Market resolver — polls for resolved markets and computes PnL."""

from __future__ import annotations


async def resolve_markets() -> int:
    """Check for newly resolved markets, compute PnL, update positions. Returns count resolved."""
    raise NotImplementedError
