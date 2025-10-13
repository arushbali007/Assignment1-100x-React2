-- Migration 002: Add Style Profiles Table
-- Description: Adds table for storing user writing style profiles from past newsletters

-- Style Profiles Table
CREATE TABLE IF NOT EXISTS style_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    newsletter_text TEXT NOT NULL,
    newsletter_title VARCHAR(500),
    style_data JSONB DEFAULT '{}',
    is_primary BOOLEAN DEFAULT FALSE,
    analyzed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Indexes
CREATE INDEX IF NOT EXISTS idx_style_profiles_user_id ON style_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_style_profiles_is_primary ON style_profiles(is_primary);
CREATE INDEX IF NOT EXISTS idx_style_profiles_created_at ON style_profiles(created_at DESC);

-- Apply Updated At Trigger
CREATE TRIGGER update_style_profiles_updated_at BEFORE UPDATE ON style_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security
ALTER TABLE style_profiles ENABLE ROW LEVEL SECURITY;

-- Style Profiles policies
CREATE POLICY "Users can view own style profiles" ON style_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own style profiles" ON style_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own style profiles" ON style_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own style profiles" ON style_profiles
    FOR DELETE USING (auth.uid() = user_id);

-- Comment
COMMENT ON TABLE style_profiles IS 'Stores user writing style profiles analyzed from past newsletters';
