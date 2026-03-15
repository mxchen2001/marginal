-- 007_odds_snapshots.sql
CREATE TABLE odds_snapshots (
  id             BIGSERIAL PRIMARY KEY,
  market_id      TEXT REFERENCES markets(market_id),
  yes_price      FLOAT,
  volume         FLOAT,
  snapshotted_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_odds_snapshots_market_time
  ON odds_snapshots(market_id, snapshotted_at DESC);
