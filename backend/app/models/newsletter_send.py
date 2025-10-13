from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class SendStatus(str, Enum):
    """Status of newsletter send"""
    PENDING = "pending"        # Queued for sending
    SENDING = "sending"        # Currently being sent
    SENT = "sent"             # Successfully sent
    FAILED = "failed"         # Send failed
    BOUNCED = "bounced"       # Email bounced
    DELIVERED = "delivered"   # Confirmed delivered
    OPENED = "opened"         # Email opened (if tracking enabled)
    CLICKED = "clicked"       # Link clicked (if tracking enabled)


class SendCreate(BaseModel):
    """Request to send newsletter"""
    draft_id: str = Field(..., description="Draft ID to send")
    recipient_email: EmailStr = Field(..., description="Recipient email address")
    is_test: bool = Field(False, description="Whether this is a test send")
    from_email: Optional[str] = Field(None, description="Custom from email")
    from_name: Optional[str] = Field(None, description="Custom from name")


class BulkSendCreate(BaseModel):
    """Request to send newsletter to multiple recipients"""
    draft_id: str = Field(..., description="Draft ID to send")
    recipient_emails: List[EmailStr] = Field(..., description="List of recipient emails")
    from_email: Optional[str] = Field(None, description="Custom from email")
    from_name: Optional[str] = Field(None, description="Custom from name")


class SendUpdate(BaseModel):
    """Update newsletter send status"""
    status: Optional[SendStatus] = None
    error_message: Optional[str] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None


class NewsletterSendResponse(BaseModel):
    """Newsletter send response"""
    id: str
    user_id: str
    draft_id: str
    recipient_email: str
    status: SendStatus
    is_test: bool
    message_id: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SendListResponse(BaseModel):
    """Paginated send list response"""
    sends: List[NewsletterSendResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class SendStats(BaseModel):
    """Newsletter send statistics"""
    total_sends: int = 0
    successful_sends: int = 0
    failed_sends: int = 0
    test_sends: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    last_send_date: Optional[datetime] = None


class BulkSendResult(BaseModel):
    """Result of bulk send operation"""
    total: int
    successful: int
    failed: int
    send_ids: List[str] = []
    errors: List[dict] = []
