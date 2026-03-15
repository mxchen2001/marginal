"""Signal aggregator — combines signals into a directional score per market."""

from __future__ import annotations


async def aggregate_signals(market_id: str) -> float:
    """Aggregate signal scores for a market. Returns score in [-1, 1]."""
    raise NotImplementedError
