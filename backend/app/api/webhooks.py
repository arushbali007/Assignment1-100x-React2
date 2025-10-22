"""
Webhook endpoints for external service events
"""
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import hmac
import hashlib
import os
from datetime import datetime

from app.core.database import get_db_client
from app.services.newsletter_send_service import NewsletterSendService

router = APIRouter()


def verify_resend_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify Resend webhook signature
    Resend uses HMAC SHA256 for webhook signatures
    """
    if not secret:
        # If no secret configured, skip verification (development mode)
        return True

    try:
        # Compute expected signature
        expected_sig = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Compare signatures (constant time comparison)
        return hmac.compare_digest(signature, expected_sig)
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False


@router.post("/resend")
async def resend_webhook(
    request: Request,
    svix_id: Optional[str] = Header(None),
    svix_timestamp: Optional[str] = Header(None),
    svix_signature: Optional[str] = Header(None)
):
    """
    Handle Resend webhook events for email tracking

    Supported events:
    - email.delivered
    - email.opened
    - email.clicked
    - email.bounced
    - email.complained
    """
    # Get webhook secret from environment
    webhook_secret = os.getenv("RESEND_WEBHOOK_SECRET", "")

    # Read raw body for signature verification
    body = await request.body()

    # Verify signature if secret is configured
    if webhook_secret and svix_signature:
        if not verify_resend_signature(body, svix_signature, webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Parse JSON payload
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

    # Extract event type and data
    event_type = payload.get("type")
    data = payload.get("data", {})

    if not event_type:
        raise HTTPException(status_code=400, detail="Missing event type")

    # Get message ID from event
    message_id = data.get("email_id") or data.get("id")

    if not message_id:
        print(f"Warning: No message_id in webhook event: {event_type}")
        return {"status": "ignored", "reason": "no_message_id"}

    # Get database client
    db = get_db_client()
    send_service = NewsletterSendService()

    # Handle different event types
    try:
        if event_type == "email.delivered":
            # Update delivered timestamp
            await send_service.update_from_webhook(
                message_id=message_id,
                event_type="delivered",
                timestamp=datetime.utcnow()
            )
            return {"status": "success", "event": "delivered"}

        elif event_type == "email.opened":
            # Update opened timestamp
            await send_service.update_from_webhook(
                message_id=message_id,
                event_type="opened",
                timestamp=datetime.utcnow()
            )
            return {"status": "success", "event": "opened"}

        elif event_type == "email.clicked":
            # Update clicked timestamp
            await send_service.update_from_webhook(
                message_id=message_id,
                event_type="clicked",
                timestamp=datetime.utcnow()
            )
            return {"status": "success", "event": "clicked"}

        elif event_type == "email.bounced":
            # Update status to bounced
            await send_service.update_from_webhook(
                message_id=message_id,
                event_type="bounced",
                timestamp=datetime.utcnow()
            )
            return {"status": "success", "event": "bounced"}

        elif event_type == "email.complained":
            # Update status to complained/spam
            await send_service.update_from_webhook(
                message_id=message_id,
                event_type="complained",
                timestamp=datetime.utcnow()
            )
            return {"status": "success", "event": "complained"}

        else:
            # Unknown event type, log and ignore
            print(f"Unknown webhook event type: {event_type}")
            return {"status": "ignored", "reason": "unknown_event_type"}

    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {e}")


@router.get("/health")
async def webhook_health():
    """Health check endpoint for webhooks"""
    return {"status": "healthy", "service": "webhooks"}
