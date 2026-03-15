"""Signal router — maps incoming signals to relevant markets via embeddings."""

from __future__ import annotations

import logging
from typing import Any

import httpx
import numpy as np

logger = logging.getLogger(__name__)


class SignalRouter:
    """Routes news/social signals to relevant markets using cosine similarity."""

    SIMILARITY_THRESHOLD = 0.75
    EMBEDDING_MODEL = "text-embedding-3-small"

    def __init__(self, openai_api_key: str) -> None:
        self.openai_api_key = openai_api_key

    async def embed(self, text: str) -> list[float]:
        """Embed text using OpenAI text-embedding-3-small."""
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in a single API call."""
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={"model": self.EMBEDDING_MODEL, "input": texts},
            )
            resp.raise_for_status()
            data = resp.json()

        # Sort by index to preserve order
        sorted_data = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in sorted_data]

    async def route(
        self, signal_headline: str, open_markets: list[dict[str, Any]]
    ) -> list[str]:
        """Return market_ids whose questions are similar to the signal headline."""
        if not open_markets:
            return []

        signal_vec = np.array(await self.embed(signal_headline))
        matched_ids: list[str] = []

        for market in open_markets:
            embedding = market.get("embedding")
            if embedding is None:
                continue
            market_vec = np.array(embedding)
            sim = float(np.dot(signal_vec, market_vec) / (
                np.linalg.norm(signal_vec) * np.linalg.norm(market_vec) + 1e-9
            ))
            if sim >= self.SIMILARITY_THRESHOLD:
                matched_ids.append(market["market_id"])

        logger.debug(
            "Routed signal '%s' to %d markets", signal_headline[:60], len(matched_ids)
        )
        return matched_ids
