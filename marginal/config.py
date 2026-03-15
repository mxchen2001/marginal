"""Central configuration loaded from .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv


@dataclass
class Settings:
    """All configuration for the marginal bot, loaded from environment."""

    # Database
    supabase_url: str = ""
    supabase_key: str = ""

    # Prediction Markets
    kalshi_api_key: str = ""
    polymarket_api_key: str = ""

    # News & Search
    newsapi_key: str = ""
    tavily_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "marginal/0.1"

    # LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Loop Config
    loop_interval_minutes: int = 30
    min_edge_threshold: float = 0.05
    max_position_usd: float = 50.0
    max_daily_loss_usd: float = 200.0
    dry_run: bool = True

    _instance: ClassVar[Settings | None] = None

    @classmethod
    def load(cls) -> Settings:
        """Load settings from environment variables. Looks for .env in project root."""
        # Walk up to find .env
        env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(env_path)

        return cls(
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_KEY", ""),
            kalshi_api_key=os.getenv("KALSHI_API_KEY", ""),
            polymarket_api_key=os.getenv("POLYMARKET_API_KEY", ""),
            newsapi_key=os.getenv("NEWSAPI_KEY", ""),
            tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
            reddit_client_id=os.getenv("REDDIT_CLIENT_ID", ""),
            reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
            reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "marginal/0.1"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            loop_interval_minutes=int(os.getenv("LOOP_INTERVAL_MINUTES", "30")),
            min_edge_threshold=float(os.getenv("MIN_EDGE_THRESHOLD", "0.05")),
            max_position_usd=float(os.getenv("MAX_POSITION_USD", "50")),
            max_daily_loss_usd=float(os.getenv("MAX_DAILY_LOSS_USD", "200")),
            dry_run=os.getenv("DRY_RUN", "true").lower() in ("true", "1", "yes"),
        )

    @classmethod
    def get(cls) -> Settings:
        """Get the singleton settings instance, loading if needed."""
        if cls._instance is None:
            cls._instance = cls.load()
        return cls._instance
