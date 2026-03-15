-- 002_markets.sql
CREATE TABLE markets (
  market_id    TEXT PRIMARY KEY,
  platform     TEXT,
  question     TEXT,
  category     TEXT,
  yes_price    FLOAT,
  volume       FLOAT,
  liquidity    FLOAT,
  close_at     TIMESTAMPTZ,
  is_open      BOOLEAN DEFAULT TRUE,
  embedding    VECTOR(1536),       -- pgvector for signal routing
  last_updated TIMESTAMPTZ
);
