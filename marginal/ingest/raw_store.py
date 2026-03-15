"""Raw event store — append-only log of all collected data."""

from __future__ import annotations

import logging
from typing import Any

from marginal.db import queries
from marginal.ingest.dedup import payload_hash

logger = logging.getLogger(__name__)


def store_raw_event(
    source: str, event_type: str, payload: dict[str, Any]
) -> str | None:
    """Write a raw event to the raw_events table.

    Returns the event ID or None if it was a duplicate.
    """
    hash = payload_hash(source, payload)
    row = queries.insert_raw_event(source, event_type, payload, hash)
    if row is None:
        logger.debug("Skipped duplicate event from %s", source)
        return None
    logger.info("Stored raw event %s from %s", row["id"], source)
    return row["id"]
