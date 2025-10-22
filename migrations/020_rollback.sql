-- Phase 1: Rollback Review Time Tracking
-- Use this to rollback if Phase 1 causes issues

-- Drop indexes
DROP INDEX IF EXISTS idx_drafts_reviewed_at;
DROP INDEX IF EXISTS idx_drafts_approved_at;

-- Drop columns
ALTER TABLE drafts DROP COLUMN IF EXISTS reviewed_at;
ALTER TABLE drafts DROP COLUMN IF EXISTS approved_at;
