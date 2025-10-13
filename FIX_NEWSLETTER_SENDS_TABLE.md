# Fix Newsletter Sends Table

## Problem
The `newsletter_sends` table is missing columns in PostgREST's schema cache, causing this error:
```
Could not find the 'from_email' column of 'newsletter_sends' in the schema cache
```

This is the same schema cache issue we had with the `drafts` table.

## Solution: Run Migration in Supabase SQL Editor

### Step 1: Create newsletter_sends Table
1. Go to Supabase Dashboard: https://supabase.com/dashboard
2. Navigate to: **SQL Editor**
3. Create a new query
4. Copy and paste the contents of: `migrations/012_create_newsletter_sends_table.sql`
5. Run the query
6. Expected output: `SUCCESS: newsletter_sends table created with all 16 required columns`

**Note:** This will DROP and recreate the newsletter_sends table. Any existing send records will be lost (which is fine for initial setup).

### Step 2: Reload Schema Cache
After creating the table, reload PostgREST's schema cache:

**Option A: Via Dashboard**
1. Navigate to: **Database** → **Replication**
2. Click **"Reload schema cache"** button

**Option B: Via SQL**
1. In SQL Editor, run:
```sql
NOTIFY pgrst, 'reload schema';
```

### Step 3: Verify the Fix
The newsletter_sends table should now have these 16 columns:
- `id`, `user_id`, `draft_id`
- `recipient_email`, `status`, `is_test`
- `message_id`, `from_email`, `from_name`
- `error_message`
- `sent_at`, `delivered_at`, `opened_at`, `clicked_at`
- `created_at`, `updated_at`

### Step 4: Test Email Sending
1. Go back to Streamlit app
2. Navigate to **Drafts** page
3. Click **"👁️ Preview"** on your draft
4. Scroll to **"📧 Send Newsletter"** section
5. Enter a test email address
6. Make sure **"Send as Test"** is checked
7. Click **"🧪 Send Test Email"**
8. Should work successfully! 🎉

---

## Why This Happened

Both `drafts` and `newsletter_sends` tables were defined in migration `003_complete_schema.sql`, but PostgREST's schema cache wasn't refreshed after the migrations ran. PostgREST caches the database schema for performance, so it needs to be explicitly notified when schema changes occur.

## What Tables Are Created Now

After running all migrations, you should have these tables:
- ✅ `users` - User accounts
- ✅ `sources` - Content sources (Twitter, YouTube, RSS, etc.)
- ✅ `content` - Aggregated content
- ✅ `trends` - Detected trending topics
- ✅ `style_profiles` - Writing style analysis
- ✅ `drafts` - Generated newsletter drafts
- ✅ `newsletter_sends` - Email send tracking

All tables should be visible to PostgREST after reloading the schema cache.

---

## Important Note About Resend API

To actually send emails, you need:
1. Valid **RESEND_API_KEY** in your `.env` file
2. Verified sender email in Resend dashboard
3. Default sender: `onboarding@resend.dev` (works in dev mode)
4. For production: Add and verify your own domain in Resend

If you don't have Resend configured, the email send will fail with an API error, but the database operations should work.
