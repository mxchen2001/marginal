"""Risk guard — enforces hard rules and flags low-confidence bets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Placement:
    """A candidate bet that has passed through sizing."""

    market_id: str
    question: str
    platform: str
    side: str
    market_prob: float
    llm_prob: float
    edge: float
    confidence: str
    size_usd: float
    rationale: str
    created_at: datetime


@dataclass
class GuardResult:
    """Result of risk guard check."""

    approved: bool
    reason: str
    adjusted_size: float | None = None


async def check_placement(placement: Placement) -> GuardResult:
    """Check a placement against risk rules."""
    raise NotImplementedError
