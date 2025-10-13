# PostgREST Schema Cache Issue - Fix Required

## Problem
The `drafts` table columns exist in the database but PostgREST's schema cache is stale, causing this error:
```
Could not find the 'content_data' column of 'drafts' in the schema cache
```

## Solution: Reload PostgREST Schema Cache in Supabase

### Option 1: Via Supabase Dashboard (Recommended)
1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Navigate to **Database** → **Replication**
4. Click **Reload schema cache** button

OR

### Option 2: Via Supabase API Settings
1. Go to **Settings** → **API**
2. Look for "Reload schema" or similar button
3. Click to refresh the PostgREST schema cache

OR

### Option 3: Via SQL Editor
1. Go to **SQL Editor** in Supabase Dashboard
2. Run this SQL command:
```sql
NOTIFY pgrst, 'reload schema';
```

OR manually run the migration `migrations/009_ensure_drafts_columns.sql` in the SQL Editor.

### Option 4: Restart PostgREST
Some Supabase plans allow you to restart services:
1. Go to **Settings** → **Infrastructure**
2. Look for PostgREST service
3. Click restart

---

## Why This Happened
The `drafts` table was created in migration `003_complete_schema.sql`, but PostgREST caches the schema and doesn't automatically detect new columns. This is a common issue when:
- Running migrations outside of Supabase's migration system
- Schema changes are made directly via SQL without notifying PostgREST
- The cache hasn't been refreshed after schema changes

## After Fixing
Once you've reloaded the schema cache, the draft generation should work correctly.

## Verify Fix
Run this command to verify the fix worked:
```bash
cd /Users/arushbali/Downloads/Assignment
source venv/bin/activate
python check_drafts_table.py
```

You should see:
```
✓ drafts table exists
✓ Test insert successful
```
