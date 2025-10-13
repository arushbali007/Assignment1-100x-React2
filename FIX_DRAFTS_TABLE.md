# Fix Drafts Table - Step by Step Guide

## Problem
The `drafts` table is missing required columns (`subject`, `html_content`, `plain_content`), which means it wasn't created properly by migration 003.

## Solution: Run Migrations in Supabase SQL Editor

### Step 1: Check Current State
1. Go to Supabase Dashboard: https://supabase.com/dashboard
2. Navigate to: **SQL Editor**
3. Create a new query
4. Copy and paste the contents of: `migrations/011_verify_all_tables.sql`
5. Run the query
6. Check the output to see which tables exist and what columns the drafts table has (if any)

### Step 2: Create Drafts Table
1. In SQL Editor, create a new query
2. Copy and paste the contents of: `migrations/010_create_drafts_table.sql`
3. Run the query
4. You should see: `SUCCESS: drafts table created with all 13 required columns`

**Note:** This will DROP the existing drafts table and recreate it with all required columns. If you have any existing drafts, they will be lost. Since this is a fresh setup, this should be fine.

### Step 3: Reload Schema Cache
After creating the table, reload PostgREST's schema cache:

**Option A: Via Dashboard**
1. Navigate to: **Database** → **Replication**
2. Click **"Reload schema cache"** button

**Option B: Via SQL**
1. In SQL Editor, run:
```sql
NOTIFY pgrst, 'reload schema';
```

### Step 4: Verify the Fix
Run the test script:
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

### Step 5: Test Draft Generation
1. Go back to your Streamlit app
2. Try generating a newsletter draft again
3. It should work correctly now!

---

## What Went Wrong?

Looking at your migrations:
- `001_initial_schema.sql` - Created basic tables (users, sources, content)
- `002_add_style_profiles.sql` - Added style_profiles table
- `003_complete_schema.sql` - Should have created drafts table

It seems migration 003 either:
1. Wasn't run in Supabase, OR
2. Failed partially, OR
3. The drafts table was created but PostgREST doesn't see it

Migration 010 will fix this by explicitly creating the drafts table with all required columns.

---

## Migration Files to Run (in order)

1. **`migrations/011_verify_all_tables.sql`** - Check current state (diagnostic)
2. **`migrations/010_create_drafts_table.sql`** - Create drafts table properly
3. **Reload schema cache** - Via dashboard or NOTIFY command

---

## After Fixing

Once the drafts table is created and schema cache is reloaded:
- ✓ Draft generation will work
- ✓ You can save generated newsletters
- ✓ You can view, edit, and send drafts
- ✓ The complete workflow will be functional
