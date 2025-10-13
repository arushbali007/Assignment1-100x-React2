"""
Source models for content aggregation
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator, HttpUrl


class SourceType(str, Enum):
    """Supported source types"""
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    RSS = "rss"
    NEWSLETTER = "newsletter"


class SourceBase(BaseModel):
    """Base source schema"""
    source_type: SourceType
    source_url: str = Field(..., max_length=500)
    source_identifier: Optional[str] = Field(None, max_length=255)
    name: str = Field(..., max_length=255)
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('source_url')
    def validate_source_url(cls, v, values):
        """Validate URL based on source type"""
        if not v:
            raise ValueError("source_url is required")

        # Basic URL validation
        v = v.strip()

        if 'source_type' in values:
            source_type = values['source_type']

            # Twitter validation
            if source_type == SourceType.TWITTER:
                if not any(domain in v.lower() for domain in ['twitter.com', 'x.com']):
                    raise ValueError("Twitter URL must contain twitter.com or x.com")

            # YouTube validation
            elif source_type == SourceType.YOUTUBE:
                if not any(domain in v.lower() for domain in ['youtube.com', 'youtu.be']):
                    raise ValueError("YouTube URL must contain youtube.com or youtu.be")

            # RSS validation
            elif source_type == SourceType.RSS:
                if not v.startswith(('http://', 'https://')):
                    raise ValueError("RSS feed URL must start with http:// or https://")

            # Newsletter validation
            elif source_type == SourceType.NEWSLETTER:
                if not v.startswith(('http://', 'https://')):
                    raise ValueError("Newsletter URL must start with http:// or https://")

        return v

    @validator('source_identifier')
    def extract_identifier(cls, v, values):
        """Extract identifier from URL if not provided"""
        if v:
            return v

        if 'source_url' not in values or 'source_type' not in values:
            return v

        url = values['source_url']
        source_type = values['source_type']

        # Extract Twitter handle
        if source_type == SourceType.TWITTER:
            # Extract @username from URL like twitter.com/username or x.com/username
            parts = url.rstrip('/').split('/')
            if len(parts) > 0:
                username = parts[-1]
                if username and username not in ['twitter.com', 'x.com']:
                    return f"@{username}" if not username.startswith('@') else username

        # Extract YouTube channel ID
        elif source_type == SourceType.YOUTUBE:
            # Extract channel ID from URL like youtube.com/@channelname or youtube.com/channel/ID
            if '@' in url:
                parts = url.split('@')
                if len(parts) > 1:
                    return '@' + parts[1].split('/')[0].split('?')[0]
            elif '/channel/' in url:
                parts = url.split('/channel/')
                if len(parts) > 1:
                    return parts[1].split('/')[0].split('?')[0]

        return v

    class Config:
        use_enum_values = True


class SourceCreate(SourceBase):
    """Schema for creating a new source"""
    pass


class SourceUpdate(BaseModel):
    """Schema for updating a source"""
    source_url: Optional[str] = Field(None, max_length=500)
    source_identifier: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class SourceInDB(SourceBase):
    """Schema for source in database"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SourceResponse(BaseModel):
    """Schema for source response"""
    id: UUID
    source_type: str
    source_url: str
    source_identifier: Optional[str]
    name: str
    is_active: bool
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SourceListResponse(BaseModel):
    """Schema for paginated source list response"""
    sources: list[SourceResponse]
    total: int
    page: int = 1
    page_size: int = 50
