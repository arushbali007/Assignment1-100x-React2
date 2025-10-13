from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


class TrendCreate(BaseModel):
    """Schema for creating a trend"""
    keyword: str
    score: float = Field(ge=0, le=100, description="Trend score 0-100")
    google_trends_score: Optional[float] = Field(None, ge=0, le=100)
    content_mentions: int = Field(ge=0, description="Number of content mentions")
    velocity: Optional[float] = Field(None, description="Rate of change in mentions")
    related_content_ids: List[UUID] = Field(default_factory=list)
    metadata: Optional[dict] = Field(default_factory=dict)


class TrendUpdate(BaseModel):
    """Schema for updating a trend"""
    score: Optional[float] = Field(None, ge=0, le=100)
    google_trends_score: Optional[float] = Field(None, ge=0, le=100)
    content_mentions: Optional[int] = Field(None, ge=0)
    velocity: Optional[float] = None
    related_content_ids: Optional[List[UUID]] = None
    metadata: Optional[dict] = None


class TrendInDB(BaseModel):
    """Schema for trend in database"""
    id: UUID
    user_id: UUID
    keyword: str
    score: float
    google_trends_score: Optional[float] = None
    content_mentions: int
    velocity: Optional[float] = None
    related_content_ids: List[UUID]
    metadata: Optional[dict] = None
    detected_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrendResponse(BaseModel):
    """Schema for trend response"""
    id: UUID
    keyword: str
    score: float
    google_trends_score: Optional[float] = None
    content_mentions: int
    velocity: Optional[float] = None
    related_content_ids: List[UUID]
    metadata: Optional[dict] = None
    detected_at: datetime
    created_at: datetime


class TrendList(BaseModel):
    """Schema for paginated trend list"""
    items: List[TrendResponse]
    total: int
    page: int
    page_size: int
    pages: int


class TrendStats(BaseModel):
    """Schema for trend statistics"""
    total_trends: int
    active_trends: int
    avg_score: float
    top_keywords: List[str]
