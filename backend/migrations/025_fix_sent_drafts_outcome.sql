-- Migration 025: Fix existing sent drafts to have outcome='accepted'
-- This updates drafts that were sent before we added the outcome tracking

-- Update all sent drafts that don't have an outcome
UPDATE drafts
SET
    outcome = 'accepted',
    updated_at = NOW()
WHERE
    status = 'sent'
    AND outcome IS NULL;

-- Also set approved_at to sent_at if approved_at is missing
UPDATE drafts
SET
    approved_at = sent_at,
    updated_at = NOW()
WHERE
    status = 'sent'
    AND sent_at IS NOT NULL
    AND approved_at IS NULL;

-- Verify the changes
SELECT
    id,
    subject,
    status,
    outcome,
    created_at,
    approved_at,
    sent_at
FROM drafts
WHERE status = 'sent'
ORDER BY created_at DESC;
