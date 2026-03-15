-- 003_signals.sql
CREATE TABLE signals (
  signal_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  market_id    TEXT REFERENCES markets(market_id),
  source_name  TEXT,
  headline     TEXT,
  body         TEXT,
  signal_score FLOAT,
  direction    SMALLINT,
  published_at TIMESTAMPTZ,
  collected_at TIMESTAMPTZ DEFAULT now()
);
