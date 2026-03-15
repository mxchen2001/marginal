-- 001_raw_events.sql
CREATE TABLE raw_events (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source       TEXT NOT NULL,
  event_type   TEXT NOT NULL,
  payload      JSONB NOT NULL,
  collected_at TIMESTAMPTZ DEFAULT now(),
  hash         TEXT UNIQUE
);
