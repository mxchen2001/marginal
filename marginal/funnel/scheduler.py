"""Scheduler — orchestrates the data funnel and prediction loop."""

from __future__ import annotations

import asyncio
import logging

import schedule

from marginal.config import Settings
from marginal.db import queries
from marginal.funnel.markets import KalshiClient, PolymarketClient
from marginal.funnel.news import NewsAPIFetcher, RSSFetcher
from marginal.funnel.router import SignalRouter
from marginal.funnel.social import RedditClient
from marginal.ingest.normalizer import normalize_market, normalize_signal
from marginal.ingest.raw_store import store_raw_event

logger = logging.getLogger(__name__)


async def run_once() -> None:
    """Execute a single iteration of the data funnel.

    Flow: fetch markets → store raw → normalize → upsert
          fetch news/social → store raw → normalize → route → insert signals
    """
    settings = Settings.get()
    logger.info("Starting funnel iteration (dry_run=%s)", settings.dry_run)

    # --- 1. Fetch & ingest markets ---
    all_raw_markets = []

    # Polymarket
    poly = PolymarketClient()
    try:
        poly_markets = await poly.fetch_open_markets()
        all_raw_markets.extend(poly_markets)
    except Exception:
        logger.error("Failed to fetch Polymarket markets", exc_info=True)

    # Kalshi
    if settings.kalshi_api_key:
        kalshi = KalshiClient(settings.kalshi_api_key)
        try:
            kalshi_markets = await kalshi.fetch_open_markets()
            all_raw_markets.extend(kalshi_markets)
        except Exception:
            logger.error("Failed to fetch Kalshi markets", exc_info=True)

    # Store raw + normalize + upsert markets
    market_count = 0
    for raw in all_raw_markets:
        store_raw_event(raw.platform, "market_snapshot", raw.payload)
        normalized = normalize_market(raw.platform, raw.payload)
        queries.upsert_market(normalized)
        # Snapshot odds
        queries.insert_odds_snapshot(
            normalized["market_id"],
            normalized.get("yes_price", 0.5),
            normalized.get("volume", 0),
        )
        market_count += 1

    logger.info("Ingested %d markets", market_count)

    # --- 2. Fetch & ingest news signals ---
    all_raw_signals = []

    # NewsAPI
    if settings.newsapi_key:
        news = NewsAPIFetcher(settings.newsapi_key)
        try:
            articles = await news.fetch()
            all_raw_signals.extend(articles)
        except Exception:
            logger.error("Failed to fetch NewsAPI", exc_info=True)

    # RSS
    rss = RSSFetcher()
    try:
        rss_articles = await rss.fetch()
        all_raw_signals.extend(rss_articles)
    except Exception:
        logger.error("Failed to fetch RSS feeds", exc_info=True)

    # Reddit (sync call, run in executor)
    if settings.reddit_client_id:
        try:
            reddit = RedditClient(
                settings.reddit_client_id,
                settings.reddit_client_secret,
                settings.reddit_user_agent,
            )
            loop = asyncio.get_event_loop()
            reddit_posts = await loop.run_in_executor(None, reddit.fetch_posts)
            all_raw_signals.extend(reddit_posts)
        except Exception:
            logger.error("Failed to fetch Reddit", exc_info=True)

    # Store raw signals
    for raw in all_raw_signals:
        store_raw_event(raw.source, "signal", raw.payload)

    # --- 3. Normalize signals and route to markets ---
    signal_count = 0
    open_markets = queries.fetch_open_markets()

    # Set up router if we have embeddings
    router = None
    if settings.openai_api_key and open_markets:
        router = SignalRouter(settings.openai_api_key)

    for raw in all_raw_signals:
        try:
            normalized = normalize_signal(raw.source, raw.payload)
        except Exception:
            logger.warning("Failed to normalize signal from %s", raw.source, exc_info=True)
            continue

        # Route signal to markets
        if router:
            try:
                matched_ids = await router.route(
                    normalized.get("headline", ""), open_markets
                )
            except Exception:
                logger.warning("Failed to route signal", exc_info=True)
                matched_ids = []
        else:
            matched_ids = []

        # Insert signal for each matched market
        for market_id in matched_ids:
            signal_row = {**normalized, "market_id": market_id}
            queries.insert_signal(signal_row)
            signal_count += 1

    logger.info("Ingested %d signals across %d markets", signal_count, len(open_markets))
    logger.info("Funnel iteration complete")


def run_loop() -> None:
    """Start the recurring loop on the configured interval."""
    settings = Settings.get()
    interval = settings.loop_interval_minutes

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    logger.info("Starting marginal loop (every %d min, dry_run=%s)", interval, settings.dry_run)

    def _run() -> None:
        asyncio.run(run_once())

    # Run immediately, then on schedule
    _run()
    schedule.every(interval).minutes.do(_run)

    while True:
        schedule.run_pending()
        import time
        time.sleep(1)
