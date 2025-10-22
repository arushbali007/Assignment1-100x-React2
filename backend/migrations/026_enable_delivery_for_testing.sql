-- Migration 026: Enable delivery for all users for testing
-- This enables morning delivery for all existing users

-- Update all users to have delivery enabled
UPDATE users
SET
    delivery_enabled = true,
    delivery_time = '08:00:00',
    delivery_days = 'daily',
    timezone = 'UTC',
    updated_at = NOW()
WHERE id IS NOT NULL;

-- Verify the changes
SELECT
    id,
    email,
    delivery_enabled,
    delivery_time,
    delivery_days,
    timezone
FROM users
ORDER BY created_at DESC;
