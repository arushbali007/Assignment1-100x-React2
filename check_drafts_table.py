#!/usr/bin/env python3
"""Check drafts table schema"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Create client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Try to query the drafts table
try:
    result = supabase.table("drafts").select("*").limit(1).execute()
    print(f"✓ drafts table exists")
    print(f"  Columns found in response: {result.data}")
except Exception as e:
    print(f"✗ Error querying drafts table: {e}")

# Try to insert a test record to see which columns are missing
print("\nAttempting test insert to check columns...")
try:
    test_data = {
        "user_id": "00000000-0000-0000-0000-000000000000",
        "subject": "Test",
        "html_content": "Test",
        "plain_content": "Test",
        "content_data": {"test": "data"},
        "status": "pending",
        "metadata": {}
    }
    result = supabase.table("drafts").insert(test_data).execute()
    print(f"✓ Test insert successful")
    # Clean up
    if result.data:
        supabase.table("drafts").delete().eq("id", result.data[0]["id"]).execute()
except Exception as e:
    print(f"✗ Test insert failed: {e}")
