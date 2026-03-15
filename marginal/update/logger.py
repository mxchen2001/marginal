"""Decision logger — persists decisions and updates positions."""

from __future__ import annotations

from typing import Any


async def log_decision(decision: dict[str, Any]) -> str:
    """Log a decision to the decisions table. Returns decision_id."""
    raise NotImplementedError


async def update_position(position: dict[str, Any]) -> None:
    """Upsert a position in the positions table."""
    raise NotImplementedError
