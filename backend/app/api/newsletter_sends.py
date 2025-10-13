from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_user
from app.core.database import get_supabase as get_db
from app.models.user import UserInDB
from app.models.newsletter_send import (
    SendCreate, BulkSendCreate, SendUpdate,
    NewsletterSendResponse, SendListResponse, SendStats,
    SendStatus, BulkSendResult
)
from app.services.newsletter_send_service import NewsletterSendService

router = APIRouter(prefix="/api/newsletter-sends", tags=["newsletter-sends"])


@router.post("/send", response_model=NewsletterSendResponse)
async def send_newsletter(
    send_request: SendCreate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Send newsletter to a single recipient

    - Sends email via Resend
    - Tracks send status
    - Updates draft status to 'sent'
    - Supports test sends with [TEST] prefix
    """
    service = NewsletterSendService(db)

    try:
        send_record = await service.send_newsletter(
            user_id=str(current_user.id),  # Convert UUID to string
            send_request=send_request
        )
        return send_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send newsletter: {str(e)}")


@router.post("/send-bulk", response_model=BulkSendResult)
async def send_bulk_newsletter(
    bulk_request: BulkSendCreate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Send newsletter to multiple recipients

    - Sends to all recipients in list
    - Returns success/failure counts
    - Tracks individual send records
    """
    service = NewsletterSendService(db)

    try:
        result = await service.send_bulk(
            user_id=str(current_user.id),  # Convert UUID to string
            bulk_request=bulk_request
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send bulk newsletter: {str(e)}")


@router.get("/", response_model=SendListResponse)
async def get_sends(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status: Optional[SendStatus] = None,
    draft_id: Optional[str] = None,
    is_test: Optional[bool] = None,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Get paginated list of newsletter sends

    - Filter by status, draft_id, or test flag
    - Ordered by creation date (newest first)
    """
    service = NewsletterSendService(db)
    return await service.get_sends(
        user_id=str(current_user.id),  # Convert UUID to string
        page=page,
        page_size=page_size,
        status=status,
        draft_id=draft_id,
        is_test=is_test
    )


@router.get("/stats", response_model=SendStats)
async def get_send_stats(
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Get newsletter send statistics

    - Total sends
    - Success/failure counts
    - Open and click rates
    - Last send date
    """
    service = NewsletterSendService(db)
    return await service.get_stats(user_id=str(current_user.id))  # Convert UUID to string


@router.get("/{send_id}", response_model=NewsletterSendResponse)
async def get_send(
    send_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get specific newsletter send by ID"""
    service = NewsletterSendService(db)
    send = await service.get_send(
        send_id=send_id,
        user_id=str(current_user.id)  # Convert UUID to string
    )

    if not send:
        raise HTTPException(status_code=404, detail="Send not found")

    return send


@router.patch("/{send_id}", response_model=NewsletterSendResponse)
async def update_send(
    send_id: str,
    update: SendUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Update send record

    - Update status
    - Track delivery, open, click events
    - Record error messages
    """
    service = NewsletterSendService(db)
    send = await service.update_send(
        send_id=send_id,
        user_id=str(current_user.id),  # Convert UUID to string
        update=update
    )

    if not send:
        raise HTTPException(status_code=404, detail="Send not found")

    return send
