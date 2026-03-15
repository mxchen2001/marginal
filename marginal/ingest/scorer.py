"""Signal scorer — recency x credibility weighting."""

from __future__ import annotations

import math
from datetime import datetime, timezone

# Source credibility weights (from Notion spec)
SOURCE_CREDIBILITY: dict[str, float] = {
    "reuters": 1.0,
    "ap": 1.0,
    "ft": 1.0,
    "financial times": 1.0,
    "nyt": 0.9,
    "new york times": 0.9,
    "the guardian": 0.9,
    "bbc": 0.9,
    "bbc news": 0.9,
    "politico": 0.85,
    "bloomberg": 0.85,
    "reddit": 0.5,
}

# Default credibility for unknown sources
DEFAULT_CREDIBILITY = 0.4

# Half-life for recency decay (in hours)
RECENCY_HALF_LIFE_HOURS = 24.0


def _source_credibility(source_name: str) -> float:
    """Look up credibility weight for a source."""
    return SOURCE_CREDIBILITY.get(source_name.lower(), DEFAULT_CREDIBILITY)


def _recency_weight(published_at: datetime) -> float:
    """Exponential decay weight based on age. Returns value in (0, 1]."""
    now = datetime.now(timezone.utc)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    age_hours = max((now - published_at).total_seconds() / 3600, 0)
    return math.exp(-math.log(2) * age_hours / RECENCY_HALF_LIFE_HOURS)


def score_signal(source_name: str, published_at: datetime) -> float:
    """Compute signal score as recency_weight * source_credibility."""
    return _recency_weight(published_at) * _source_credibility(source_name)
