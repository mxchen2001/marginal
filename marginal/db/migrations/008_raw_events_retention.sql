-- 008_raw_events_retention.sql
-- Auto-delete raw_events older than 7 days using pg_cron

-- Enable pg_cron (already available on Supabase Pro)
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule daily cleanup at 3am UTC
SELECT cron.schedule(
  'cleanup-raw-events',
  '0 3 * * *',
  $$DELETE FROM raw_events WHERE collected_at < now() - interval '7 days'$$
);
