-- ============================================================================
-- Migration 011: Verify and report on all required tables
-- ============================================================================

-- Check what tables exist
DO $$
DECLARE
    tables_status TEXT := '';
BEGIN
    -- Check users table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        tables_status := tables_status || '✓ users table exists' || E'\n';
    ELSE
        tables_status := tables_status || '✗ users table MISSING' || E'\n';
    END IF;

    -- Check sources table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sources') THEN
        tables_status := tables_status || '✓ sources table exists' || E'\n';
    ELSE
        tables_status := tables_status || '✗ sources table MISSING' || E'\n';
    END IF;

    -- Check content table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'content') THEN
        tables_status := tables_status || '✓ content table exists' || E'\n';
    ELSE
        tables_status := tables_status || '✗ content table MISSING' || E'\n';
    END IF;

    -- Check trends table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'trends') THEN
        tables_status := tables_status || '✓ trends table exists' || E'\n';
    ELSE
        tables_status := tables_status || '✗ trends table MISSING' || E'\n';
    END IF;

    -- Check style_profiles table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'style_profiles') THEN
        tables_status := tables_status || '✓ style_profiles table exists' || E'\n';
    ELSE
        tables_status := tables_status || '✗ style_profiles table MISSING' || E'\n';
    END IF;

    -- Check drafts table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'drafts') THEN
        tables_status := tables_status || '✓ drafts table exists' || E'\n';
    ELSE
        tables_status := tables_status || '✗ drafts table MISSING' || E'\n';
    END IF;

    -- Check newsletter_sends table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'newsletter_sends') THEN
        tables_status := tables_status || '✓ newsletter_sends table exists' || E'\n';
    ELSE
        tables_status := tables_status || '✗ newsletter_sends table MISSING' || E'\n';
    END IF;

    RAISE NOTICE E'\nTable Status:\n%', tables_status;
END $$;

-- Check drafts table columns specifically
DO $$
DECLARE
    drafts_cols TEXT := '';
    col_name TEXT;
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'drafts') THEN
        RAISE NOTICE E'\nDrafts table columns:';

        FOR col_name IN
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'drafts'
            ORDER BY ordinal_position
        LOOP
            RAISE NOTICE '  - %', col_name;
        END LOOP;
    ELSE
        RAISE NOTICE E'\nDrafts table does not exist - run migration 010 first';
    END IF;
END $$;
