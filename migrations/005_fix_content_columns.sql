-- Migration to align content table columns with application code
-- The app expects: content_type, body, url
-- The DB has: content_text, content_html, url (from migration 001)

-- Check current columns
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'content';

-- Add content_type column if it doesn't exist
ALTER TABLE content ADD COLUMN IF NOT EXISTS content_type TEXT;

-- Rename content_text to body if body doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'content' AND column_name = 'body') THEN
        ALTER TABLE content RENAME COLUMN content_text TO body;
    END IF;
END $$;

-- Set default content_type for existing rows (assume articles from RSS)
UPDATE content SET content_type = 'article' WHERE content_type IS NULL;

-- Make content_type NOT NULL after setting defaults
ALTER TABLE content ALTER COLUMN content_type SET NOT NULL;

-- Add index for content_type
CREATE INDEX IF NOT EXISTS idx_content_type ON content(content_type);
