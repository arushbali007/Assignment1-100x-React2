-- ============================================================================
-- Migration 009: Ensure drafts table has all required columns
-- ============================================================================

-- Add content_data column if it doesn't exist (JSONB type)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'drafts' AND column_name = 'content_data'
    ) THEN
        ALTER TABLE drafts ADD COLUMN content_data JSONB NOT NULL DEFAULT '{}';
    END IF;
END $$;

-- Add metadata column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'drafts' AND column_name = 'metadata'
    ) THEN
        ALTER TABLE drafts ADD COLUMN metadata JSONB DEFAULT '{}';
    END IF;
END $$;

-- Add status column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'drafts' AND column_name = 'status'
    ) THEN
        ALTER TABLE drafts ADD COLUMN status TEXT DEFAULT 'pending';
    END IF;
END $$;

-- Add notes column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'drafts' AND column_name = 'notes'
    ) THEN
        ALTER TABLE drafts ADD COLUMN notes TEXT;
    END IF;
END $$;

-- Add reviewed_at column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'drafts' AND column_name = 'reviewed_at'
    ) THEN
        ALTER TABLE drafts ADD COLUMN reviewed_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- Add sent_at column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'drafts' AND column_name = 'sent_at'
    ) THEN
        ALTER TABLE drafts ADD COLUMN sent_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- Verify all columns exist
DO $$
DECLARE
    missing_columns TEXT[];
BEGIN
    SELECT ARRAY_AGG(col)
    INTO missing_columns
    FROM UNNEST(ARRAY['user_id', 'subject', 'html_content', 'plain_content', 'content_data',
                      'status', 'metadata', 'notes', 'reviewed_at', 'sent_at',
                      'created_at', 'updated_at']) AS col
    WHERE NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'drafts' AND column_name = col
    );

    IF array_length(missing_columns, 1) > 0 THEN
        RAISE EXCEPTION 'Missing columns in drafts table: %', array_to_string(missing_columns, ', ');
    ELSE
        RAISE NOTICE 'All required columns exist in drafts table';
    END IF;
END $$;
