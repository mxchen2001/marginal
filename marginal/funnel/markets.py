"""Prediction market API clients — Polymarket & Kalshi."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class RawMarket:
    """Raw market data from a platform API before normalization."""

    platform: str
    raw_id: str
    payload: dict


class PolymarketClient:
    """Fetches open markets from the Polymarket CLOB API."""

    BASE_URL = "https://gamma-api.polymarket.com"

    async def fetch_open_markets(
        self, limit: int = 100, active: bool = True
    ) -> list[RawMarket]:
        """Fetch open markets from Polymarket's gamma API."""
        params = {"limit": limit, "active": str(active).lower(), "closed": "false"}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{self.BASE_URL}/markets", params=params)
            resp.raise_for_status()
            data = resp.json()

        markets = []
        for item in data if isinstance(data, list) else data.get("data", data.get("markets", [])):
            markets.append(
                RawMarket(
                    platform="polymarket",
                    raw_id=str(item.get("id", item.get("condition_id", ""))),
                    payload=item,
                )
            )
        logger.info("Fetched %d markets from Polymarket", len(markets))
        return markets

    async def fetch_market(self, condition_id: str) -> RawMarket:
        """Fetch a single market by condition ID."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{self.BASE_URL}/markets/{condition_id}")
            resp.raise_for_status()
            data = resp.json()

        return RawMarket(
            platform="polymarket",
            raw_id=condition_id,
            payload=data,
        )


class KalshiClient:
    """Fetches open markets from the Kalshi trading API."""

    BASE_URL = "https://trading-api.kalshi.com/trade-api/v2"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}

    async def fetch_open_markets(
        self, limit: int = 100, status: str = "open"
    ) -> list[RawMarket]:
        """Fetch open markets from Kalshi."""
        params = {"limit": limit, "status": status}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.BASE_URL}/markets",
                headers=self._headers(),
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        markets = []
        for item in data.get("markets", []):
            markets.append(
                RawMarket(
                    platform="kalshi",
                    raw_id=item.get("ticker", item.get("id", "")),
                    payload=item,
                )
            )
        logger.info("Fetched %d markets from Kalshi", len(markets))
        return markets

    async def fetch_market(self, ticker: str) -> RawMarket:
        """Fetch a single market by ticker."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.BASE_URL}/markets/{ticker}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()

        return RawMarket(
            platform="kalshi",
            raw_id=ticker,
            payload=data.get("market", data),
        )
