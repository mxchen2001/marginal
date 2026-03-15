"""On-demand web search via Tavily API."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from tavily import AsyncTavilyClient

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    url: str
    content: str
    score: float


class TavilySearcher:
    """Wraps the Tavily API for on-demand market research."""

    def __init__(self, api_key: str) -> None:
        self.client = AsyncTavilyClient(api_key=api_key)

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Search the web for a query. Used on-demand per market, not polled."""
        response = await self.client.search(query=query, max_results=max_results)
        results = [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                content=r.get("content", ""),
                score=r.get("score", 0.0),
            )
            for r in response.get("results", [])
        ]
        logger.info("Tavily search for '%s' returned %d results", query[:50], len(results))
        return results
