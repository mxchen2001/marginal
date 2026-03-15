"""Deduplication — hash-based event dedup."""

from __future__ import annotations

import hashlib
from typing import Any

# Keys that uniquely identify an event per source type.
# Only these are hashed — volatile fields like price/volume are ignored.
_IDENTITY_KEYS: dict[str, list[str]] = {
    "polymarket": ["id", "condition_id"],
    "kalshi": ["ticker", "id"],
    "newsapi": ["url", "title", "publishedAt"],
    "rss": ["link", "title"],
    "reddit": ["subreddit", "title", "created_utc"],
}


def dedup_hash(source: str, content: str) -> str:
    """Generate a truncated SHA-256 hash for deduplication."""
    return hashlib.sha256(f"{source}:{content}".encode()).hexdigest()[:16]


def payload_hash(source: str, payload: dict[str, Any]) -> str:
    """Hash a source + stable identity fields for dedup.

    Only hashes fields that identify the event (not volatile data like prices).
    """
    identity_keys = _IDENTITY_KEYS.get(source)
    if identity_keys:
        parts = [str(payload.get(k, "")) for k in identity_keys]
        content = "|".join(parts)
    else:
        # Unknown source — fall back to title or first string value
        content = str(payload.get("title", payload.get("id", str(payload))))
    return dedup_hash(source, content)
