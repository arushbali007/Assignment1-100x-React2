from supabase import create_client, Client
from app.core.config import settings

# Initialize Supabase client (anon key - respects RLS)
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Initialize Supabase admin client (service key - bypasses RLS)
# Use this for operations like user registration that need to bypass RLS
supabase_admin: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
)


def get_supabase() -> Client:
    """
    Dependency to get Supabase client instance (anon key)
    """
    return supabase


def get_supabase_admin() -> Client:
    """
    Dependency to get Supabase admin client instance (service key)
    Use for operations that need to bypass RLS
    """
    return supabase_admin
