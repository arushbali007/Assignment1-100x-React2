# Database Migrations

## How to Run Migrations

### Step 1: Open Supabase SQL Editor
1. Go to your Supabase Dashboard: https://app.supabase.com/
2. Select your project
3. Click on "SQL Editor" in the left sidebar

### Step 2: Run the Initial Schema Migration
1. Click "New Query"
2. Copy the entire content of `001_initial_schema.sql`
3. Paste it into the SQL Editor
4. Click "Run" or press `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (Mac)

### Step 3: Run Additional Migrations
Run migrations in order:
1. `002_add_style_profiles.sql` - Adds style_profiles table for Phase 5

### Step 4: Verify Tables Created
After running the migrations, verify that all tables were created:
- Go to "Table Editor" in the left sidebar
- You should see: users, sources, content, trends, drafts, feedback, newsletter_sends, style_profiles

## Schema Overview

### Tables Created:
1. **users** - User accounts and preferences
2. **sources** - Content sources (Twitter, YouTube, RSS)
3. **content** - Fetched content from sources
4. **trends** - Detected trending topics
5. **style_profiles** - User writing style analysis (Phase 5)
6. **drafts** - Generated newsletter drafts
7. **feedback** - User feedback on drafts
8. **newsletter_sends** - Email delivery tracking

### Features:
- ✅ UUID primary keys
- ✅ Foreign key relationships with CASCADE delete
- ✅ Timestamps (created_at, updated_at)
- ✅ Automatic updated_at triggers
- ✅ Indexes for performance
- ✅ Row Level Security (RLS) enabled
- ✅ JSONB fields for flexible metadata

## Notes
- All tables use UUID for primary keys
- RLS policies ensure users can only access their own data
- Timestamps are in UTC with timezone support
- JSONB fields allow flexible schema evolution
