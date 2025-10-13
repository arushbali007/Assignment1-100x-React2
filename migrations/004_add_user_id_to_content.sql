-- Migration to add user_id column to content table
-- This fixes the mismatch between the original schema and the application code

-- Add user_id column to content table
ALTER TABLE content ADD COLUMN IF NOT EXISTS user_id UUID;

-- Populate user_id from sources table (backfill existing data)
UPDATE content
SET user_id = sources.user_id
FROM sources
WHERE content.source_id = sources.id
AND content.user_id IS NULL;

-- Make user_id NOT NULL after backfill
ALTER TABLE content ALTER COLUMN user_id SET NOT NULL;

-- Add foreign key constraint
ALTER TABLE content ADD CONSTRAINT content_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_content_user_id ON content(user_id);

-- Update RLS policies if needed
DROP POLICY IF EXISTS "Users can view content from own sources" ON content;
CREATE POLICY "Users can view content from own sources"
    ON content FOR SELECT
    USING (user_id = auth.uid() OR user_id IN (SELECT user_id FROM sources WHERE auth.uid() = sources.user_id));

DROP POLICY IF EXISTS "Users can insert content from own sources" ON content;
CREATE POLICY "Users can insert content from own sources"
    ON content FOR INSERT
    WITH CHECK (user_id = auth.uid() OR user_id IN (SELECT user_id FROM sources WHERE auth.uid() = sources.user_id));
