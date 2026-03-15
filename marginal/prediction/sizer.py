"""Position sizer — fractional Kelly criterion."""

from __future__ import annotations


def kelly_size(
    edge: float,
    confidence: str,
    bankroll: float,
    max_position: float,
) -> float:
    """Compute bet size using fractional Kelly criterion."""
    raise NotImplementedError
