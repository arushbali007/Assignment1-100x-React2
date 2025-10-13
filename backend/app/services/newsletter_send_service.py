from typing import Optional, List
from datetime import datetime
from supabase import Client

from app.models.newsletter_send import (
    NewsletterSendResponse, SendCreate, BulkSendCreate, SendUpdate,
    SendListResponse, SendStats, SendStatus, BulkSendResult
)
from app.services.email_service import EmailService
from app.services.draft_service import DraftService
from app.models.draft import DraftStatus


class NewsletterSendService:
    """Manage newsletter sends"""

    def __init__(self, db: Client):
        self.db = db
        self.email_service = EmailService()
        self.draft_service = DraftService(db)

    async def send_newsletter(
        self,
        user_id: str,
        send_request: SendCreate
    ) -> NewsletterSendResponse:
        """
        Send newsletter to a single recipient

        Args:
            user_id: User ID
            send_request: Send request details

        Returns:
            Newsletter send record
        """
        # Get draft
        draft = await self.draft_service.get_draft(send_request.draft_id, user_id)
        if not draft:
            raise Exception("Draft not found")

        # Validate email
        if not self.email_service.validate_email(send_request.recipient_email):
            raise Exception("Invalid recipient email address")

        # Create send record
        send_data = {
            "user_id": user_id,
            "draft_id": send_request.draft_id,
            "recipient_email": send_request.recipient_email,
            "status": SendStatus.PENDING.value,
            "is_test": send_request.is_test,
            "from_email": send_request.from_email,
            "from_name": send_request.from_name,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        response = self.db.table("newsletter_sends").insert(send_data).execute()

        if not response.data:
            raise Exception("Failed to create send record")

        send_record = self._map_to_response(response.data[0])

        # Send email
        try:
            # Update status to sending
            await self._update_send_status(send_record.id, SendStatus.SENDING)

            # Send via email service
            if send_request.is_test:
                result = await self.email_service.send_test_email(
                    to_email=send_request.recipient_email,
                    draft_subject=draft.subject,
                    draft_html=draft.html_content,
                    draft_plain=draft.plain_content
                )
            else:
                result = await self.email_service.send_newsletter(
                    to_email=send_request.recipient_email,
                    subject=draft.subject,
                    html_content=draft.html_content,
                    plain_content=draft.plain_content,
                    from_email=send_request.from_email,
                    from_name=send_request.from_name
                )

            # Update send record with success
            update_data = {
                "status": SendStatus.SENT.value,
                "message_id": result.get("message_id"),
                "sent_at": result.get("sent_at"),
                "updated_at": datetime.utcnow().isoformat()
            }

            update_response = self.db.table("newsletter_sends").update(
                update_data
            ).eq("id", send_record.id).execute()

            # Update draft status to sent if not test
            if not send_request.is_test and draft.status != DraftStatus.SENT:
                await self.draft_service.update_draft(
                    draft_id=send_request.draft_id,
                    user_id=user_id,
                    update={"status": DraftStatus.SENT}
                )

            return self._map_to_response(update_response.data[0])

        except Exception as e:
            # Update send record with failure
            error_message = str(e)
            update_data = {
                "status": SendStatus.FAILED.value,
                "error_message": error_message,
                "updated_at": datetime.utcnow().isoformat()
            }

            self.db.table("newsletter_sends").update(
                update_data
            ).eq("id", send_record.id).execute()

            raise Exception(f"Failed to send newsletter: {error_message}")

    async def send_bulk(
        self,
        user_id: str,
        bulk_request: BulkSendCreate
    ) -> BulkSendResult:
        """
        Send newsletter to multiple recipients

        Args:
            user_id: User ID
            bulk_request: Bulk send request

        Returns:
            Bulk send result
        """
        # Get draft
        draft = await self.draft_service.get_draft(bulk_request.draft_id, user_id)
        if not draft:
            raise Exception("Draft not found")

        result = BulkSendResult(
            total=len(bulk_request.recipient_emails),
            successful=0,
            failed=0
        )

        for email in bulk_request.recipient_emails:
            try:
                send_request = SendCreate(
                    draft_id=bulk_request.draft_id,
                    recipient_email=email,
                    is_test=False,
                    from_email=bulk_request.from_email,
                    from_name=bulk_request.from_name
                )

                send_record = await self.send_newsletter(user_id, send_request)
                result.successful += 1
                result.send_ids.append(send_record.id)

            except Exception as e:
                result.failed += 1
                result.errors.append({
                    "email": email,
                    "error": str(e)
                })

        return result

    async def get_sends(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
        status: Optional[SendStatus] = None,
        draft_id: Optional[str] = None,
        is_test: Optional[bool] = None
    ) -> SendListResponse:
        """Get user's newsletter sends with pagination"""
        offset = (page - 1) * page_size

        # Build query
        query = self.db.table("newsletter_sends").select("*", count="exact").eq("user_id", user_id)

        if status:
            query = query.eq("status", status.value)

        if draft_id:
            query = query.eq("draft_id", draft_id)

        if is_test is not None:
            query = query.eq("is_test", is_test)

        # Get total count
        count_response = query.execute()
        total = count_response.count if count_response.count else 0

        # Get paginated data
        response = query.order(
            "created_at", desc=True
        ).range(offset, offset + page_size - 1).execute()

        sends = [self._map_to_response(item) for item in response.data]

        return SendListResponse(
            sends=sends,
            total=total,
            page=page,
            page_size=page_size,
            has_more=offset + page_size < total
        )

    async def get_send(self, send_id: str, user_id: str) -> Optional[NewsletterSendResponse]:
        """Get specific send"""
        response = self.db.table("newsletter_sends").select("*").eq(
            "id", send_id
        ).eq("user_id", user_id).execute()

        if response.data:
            return self._map_to_response(response.data[0])
        return None

    async def update_send(
        self,
        send_id: str,
        user_id: str,
        update: SendUpdate
    ) -> Optional[NewsletterSendResponse]:
        """Update send record (for tracking)"""
        existing = await self.get_send(send_id, user_id)
        if not existing:
            return None

        update_data = {"updated_at": datetime.utcnow().isoformat()}

        if update.status is not None:
            update_data["status"] = update.status.value

        if update.error_message is not None:
            update_data["error_message"] = update.error_message

        if update.delivered_at is not None:
            update_data["delivered_at"] = update.delivered_at.isoformat()

        if update.opened_at is not None:
            update_data["opened_at"] = update.opened_at.isoformat()

        if update.clicked_at is not None:
            update_data["clicked_at"] = update.clicked_at.isoformat()

        response = self.db.table("newsletter_sends").update(
            update_data
        ).eq("id", send_id).eq("user_id", user_id).execute()

        if response.data:
            return self._map_to_response(response.data[0])
        return None

    async def get_stats(self, user_id: str) -> SendStats:
        """Get newsletter send statistics"""
        # Get all sends
        response = self.db.table("newsletter_sends").select("*").eq("user_id", user_id).execute()

        if not response.data:
            return SendStats()

        sends = response.data

        # Calculate stats
        stats = SendStats(
            total_sends=len(sends),
            successful_sends=len([s for s in sends if s["status"] == SendStatus.SENT.value]),
            failed_sends=len([s for s in sends if s["status"] == SendStatus.FAILED.value]),
            test_sends=len([s for s in sends if s.get("is_test", False)]),
            delivered_count=len([s for s in sends if s.get("delivered_at")]),
            opened_count=len([s for s in sends if s.get("opened_at")]),
            clicked_count=len([s for s in sends if s.get("clicked_at")])
        )

        # Calculate rates
        if stats.delivered_count > 0:
            stats.open_rate = round((stats.opened_count / stats.delivered_count) * 100, 2)
        if stats.opened_count > 0:
            stats.click_rate = round((stats.clicked_count / stats.opened_count) * 100, 2)

        # Get last send date
        if sends:
            stats.last_send_date = datetime.fromisoformat(
                sends[0]["created_at"].replace("Z", "+00:00")
            )

        return stats

    async def _update_send_status(self, send_id: str, status: SendStatus):
        """Update send status"""
        update_data = {
            "status": status.value,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.db.table("newsletter_sends").update(update_data).eq("id", send_id).execute()

    def _map_to_response(self, data: dict) -> NewsletterSendResponse:
        """Map database record to response model"""
        return NewsletterSendResponse(
            id=data["id"],
            user_id=data["user_id"],
            draft_id=data["draft_id"],
            recipient_email=data["recipient_email"],
            status=SendStatus(data["status"]),
            is_test=data.get("is_test", False),
            message_id=data.get("message_id"),
            from_email=data.get("from_email"),
            from_name=data.get("from_name"),
            error_message=data.get("error_message"),
            sent_at=datetime.fromisoformat(data["sent_at"].replace("Z", "+00:00")) if data.get("sent_at") else None,
            delivered_at=datetime.fromisoformat(data["delivered_at"].replace("Z", "+00:00")) if data.get("delivered_at") else None,
            opened_at=datetime.fromisoformat(data["opened_at"].replace("Z", "+00:00")) if data.get("opened_at") else None,
            clicked_at=datetime.fromisoformat(data["clicked_at"].replace("Z", "+00:00")) if data.get("clicked_at") else None,
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        )
