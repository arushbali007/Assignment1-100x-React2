-- Phase 8: Rollback Morning Delivery Preferences

-- Drop index
DROP INDEX IF EXISTS idx_users_delivery_enabled;

-- Drop columns
ALTER TABLE users DROP COLUMN IF EXISTS delivery_enabled;
ALTER TABLE users DROP COLUMN IF EXISTS delivery_time;
ALTER TABLE users DROP COLUMN IF EXISTS delivery_days;
