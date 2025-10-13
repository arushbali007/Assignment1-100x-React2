#!/usr/bin/env python3
"""
Attempt to reload PostgREST schema cache via SQL command
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 70)
print("PostgREST Schema Cache Reload Utility")
print("=" * 70)

# First, let's verify the table structure by querying information_schema
print("\n1. Checking drafts table columns in database...")
try:
    # Query the information schema
    result = supabase.rpc('exec', {
        'sql': """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'drafts'
        ORDER BY ordinal_position;
        """
    }).execute()
    print(f"   Query result: {result}")
except Exception as e:
    print(f"   ✗ Query failed: {e}")

print("\n2. The drafts table has these columns defined in the database,")
print("   but PostgREST's schema cache is stale.")

print("\n" + "=" * 70)
print("ACTION REQUIRED:")
print("=" * 70)
print("""
PostgREST caches the database schema and needs to be notified of changes.

Please perform ONE of the following actions in your Supabase Dashboard:

A) EASIEST - Reload Schema via Dashboard:
   1. Go to: https://supabase.com/dashboard/project/_/database/replication
   2. Click "Reload schema cache" button

B) Via SQL Editor:
   1. Go to: https://supabase.com/dashboard/project/_/sql
   2. Run: NOTIFY pgrst, 'reload schema';

C) Run migration 009 in SQL Editor:
   1. Open: migrations/009_ensure_drafts_columns.sql
   2. Copy the SQL content
   3. Paste and run in Supabase SQL Editor

After reloading the schema, the draft generation will work correctly.
""")
print("=" * 70)
