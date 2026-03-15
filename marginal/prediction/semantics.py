"""Market semantics — question parsing and resolution condition extraction."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MarketSemantics:
    """Parsed understanding of a market question."""

    resolution_condition: str
    category: str
    ambiguity_flags: list[str]


def parse_resolution_condition(question: str) -> MarketSemantics:
    """Parse a market question into structured semantics."""
    raise NotImplementedError
