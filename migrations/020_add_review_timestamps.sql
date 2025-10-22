-- Phase 1: Add Review Time Tracking
-- Add timestamps to track user review time for drafts

-- Add reviewed_at: when user first opens/views the draft
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;

-- Add approved_at: when user approves/sends the draft
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_drafts_reviewed_at ON drafts(reviewed_at);
CREATE INDEX IF NOT EXISTS idx_drafts_approved_at ON drafts(approved_at);

-- Comment for clarity
COMMENT ON COLUMN drafts.reviewed_at IS 'Timestamp when user first reviewed the draft';
COMMENT ON COLUMN drafts.approved_at IS 'Timestamp when user approved/sent the draft';
