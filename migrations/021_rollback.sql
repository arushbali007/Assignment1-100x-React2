-- Phase 2: Rollback Draft Outcome Tracking

-- Drop index
DROP INDEX IF EXISTS idx_drafts_outcome;

-- Drop columns
ALTER TABLE drafts DROP COLUMN IF EXISTS outcome;
ALTER TABLE drafts DROP COLUMN IF EXISTS rejection_reason;
