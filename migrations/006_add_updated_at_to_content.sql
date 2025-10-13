-- Add updated_at column to content table

-- Add updated_at column if it doesn't exist
ALTER TABLE content ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Backfill existing rows with created_at value
UPDATE content SET updated_at = created_at WHERE updated_at IS NULL;

-- Make updated_at NOT NULL
ALTER TABLE content ALTER COLUMN updated_at SET NOT NULL;

-- Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_content_updated_at ON content;
CREATE TRIGGER update_content_updated_at
    BEFORE UPDATE ON content
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
