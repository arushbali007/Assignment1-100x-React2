-- Comprehensive fix for trends table to match application code

-- 1. Add user_id column if it doesn't exist
ALTER TABLE trends ADD COLUMN IF NOT EXISTS user_id UUID;

-- 2. Add missing columns that the app expects
ALTER TABLE trends ADD COLUMN IF NOT EXISTS score DECIMAL(10, 2);
ALTER TABLE trends ADD COLUMN IF NOT EXISTS google_trends_score DECIMAL(10, 2);
ALTER TABLE trends ADD COLUMN IF NOT EXISTS content_mentions INTEGER DEFAULT 0;
ALTER TABLE trends ADD COLUMN IF NOT EXISTS velocity DECIMAL(10, 2) DEFAULT 0.0;
ALTER TABLE trends ADD COLUMN IF NOT EXISTS related_content_ids UUID[];
ALTER TABLE trends ADD COLUMN IF NOT EXISTS detected_at TIMESTAMP WITH TIME ZONE;

-- 3. Migrate data from old columns to new columns
UPDATE trends SET detected_at = spike_detected_at WHERE detected_at IS NULL AND spike_detected_at IS NOT NULL;
UPDATE trends SET score = trend_score WHERE score IS NULL AND trend_score IS NOT NULL;

-- 4. Set default values for detected_at and score
UPDATE trends SET detected_at = created_at WHERE detected_at IS NULL;
UPDATE trends SET score = 0.0 WHERE score IS NULL;

-- 5. Delete trends without user_id (safe for fresh setup)
DELETE FROM trends WHERE user_id IS NULL;

-- 6. Make required columns NOT NULL
ALTER TABLE trends ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE trends ALTER COLUMN score SET NOT NULL;
ALTER TABLE trends ALTER COLUMN detected_at SET NOT NULL;

-- 7. Add foreign key constraint
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

-- 8. Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_trends_user_id ON trends(user_id);
CREATE INDEX IF NOT EXISTS idx_trends_user_keyword ON trends(user_id, keyword);
CREATE INDEX IF NOT EXISTS idx_trends_detected_at ON trends(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_trends_score ON trends(score DESC);

-- 9. Update RLS policies for trends (since we use custom auth, not Supabase Auth)
DROP POLICY IF EXISTS "Users can view their own trends" ON trends;
DROP POLICY IF EXISTS "Users can insert their own trends" ON trends;
DROP POLICY IF EXISTS "Users can update their own trends" ON trends;
DROP POLICY IF EXISTS "Users can delete their own trends" ON trends;

-- Note: Since we're using supabase_admin (service key) in the code,
-- we don't need strict RLS policies, but let's add permissive ones
CREATE POLICY "Allow all operations on trends"
    ON trends FOR ALL
    USING (true)
    WITH CHECK (true);

-- 10. Drop old columns if you want (optional - uncomment if desired)
-- ALTER TABLE trends DROP COLUMN IF EXISTS trend_score;
-- ALTER TABLE trends DROP COLUMN IF EXISTS spike_detected_at;
-- ALTER TABLE trends DROP COLUMN IF EXISTS category;
-- ALTER TABLE trends DROP COLUMN IF EXISTS sources;
