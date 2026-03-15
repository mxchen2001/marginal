"""News fetchers — NewsAPI and RSS feeds."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import feedparser
import httpx

logger = logging.getLogger(__name__)


@dataclass
class RawArticle:
    """A raw news article before normalization."""

    source: str
    payload: dict


class NewsAPIFetcher:
    """Fetches headlines from NewsAPI.org."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def fetch(self, query: str | None = None) -> list[RawArticle]:
        """Fetch top headlines, optionally filtered by query."""
        params: dict[str, str] = {"apiKey": self.api_key, "language": "en"}
        if query:
            params["q"] = query
            endpoint = f"{self.BASE_URL}/everything"
        else:
            endpoint = f"{self.BASE_URL}/top-headlines"
            params["country"] = "us"

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()

        articles = [
            RawArticle(source="newsapi", payload=article)
            for article in data.get("articles", [])
        ]
        logger.info("Fetched %d articles from NewsAPI", len(articles))
        return articles


class RSSFetcher:
    """Fetches and parses RSS feeds using feedparser."""

    DEFAULT_FEEDS: list[str] = [
        "https://feeds.reuters.com/reuters/topNews",
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://rsshub.app/apnews/topics/apf-topnews",
    ]

    async def fetch(self, feeds: list[str] | None = None) -> list[RawArticle]:
        """Fetch and parse RSS feeds. Uses default feeds if none provided."""
        feed_urls = feeds or self.DEFAULT_FEEDS
        articles: list[RawArticle] = []

        async with httpx.AsyncClient(timeout=30) as client:
            for url in feed_urls:
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    parsed = feedparser.parse(resp.text)
                    feed_title = parsed.feed.get("title", url)

                    for entry in parsed.entries:
                        articles.append(
                            RawArticle(
                                source="rss",
                                payload={
                                    "feed_title": feed_title,
                                    "title": entry.get("title", ""),
                                    "summary": entry.get("summary", ""),
                                    "link": entry.get("link", ""),
                                    "published": entry.get("published", ""),
                                },
                            )
                        )
                except Exception:
                    logger.warning("Failed to fetch RSS feed: %s", url, exc_info=True)

        logger.info("Fetched %d articles from %d RSS feeds", len(articles), len(feed_urls))
        return articles
