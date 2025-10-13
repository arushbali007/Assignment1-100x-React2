-- ============================================================================
-- Migration 012: Create newsletter_sends table with all required columns
-- ============================================================================

-- Drop existing newsletter_sends table if it exists (to start fresh)
DROP TABLE IF EXISTS newsletter_sends CASCADE;

-- Create newsletter_sends table with all required columns
CREATE TABLE newsletter_sends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    draft_id UUID NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
    recipient_email TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    is_test BOOLEAN DEFAULT FALSE,
    message_id TEXT,
    from_email TEXT,
    from_name TEXT,
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes on newsletter_sends
CREATE INDEX idx_newsletter_sends_user_id ON newsletter_sends(user_id);
CREATE INDEX idx_newsletter_sends_draft_id ON newsletter_sends(draft_id);
CREATE INDEX idx_newsletter_sends_status ON newsletter_sends(status);
CREATE INDEX idx_newsletter_sends_created_at ON newsletter_sends(created_at DESC);
CREATE INDEX idx_newsletter_sends_recipient ON newsletter_sends(recipient_email);

-- Add comment to table
COMMENT ON TABLE newsletter_sends IS 'Newsletter send tracking and email delivery status';

-- Add comments to columns
COMMENT ON COLUMN newsletter_sends.is_test IS 'Whether this is a test send';
COMMENT ON COLUMN newsletter_sends.message_id IS 'Email provider message ID (e.g., Resend)';
COMMENT ON COLUMN newsletter_sends.from_email IS 'Sender email address';
COMMENT ON COLUMN newsletter_sends.from_name IS 'Sender display name';
COMMENT ON COLUMN newsletter_sends.status IS 'Send status: pending, sent, delivered, failed';

-- Verify all columns exist
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'newsletter_sends'
    AND column_name IN (
        'id', 'user_id', 'draft_id', 'recipient_email', 'status', 'is_test',
        'message_id', 'from_email', 'from_name', 'error_message',
        'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
        'created_at', 'updated_at'
    );

    IF col_count = 16 THEN
        RAISE NOTICE 'SUCCESS: newsletter_sends table created with all 16 required columns';
    ELSE
        RAISE EXCEPTION 'ERROR: Expected 16 columns but found %', col_count;
    END IF;
END $$;
