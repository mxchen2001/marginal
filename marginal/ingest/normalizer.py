"""Normalizer — transforms raw API responses into canonical DB schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import json
from marginal.ingest.scorer import score_signal


# ---------------------------------------------------------------------------
# Market normalization
# ---------------------------------------------------------------------------

def normalize_market(platform: str, raw: dict[str, Any]) -> dict[str, Any]:
    """Transform raw market JSON into the markets table schema.

    Handles Polymarket and Kalshi response formats.
    """
    if platform == "polymarket":
        return _normalize_polymarket(raw)
    elif platform == "kalshi":
        return _normalize_kalshi(raw)
    else:
        raise ValueError(f"Unknown platform: {platform}")


def _normalize_polymarket(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Polymarket market response."""
    # Polymarket gamma-api fields
    market_id = f"polymarket:{raw.get('id', raw.get('condition_id', ''))}"
    tokens = raw.get("tokens", [])
    yes_price = None
    if tokens:
        for t in tokens:
            if t.get("outcome", "").upper() == "YES":
                yes_price = float(t.get("price", 0))
                break
    if yes_price is None:
        # parse as json if type is string
        if type(raw.get("outcomePrices")) == str:
            outcome_prices = json.loads(raw.get("outcomePrices"))
        else:
            outcome_prices = raw.get("outcomePrices", [0.5])
            
        print(outcome_prices)
            
        yes_price = float(outcome_prices[0])

    return {
        "market_id": market_id,
        "platform": "polymarket",
        "question": raw.get("question", raw.get("title", "")),
        "category": _normalize_category(raw.get("tags", raw.get("category", ""))),
        "yes_price": yes_price,
        "volume": float(raw.get("volume", raw.get("volume24hr", 0)) or 0),
        "liquidity": float(raw.get("liquidity", 0) or 0),
        "close_at": raw.get("end_date_iso", raw.get("endDate")),
        "is_open": not raw.get("closed", False) and raw.get("active", True),
    }


def _normalize_kalshi(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Kalshi market response."""
    market_id = f"kalshi:{raw.get('ticker', raw.get('id', ''))}"
    yes_price = float(raw.get("yes_ask", raw.get("last_price", 0.5)) or 0.5) / 100

    return {
        "market_id": market_id,
        "platform": "kalshi",
        "question": raw.get("title", raw.get("subtitle", "")),
        "category": _normalize_category(raw.get("category", "")),
        "yes_price": yes_price,
        "volume": float(raw.get("volume", 0) or 0),
        "liquidity": float(raw.get("liquidity", 0) or 0),
        "close_at": raw.get("close_time", raw.get("expiration_time")),
        "is_open": raw.get("status", "").lower() in ("open", "active"),
    }


# ---------------------------------------------------------------------------
# Signal normalization
# ---------------------------------------------------------------------------

def normalize_signal(source: str, raw: dict[str, Any]) -> dict[str, Any]:
    """Transform raw news/social JSON into the signals table schema."""
    if source == "newsapi":
        return _normalize_newsapi(raw)
    elif source == "rss":
        return _normalize_rss(raw)
    elif source == "reddit":
        return _normalize_reddit(raw)
    else:
        raise ValueError(f"Unknown signal source: {source}")


def _normalize_newsapi(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a NewsAPI article."""
    source_name = raw.get("source", {}).get("name", "unknown")
    published_at = raw.get("publishedAt", datetime.utcnow().isoformat())

    return {
        "source_name": source_name,
        "headline": raw.get("title", ""),
        "body": (raw.get("description", "") or "")[:1000],
        "signal_score": score_signal(source_name, _parse_dt(published_at)),
        "direction": 0,  # neutral until routed + scored
        "published_at": published_at,
    }


def _normalize_rss(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize an RSS feed entry (parsed by feedparser)."""
    source_name = raw.get("feed_title", "rss")
    published_at = raw.get("published", datetime.utcnow().isoformat())

    return {
        "source_name": source_name,
        "headline": raw.get("title", ""),
        "body": (raw.get("summary", "") or "")[:1000],
        "signal_score": score_signal(source_name, _parse_dt(published_at)),
        "direction": 0,
        "published_at": published_at,
    }


def _normalize_reddit(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Reddit post."""
    published_at = datetime.utcfromtimestamp(
        raw.get("created_utc", 0)
    ).isoformat()

    return {
        "source_name": f"reddit/r/{raw.get('subreddit', 'unknown')}",
        "headline": raw.get("title", ""),
        "body": (raw.get("selftext", "") or "")[:1000],
        "signal_score": score_signal("reddit", _parse_dt(published_at)),
        "direction": 0,
        "published_at": published_at,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize_category(raw_category: Any) -> str:
    """Normalize category to a consistent string."""
    if isinstance(raw_category, list):
        return raw_category[0].lower() if raw_category else "other"
    return str(raw_category or "other").lower()


def _parse_dt(dt_str: str) -> datetime:
    """Best-effort parse of a datetime string."""
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(dt_str, fmt)
        except (ValueError, TypeError):
            continue
    return datetime.utcnow()
