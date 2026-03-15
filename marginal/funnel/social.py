"""Social signal fetcher — Reddit via PRAW."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import praw

logger = logging.getLogger(__name__)


@dataclass
class RawPost:
    """A raw social media post before normalization."""

    source: str
    payload: dict


class RedditClient:
    """Fetches top posts from target subreddits."""

    DEFAULT_SUBREDDITS = ["politics", "worldnews", "geopolitics", "Economics"]

    def __init__(
        self, client_id: str, client_secret: str, user_agent: str
    ) -> None:
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

    def fetch_posts(
        self,
        subreddits: list[str] | None = None,
        limit: int = 25,
    ) -> list[RawPost]:
        """Fetch hot posts from target subreddits. Synchronous (PRAW is sync)."""
        subs = subreddits or self.DEFAULT_SUBREDDITS
        posts: list[RawPost] = []

        for sub_name in subs:
            try:
                subreddit = self.reddit.subreddit(sub_name)
                for submission in subreddit.hot(limit=limit):
                    posts.append(
                        RawPost(
                            source="reddit",
                            payload={
                                "subreddit": sub_name,
                                "title": submission.title,
                                "selftext": submission.selftext or "",
                                "score": submission.score,
                                "upvote_ratio": submission.upvote_ratio,
                                "created_utc": submission.created_utc,
                                "url": submission.url,
                                "num_comments": submission.num_comments,
                            },
                        )
                    )
            except Exception:
                logger.warning("Failed to fetch r/%s", sub_name, exc_info=True)

        logger.info("Fetched %d posts from %d subreddits", len(posts), len(subs))
        return posts
