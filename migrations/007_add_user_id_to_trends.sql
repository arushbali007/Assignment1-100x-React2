-- Add user_id column to trends table

-- Add user_id column if it doesn't exist
ALTER TABLE trends ADD COLUMN IF NOT EXISTS user_id UUID;

-- For existing trends without user_id, we need to either:
-- 1. Delete them (safest if no important data)
-- 2. Or set a default user (if you know a user_id)

-- Option 1: Delete existing trends (recommended for fresh setup)
DELETE FROM trends WHERE user_id IS NULL;

-- After cleanup, make user_id NOT NULL
ALTER TABLE trends ALTER COLUMN user_id SET NOT NULL;

-- Add foreign key constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'trends_user_id_fkey' AND table_name = 'trends'
    ) THEN
        ALTER TABLE trends ADD CONSTRAINT trends_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_trends_user_id ON trends(user_id);
CREATE INDEX IF NOT EXISTS idx_trends_user_keyword ON trends(user_id, keyword);
CREATE INDEX IF NOT EXISTS idx_trends_detected_at ON trends(detected_at DESC);

-- Update RLS policies for trends
DROP POLICY IF EXISTS "Users can view their own trends" ON trends;
CREATE POLICY "Users can view their own trends"
    ON trends FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can insert their own trends" ON trends;
CREATE POLICY "Users can insert their own trends"
    ON trends FOR INSERT
    WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can update their own trends" ON trends;
CREATE POLICY "Users can update their own trends"
    ON trends FOR UPDATE
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can delete their own trends" ON trends;
CREATE POLICY "Users can delete their own trends"
    ON trends FOR DELETE
    USING (user_id = auth.uid());
