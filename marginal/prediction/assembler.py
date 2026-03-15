"""Context assembler — builds MarketContextBundle for the LLM evaluator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MarketContextBundle:
    """All context needed for the LLM to evaluate a market."""

    market: dict[str, Any]
    signals: list[dict[str, Any]]
    odds_trend: list[dict[str, Any]]
    base_rate: float | None
    already_positioned: bool


async def build_context_bundle(market_id: str) -> MarketContextBundle:
    """Assemble all context for a given market from DB."""
    raise NotImplementedError
