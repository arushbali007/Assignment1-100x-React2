-- Phase 8: Add Morning Delivery Preferences
-- Allow users to configure automated morning email delivery

-- Add delivery preferences to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS delivery_enabled BOOLEAN DEFAULT true;
ALTER TABLE users ADD COLUMN IF NOT EXISTS delivery_time TIME DEFAULT '08:00:00';
ALTER TABLE users ADD COLUMN IF NOT EXISTS delivery_days VARCHAR(50) DEFAULT 'weekdays';

-- Add indexes for delivery queries
CREATE INDEX IF NOT EXISTS idx_users_delivery_enabled ON users(delivery_enabled);

-- Comments for clarity
COMMENT ON COLUMN users.delivery_enabled IS 'Whether automated morning delivery is enabled';
COMMENT ON COLUMN users.delivery_time IS 'Time to send morning email (user local time)';
COMMENT ON COLUMN users.delivery_days IS 'Which days to send: weekdays, daily, or custom (e.g., Mon,Wed,Fri)';
