-- 005_decisions.sql
CREATE TABLE decisions (
  decision_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  market_id    TEXT REFERENCES markets(market_id),
  side         TEXT,
  size_usd     FLOAT,
  market_prob  FLOAT,
  llm_prob     FLOAT,
  edge         FLOAT,
  confidence   TEXT,
  rationale    TEXT,
  dry_run      BOOLEAN DEFAULT TRUE,
  decided_at   TIMESTAMPTZ DEFAULT now()
);
