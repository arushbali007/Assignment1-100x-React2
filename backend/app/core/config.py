from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "CreatorPulse"
    APP_ENV: str = "development"
    SECRET_KEY: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # Groq Cloud
    GROQ_API_KEY: str

    # Resend
    RESEND_API_KEY: str
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"  # Default Resend test email
    RESEND_WEBHOOK_SECRET: Optional[str] = None  # For webhook signature verification

    # Twitter API (optional)
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None

    # YouTube API (optional)
    YOUTUBE_API_KEY: Optional[str] = None

    # JWT Settings
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        # Look for .env in the project root (parent of backend/)
        env_file = str(Path(__file__).parent.parent.parent.parent / ".env")
        case_sensitive = True


settings = Settings()
