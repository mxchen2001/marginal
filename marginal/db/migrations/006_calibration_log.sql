-- 006_calibration_log.sql
CREATE TABLE calibration_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_id     UUID REFERENCES decisions(decision_id),
  market_id       TEXT,
  category        TEXT,
  llm_prob        FLOAT,
  actual_outcome  FLOAT,
  delta           FLOAT,
  pnl             FLOAT,
  resolved_at     TIMESTAMPTZ
);