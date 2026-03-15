"""Typed query helpers for all DB tables."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from marginal.db.client import get_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# raw_events
# ---------------------------------------------------------------------------

def insert_raw_event(
    source: str, event_type: str, payload: dict[str, Any], hash: str
) -> dict[str, Any] | None:
    """Insert a raw event. Returns the row or None if duplicate (hash conflict)."""
    try:
        result = (
            get_client()
            .table("raw_events")
            .insert(
                {
                    "source": source,
                    "event_type": event_type,
                    "payload": payload,
                    "hash": hash,
                }
            )
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        # Unique constraint violation on hash = duplicate
        if "duplicate" in str(e).lower() or "23505" in str(e):
            logger.debug("Duplicate raw event skipped: %s", hash)
            return None
        raise


# ---------------------------------------------------------------------------
# markets
# ---------------------------------------------------------------------------

def upsert_market(market: dict[str, Any]) -> dict[str, Any]:
    """Upsert a market record. market must include market_id."""
    market["last_updated"] = datetime.utcnow().isoformat()
    result = (
        get_client()
        .table("markets")
        .upsert(market, on_conflict="market_id")
        .execute()
    )
    return result.data[0]


def fetch_market(market_id: str) -> dict[str, Any] | None:
    """Fetch a single market by ID."""
    result = (
        get_client()
        .table("markets")
        .select("*")
        .eq("market_id", market_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def fetch_open_markets() -> list[dict[str, Any]]:
    """Fetch all open markets."""
    result = (
        get_client()
        .table("markets")
        .select("*")
        .eq("is_open", True)
        .execute()
    )
    return result.data


# ---------------------------------------------------------------------------
# signals
# ---------------------------------------------------------------------------

def insert_signal(signal: dict[str, Any]) -> dict[str, Any]:
    """Insert a signal record."""
    result = (
        get_client()
        .table("signals")
        .insert(signal)
        .execute()
    )
    return result.data[0]


def fetch_signals(
    market_id: str, limit: int = 10, order_by: str = "signal_score"
) -> list[dict[str, Any]]:
    """Fetch signals for a market, ordered by score descending."""
    result = (
        get_client()
        .table("signals")
        .select("*")
        .eq("market_id", market_id)
        .order(order_by, desc=True)
        .limit(limit)
        .execute()
    )
    return result.data


# ---------------------------------------------------------------------------
# odds_snapshots
# ---------------------------------------------------------------------------

def insert_odds_snapshot(
    market_id: str, yes_price: float, volume: float
) -> dict[str, Any]:
    """Insert an odds snapshot."""
    result = (
        get_client()
        .table("odds_snapshots")
        .insert(
            {"market_id": market_id, "yes_price": yes_price, "volume": volume}
        )
        .execute()
    )
    return result.data[0]


def fetch_odds_trend(
    market_id: str, hours: int = 48
) -> list[dict[str, Any]]:
    """Fetch recent odds snapshots for a market."""
    result = (
        get_client()
        .table("odds_snapshots")
        .select("*")
        .eq("market_id", market_id)
        .order("snapshotted_at", desc=True)
        .limit(100)
        .execute()
    )
    return result.data


# ---------------------------------------------------------------------------
# positions
# ---------------------------------------------------------------------------

def upsert_position(position: dict[str, Any]) -> dict[str, Any]:
    """Upsert a position record."""
    result = (
        get_client()
        .table("positions")
        .upsert(position, on_conflict="position_id")
        .execute()
    )
    return result.data[0]


def fetch_open_positions(
    market_id: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch open positions, optionally filtered by market_id."""
    query = (
        get_client()
        .table("positions")
        .select("*")
        .eq("status", "open")
    )
    if market_id:
        query = query.eq("market_id", market_id)
    return query.execute().data


# ---------------------------------------------------------------------------
# decisions
# ---------------------------------------------------------------------------

def insert_decision(decision: dict[str, Any]) -> dict[str, Any]:
    """Insert a decision record."""
    result = (
        get_client()
        .table("decisions")
        .insert(decision)
        .execute()
    )
    return result.data[0]


def fetch_decisions(market_id: str) -> list[dict[str, Any]]:
    """Fetch all decisions for a market."""
    result = (
        get_client()
        .table("decisions")
        .select("*")
        .eq("market_id", market_id)
        .order("decided_at", desc=True)
        .execute()
    )
    return result.data


# ---------------------------------------------------------------------------
# calibration_log
# ---------------------------------------------------------------------------

def insert_calibration_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Insert a calibration log entry."""
    result = (
        get_client()
        .table("calibration_log")
        .insert(entry)
        .execute()
    )
    return result.data[0]
