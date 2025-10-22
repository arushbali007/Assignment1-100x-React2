from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class DraftStatus(str, Enum):
    """Status of newsletter draft"""
    PENDING = "pending"      # Draft generated, awaiting review
    REVIEWED = "reviewed"    # User reviewed and approved
    EDITED = "edited"        # User made edits
    SENT = "sent"           # Newsletter sent via email
    ARCHIVED = "archived"    # Archived without sending


class NewsletterBlock(BaseModel):
    """Individual content block in newsletter"""
    title: str = Field(..., description="Block title/heading")
    content: str = Field(..., description="Block content/body")
    source_ids: List[str] = Field(default_factory=list, description="Related content IDs")
    trend_id: Optional[str] = Field(None, description="Related trend ID if applicable")


class DraftContent(BaseModel):
    """Structured newsletter content"""
    subject: str = Field(..., description="Email subject line")
    greeting: str = Field(..., description="Newsletter opening/greeting")
    intro: str = Field(..., description="Introduction paragraph")
    blocks: List[NewsletterBlock] = Field(..., description="Main content blocks")
    trends_section: Optional[NewsletterBlock] = Field(None, description="'Trends to Watch' section")
    closing: str = Field(..., description="Closing paragraph")
    cta: Optional[str] = Field(None, description="Call to action")
    signature: str = Field(..., description="Sign-off and signature")


class DraftMetadata(BaseModel):
    """Metadata about draft generation"""
    generation_time_seconds: Optional[float] = None
    trends_used: List[str] = Field(default_factory=list)
    content_items_used: int = 0
    style_profile_id: Optional[str] = None
    model_name: str = "llama-3.3-70b-versatile"


class DraftCreate(BaseModel):
    """Request to generate a new draft"""
    force_regenerate: bool = Field(False, description="Force regeneration even if today's draft exists")
    include_trends: bool = Field(True, description="Include trends section")
    max_trends: int = Field(3, description="Maximum trends to include")


class DraftUpdate(BaseModel):
    """Update draft content or status"""
    status: Optional[DraftStatus] = None
    subject: Optional[str] = None
    html_content: Optional[str] = None
    plain_content: Optional[str] = None
    content_data: Optional[DraftContent] = None
    notes: Optional[str] = None


class DraftResponse(BaseModel):
    """Newsletter draft response"""
    id: str
    user_id: str
    subject: str
    html_content: str
    plain_content: str
    content_data: DraftContent
    status: DraftStatus
    metadata: DraftMetadata
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DraftListResponse(BaseModel):
    """Paginated draft list response"""
    drafts: List[DraftResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class DraftStats(BaseModel):
    """Draft statistics"""
    total_drafts: int = 0
    pending_drafts: int = 0
    reviewed_drafts: int = 0
    sent_drafts: int = 0
    archived_drafts: int = 0
    last_draft_date: Optional[datetime] = None
    avg_generation_time: Optional[float] = None
    avg_review_time_minutes: Optional[float] = None
