"""Supabase client singleton."""

from __future__ import annotations

from supabase import Client, create_client

from marginal.config import Settings

_client: Client | None = None


def get_client() -> Client:
    """Get or create the Supabase client singleton."""
    global _client
    if _client is None:
        settings = Settings.get()
        _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client
