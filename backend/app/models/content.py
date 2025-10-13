from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID


class ContentType(str, Enum):
    """Content type enum"""
    TWEET = "tweet"
    VIDEO = "video"
    ARTICLE = "article"
    NEWSLETTER = "newsletter"


class ContentCreate(BaseModel):
    """Schema for creating content"""
    source_id: UUID
    content_type: ContentType
    title: Optional[str] = None
    body: Optional[str] = None
    url: HttpUrl
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class ContentUpdate(BaseModel):
    """Schema for updating content"""
    title: Optional[str] = None
    body: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class ContentInDB(BaseModel):
    """Schema for content in database"""
    id: UUID
    user_id: UUID
    source_id: UUID
    content_type: ContentType
    title: Optional[str] = None
    body: Optional[str] = None
    url: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentResponse(BaseModel):
    """Schema for content response"""
    id: UUID
    source_id: UUID
    content_type: ContentType
    title: Optional[str] = None
    body: Optional[str] = None
    url: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class ContentList(BaseModel):
    """Schema for paginated content list"""
    items: list[ContentResponse]
    total: int
    page: int
    page_size: int
    pages: int
