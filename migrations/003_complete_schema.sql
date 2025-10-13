-- Complete CreatorPulse Database Schema
-- Run this migration in Supabase SQL Editor to create all tables

-- ============================================================================
-- USERS TABLE (Already created in 001_initial_schema.sql)
-- ============================================================================
-- CREATE TABLE IF NOT EXISTS users (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     email TEXT UNIQUE NOT NULL,
--     password_hash TEXT NOT NULL,
--     full_name TEXT,
--     timezone TEXT DEFAULT 'UTC',
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- ============================================================================
-- SOURCES TABLE (Already created in 001_initial_schema.sql)
-- ============================================================================
-- CREATE TABLE IF NOT EXISTS sources (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     source_type TEXT NOT NULL,
--     source_url TEXT NOT NULL,
--     source_identifier TEXT,
--     name TEXT NOT NULL,
--     is_active BOOLEAN DEFAULT TRUE,
--     metadata JSONB DEFAULT '{}',
--     last_fetched_at TIMESTAMP WITH TIME ZONE,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- ============================================================================
-- CONTENT TABLE (Already created in 001_initial_schema.sql)
-- ============================================================================
-- CREATE TABLE IF NOT EXISTS content (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
--     content_type TEXT NOT NULL,
--     title TEXT,
--     body TEXT,
--     url TEXT UNIQUE NOT NULL,
--     author TEXT,
--     published_at TIMESTAMP WITH TIME ZONE,
--     metadata JSONB DEFAULT '{}',
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- ============================================================================
-- TRENDS TABLE (Already created in 001_initial_schema.sql)
-- ============================================================================
-- CREATE TABLE IF NOT EXISTS trends (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     keyword TEXT NOT NULL,
--     score DECIMAL(5,2) NOT NULL,
--     google_trends_score DECIMAL(5,2),
--     content_mentions INTEGER DEFAULT 0,
--     velocity DECIMAL(5,2) DEFAULT 0.0,
--     related_content_ids UUID[],
--     detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- ============================================================================
-- STYLE_PROFILES TABLE (Created in 002_add_style_profiles.sql)
-- ============================================================================
CREATE TABLE IF NOT EXISTS style_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    newsletter_text TEXT NOT NULL,
    newsletter_title TEXT,
    style_data JSONB NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    analyzed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes on style_profiles
CREATE INDEX IF NOT EXISTS idx_style_profiles_user_id ON style_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_style_profiles_is_primary ON style_profiles(user_id, is_primary);
CREATE INDEX IF NOT EXISTS idx_style_profiles_created_at ON style_profiles(created_at DESC);

-- ============================================================================
-- DRAFTS TABLE (Already created in 001_initial_schema.sql, but verify columns)
-- ============================================================================
CREATE TABLE IF NOT EXISTS drafts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    html_content TEXT NOT NULL,
    plain_content TEXT NOT NULL,
    content_data JSONB NOT NULL,
    status TEXT DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    notes TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes on drafts
CREATE INDEX IF NOT EXISTS idx_drafts_user_id ON drafts(user_id);
CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status);
CREATE INDEX IF NOT EXISTS idx_drafts_created_at ON drafts(created_at DESC);

-- ============================================================================
-- NEWSLETTER_SENDS TABLE (New in Phase 7)
-- ============================================================================
CREATE TABLE IF NOT EXISTS newsletter_sends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    draft_id UUID NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
    recipient_email TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    is_test BOOLEAN DEFAULT FALSE,
    message_id TEXT,
    from_email TEXT,
    from_name TEXT,
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes on newsletter_sends
CREATE INDEX IF NOT EXISTS idx_newsletter_sends_user_id ON newsletter_sends(user_id);
CREATE INDEX IF NOT EXISTS idx_newsletter_sends_draft_id ON newsletter_sends(draft_id);
CREATE INDEX IF NOT EXISTS idx_newsletter_sends_status ON newsletter_sends(status);
CREATE INDEX IF NOT EXISTS idx_newsletter_sends_created_at ON newsletter_sends(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_newsletter_sends_recipient ON newsletter_sends(recipient_email);

-- ============================================================================
-- FEEDBACK TABLE (Optional - for Phase 8)
-- ============================================================================
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    draft_id UUID REFERENCES drafts(id) ON DELETE CASCADE,
    feedback_type TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    changes_made JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes on feedback
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_draft_id ON feedback(draft_id);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE style_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_sends ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Style Profiles RLS
DROP POLICY IF EXISTS "Users can view their own style profiles" ON style_profiles;
CREATE POLICY "Users can view their own style profiles"
    ON style_profiles FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create their own style profiles" ON style_profiles;
CREATE POLICY "Users can create their own style profiles"
    ON style_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own style profiles" ON style_profiles;
CREATE POLICY "Users can update their own style profiles"
    ON style_profiles FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own style profiles" ON style_profiles;
CREATE POLICY "Users can delete their own style profiles"
    ON style_profiles FOR DELETE
    USING (auth.uid() = user_id);

-- Drafts RLS
DROP POLICY IF EXISTS "Users can view their own drafts" ON drafts;
CREATE POLICY "Users can view their own drafts"
    ON drafts FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create their own drafts" ON drafts;
CREATE POLICY "Users can create their own drafts"
    ON drafts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own drafts" ON drafts;
CREATE POLICY "Users can update their own drafts"
    ON drafts FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own drafts" ON drafts;
CREATE POLICY "Users can delete their own drafts"
    ON drafts FOR DELETE
    USING (auth.uid() = user_id);

-- Newsletter Sends RLS
DROP POLICY IF EXISTS "Users can view their own sends" ON newsletter_sends;
CREATE POLICY "Users can view their own sends"
    ON newsletter_sends FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create their own sends" ON newsletter_sends;
CREATE POLICY "Users can create their own sends"
    ON newsletter_sends FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own sends" ON newsletter_sends;
CREATE POLICY "Users can update their own sends"
    ON newsletter_sends FOR UPDATE
    USING (auth.uid() = user_id);

-- Feedback RLS
DROP POLICY IF EXISTS "Users can view their own feedback" ON feedback;
CREATE POLICY "Users can view their own feedback"
    ON feedback FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create their own feedback" ON feedback;
CREATE POLICY "Users can create their own feedback"
    ON feedback FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- TRIGGERS FOR AUTO-UPDATING TIMESTAMPS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to tables with updated_at
DROP TRIGGER IF EXISTS update_style_profiles_updated_at ON style_profiles;
CREATE TRIGGER update_style_profiles_updated_at
    BEFORE UPDATE ON style_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_drafts_updated_at ON drafts;
CREATE TRIGGER update_drafts_updated_at
    BEFORE UPDATE ON drafts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_newsletter_sends_updated_at ON newsletter_sends;
CREATE TRIGGER update_newsletter_sends_updated_at
    BEFORE UPDATE ON newsletter_sends
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Run these to verify tables were created successfully:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
-- SELECT tablename, indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname;
