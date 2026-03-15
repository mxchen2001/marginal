"""Deduplication — hash-based event dedup."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def dedup_hash(source: str, content: str) -> str:
    """Generate a truncated SHA-256 hash for deduplication."""
    return hashlib.sha256(f"{source}:{content}".encode()).hexdigest()[:16]


def payload_hash(source: str, payload: dict[str, Any]) -> str:
    """Hash a source + payload dict for dedup."""
    content = json.dumps(payload, sort_keys=True, default=str)
    return dedup_hash(source, content)
