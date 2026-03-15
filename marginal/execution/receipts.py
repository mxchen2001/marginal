"""Execution receipts — stores order results in the DB."""

from __future__ import annotations

from typing import Any


async def store_receipt(receipt: Any) -> None:
    """Persist an execution receipt to the database."""
    raise NotImplementedError
