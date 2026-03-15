-- 004_positions.sql
CREATE TABLE positions (
  position_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  market_id    TEXT REFERENCES markets(market_id),
  platform     TEXT,
  side         TEXT,
  size_usd     FLOAT,
  entry_price  FLOAT,
  status       TEXT DEFAULT 'open',
  opened_at    TIMESTAMPTZ DEFAULT now(),
  closed_at    TIMESTAMPTZ
);
