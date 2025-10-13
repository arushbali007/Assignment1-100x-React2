"""Style Profile Models"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class StyleProfileCreate(BaseModel):
    """Schema for creating a style profile"""
    newsletter_text: str = Field(..., min_length=100, description="Text content of past newsletter")
    newsletter_title: Optional[str] = Field(None, description="Title of the newsletter")


class StyleProfileUpdate(BaseModel):
    """Schema for updating a style profile"""
    style_data: Optional[Dict[str, Any]] = Field(None, description="Analyzed style data")
    is_primary: Optional[bool] = Field(None, description="Whether this is the primary style profile")


class StyleAnalysis(BaseModel):
    """Schema for analyzed style data"""
    tone: str = Field(..., description="Overall tone (e.g., professional, casual, witty)")
    voice: str = Field(..., description="Voice characteristics")
    sentence_structure: str = Field(..., description="Typical sentence structure patterns")
    vocabulary_level: str = Field(..., description="Vocabulary complexity level")
    opening_style: str = Field(..., description="How newsletters typically open")
    closing_style: str = Field(..., description="How newsletters typically close")
    formatting_preferences: str = Field(..., description="Preferred formatting patterns")
    use_of_humor: str = Field(..., description="Level and type of humor used")
    call_to_action_style: str = Field(..., description="How CTAs are presented")
    personal_touches: str = Field(..., description="Personal elements or signatures")
    avg_sentence_length: Optional[float] = Field(None, description="Average sentence length")
    avg_paragraph_length: Optional[float] = Field(None, description="Average paragraph length")
    key_phrases: Optional[list[str]] = Field(default_factory=list, description="Frequently used phrases")


class StyleProfileResponse(BaseModel):
    """Schema for style profile response"""
    id: str
    user_id: str
    newsletter_text: str
    newsletter_title: Optional[str] = None
    style_data: Optional[Dict[str, Any]] = None
    is_primary: bool = False
    analyzed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StyleProfileList(BaseModel):
    """Schema for paginated style profile list"""
    profiles: list[StyleProfileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class StyleSummary(BaseModel):
    """Schema for aggregated style summary"""
    user_id: str
    tone: str
    voice: str
    key_characteristics: list[str]
    avg_sentence_length: float
    avg_paragraph_length: float
    common_phrases: list[str]
    style_confidence: float = Field(..., ge=0, le=1, description="Confidence score based on number of samples")
    sample_count: int = Field(..., description="Number of newsletters analyzed")
