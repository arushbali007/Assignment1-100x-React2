-- Phase 2: Add Draft Outcome Tracking
-- Track whether drafts were accepted or rejected

-- Add outcome field: 'accepted', 'rejected', or null (pending)
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS outcome VARCHAR(20);

-- Add rejection reason for rejected drafts
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- Add index for outcome queries
CREATE INDEX IF NOT EXISTS idx_drafts_outcome ON drafts(outcome);

-- Comments for clarity
COMMENT ON COLUMN drafts.outcome IS 'Draft outcome: accepted, rejected, or null (pending)';
COMMENT ON COLUMN drafts.rejection_reason IS 'Reason provided when draft is rejected';
