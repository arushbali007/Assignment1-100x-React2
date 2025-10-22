from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from supabase import Client

from app.models.draft import (
    DraftResponse, DraftCreate, DraftUpdate, DraftListResponse,
    DraftStats, DraftStatus, DraftContent, DraftMetadata
)
from app.services.newsletter_generation_service import NewsletterGenerationService
from app.services.trend_service import TrendService
from app.services.content_service import ContentService
from app.services.style_profile_service import StyleProfileService


class DraftService:
    """Manage newsletter drafts"""

    def __init__(self, db: Client):
        self.db = db
        self.generator = NewsletterGenerationService()
        self.trend_service = TrendService()  # Fixed: no db parameter
        self.content_service = ContentService()  # Fixed: no db parameter
        self.style_service = StyleProfileService()  # Fixed: no db parameter

    async def generate_draft(
        self,
        user_id: str,
        request: DraftCreate
    ) -> DraftResponse:
        """
        Generate a new newsletter draft

        Args:
            user_id: User ID
            request: Draft generation request

        Returns:
            Generated draft
        """
        # Check if today's draft already exists
        if not request.force_regenerate:
            existing = await self._get_today_draft(user_id)
            if existing:
                return existing

        # Get top trends
        trends_response = await self.trend_service.get_top_trends(
            user_id=UUID(user_id),
            limit=request.max_trends
        )
        trends = trends_response if trends_response else []

        # Get recent content (last 7 days)
        content_list, total = await self.content_service.get_content_list(
            user_id=UUID(user_id),
            limit=20,
            offset=0
        )
        recent_content = content_list if content_list else []

        # Get user's aggregated style
        style_summary = await self.style_service.get_aggregated_style(user_id)

        # Get user info
        user_response = self.db.table("users").select("*").eq("id", user_id).execute()
        user_name = None
        if user_response.data:
            user_name = user_response.data[0].get("email", "Creator").split("@")[0]

        # Generate newsletter
        draft_content, metadata = await self.generator.generate_newsletter(
            trends=trends,
            recent_content=recent_content,
            style_summary=style_summary,
            user_name=user_name,
            include_trends_section=request.include_trends,
            max_trends=request.max_trends
        )

        # Get primary style profile ID
        primary_profile = await self.style_service.get_primary_profile(user_id)
        if primary_profile:
            metadata.style_profile_id = primary_profile.id

        # Convert to HTML and plain text
        html_content = self.generator.convert_to_html(draft_content)
        plain_content = self.generator.convert_to_plain_text(draft_content)

        # Save to database
        draft_data = {
            "user_id": user_id,
            "subject": draft_content.subject,
            "html_content": html_content,
            "plain_content": plain_content,
            "content_data": draft_content.model_dump(),
            "status": DraftStatus.PENDING.value,
            "metadata": metadata.model_dump(),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        response = self.db.table("drafts").insert(draft_data).execute()

        if not response.data:
            raise Exception("Failed to create draft")

        return self._map_to_response(response.data[0])

    async def _get_today_draft(self, user_id: str) -> Optional[DraftResponse]:
        """Get draft created today"""
        today = date.today().isoformat()

        response = self.db.table("drafts").select("*").eq(
            "user_id", user_id
        ).gte(
            "created_at", today
        ).order(
            "created_at", desc=True
        ).limit(1).execute()

        if response.data:
            return self._map_to_response(response.data[0])
        return None

    async def get_drafts(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
        status: Optional[DraftStatus] = None
    ) -> DraftListResponse:
        """Get user's drafts with pagination"""
        offset = (page - 1) * page_size

        # Build query
        query = self.db.table("drafts").select("*", count="exact").eq("user_id", user_id)

        if status:
            query = query.eq("status", status.value)

        # Get total count
        count_response = query.execute()
        total = count_response.count if count_response.count else 0

        # Get paginated data
        response = query.order(
            "created_at", desc=True
        ).range(offset, offset + page_size - 1).execute()

        drafts = [self._map_to_response(item) for item in response.data]

        return DraftListResponse(
            drafts=drafts,
            total=total,
            page=page,
            page_size=page_size,
            has_more=offset + page_size < total
        )

    async def get_draft(self, draft_id: str, user_id: str) -> Optional[DraftResponse]:
        """Get specific draft"""
        response = self.db.table("drafts").select("*").eq(
            "id", draft_id
        ).eq("user_id", user_id).execute()

        if response.data:
            return self._map_to_response(response.data[0])
        return None

    async def update_draft(
        self,
        draft_id: str,
        user_id: str,
        update: DraftUpdate
    ) -> Optional[DraftResponse]:
        """Update draft"""
        # Get existing draft
        existing = await self.get_draft(draft_id, user_id)
        if not existing:
            return None

        # Build update data
        update_data = {"updated_at": datetime.utcnow().isoformat()}

        if update.status is not None:
            update_data["status"] = update.status.value

            # Update timestamps based on status
            if update.status == DraftStatus.REVIEWED and not existing.reviewed_at:
                update_data["reviewed_at"] = datetime.utcnow().isoformat()
            elif update.status == DraftStatus.SENT:
                if not existing.sent_at:
                    update_data["sent_at"] = datetime.utcnow().isoformat()
                if not existing.approved_at:
                    update_data["approved_at"] = datetime.utcnow().isoformat()
                # Auto-set outcome to accepted when sent
                if not existing.outcome:
                    update_data["outcome"] = "accepted"

        # Handle explicit outcome updates
        if update.outcome is not None:
            update_data["outcome"] = update.outcome

        if update.rejection_reason is not None:
            update_data["rejection_reason"] = update.rejection_reason

        if update.subject is not None:
            update_data["subject"] = update.subject

        if update.html_content is not None:
            update_data["html_content"] = update.html_content

        if update.plain_content is not None:
            update_data["plain_content"] = update.plain_content

        if update.content_data is not None:
            update_data["content_data"] = update.content_data.model_dump()

            # Regenerate HTML and plain text if content_data changes
            update_data["html_content"] = self.generator.convert_to_html(update.content_data)
            update_data["plain_content"] = self.generator.convert_to_plain_text(update.content_data)
            update_data["subject"] = update.content_data.subject

        if update.notes is not None:
            update_data["notes"] = update.notes

        # Update in database
        response = self.db.table("drafts").update(
            update_data
        ).eq("id", draft_id).eq("user_id", user_id).execute()

        if response.data:
            return self._map_to_response(response.data[0])
        return None

    async def delete_draft(self, draft_id: str, user_id: str) -> bool:
        """Delete draft"""
        response = self.db.table("drafts").delete().eq(
            "id", draft_id
        ).eq("user_id", user_id).execute()

        return len(response.data) > 0

    async def get_stats(self, user_id: str) -> DraftStats:
        """Get draft statistics"""
        try:
            # Get all drafts
            response = self.db.table("drafts").select("*").eq("user_id", user_id).execute()

            if not response.data:
                return DraftStats()

            drafts = response.data

            # Calculate stats
            accepted_count = len([d for d in drafts if d.get("outcome") == "accepted"])
            rejected_count = len([d for d in drafts if d.get("outcome") == "rejected"])

            # Calculate acceptance rate
            total_outcomes = accepted_count + rejected_count
            acceptance_rate = (accepted_count / total_outcomes * 100) if total_outcomes > 0 else 0.0

            stats = DraftStats(
                total_drafts=len(drafts),
                pending_drafts=len([d for d in drafts if d.get("status") == DraftStatus.PENDING.value]),
                reviewed_drafts=len([d for d in drafts if d.get("status") == DraftStatus.REVIEWED.value]),
                sent_drafts=len([d for d in drafts if d.get("status") == DraftStatus.SENT.value]),
                archived_drafts=len([d for d in drafts if d.get("status") == DraftStatus.ARCHIVED.value]),
                accepted_drafts=accepted_count,
                rejected_drafts=rejected_count,
                acceptance_rate=round(acceptance_rate, 1)
            )

            # Get last draft date
            if drafts:
                stats.last_draft_date = datetime.fromisoformat(
                    drafts[0]["created_at"].replace("Z", "+00:00")
                )

            # Calculate avg generation time
            generation_times = []
            for draft in drafts:
                metadata = draft.get("metadata", {})
                if isinstance(metadata, dict):
                    gen_time = metadata.get("generation_time_seconds")
                    if gen_time:
                        generation_times.append(gen_time)

            if generation_times:
                stats.avg_generation_time = round(sum(generation_times) / len(generation_times), 2)

            # Calculate avg review time (approved_at - created_at in minutes)
            review_times = []
            for draft in drafts:
                if draft.get("approved_at") and draft.get("created_at"):
                    try:
                        created = datetime.fromisoformat(draft["created_at"].replace("Z", "+00:00"))
                        approved = datetime.fromisoformat(draft["approved_at"].replace("Z", "+00:00"))
                        review_time_minutes = (approved - created).total_seconds() / 60
                        review_times.append(review_time_minutes)
                    except (ValueError, TypeError) as e:
                        print(f"Error parsing review time for draft: {e}")
                        continue

            if review_times:
                stats.avg_review_time_minutes = round(sum(review_times) / len(review_times), 2)

            return stats

        except Exception as e:
            import traceback
            print(f"Error calculating draft stats: {e}")
            print(traceback.format_exc())
            # Return empty stats on error
            return DraftStats()

    def _map_to_response(self, data: dict) -> DraftResponse:
        """Map database record to response model"""
        return DraftResponse(
            id=data["id"],
            user_id=data["user_id"],
            subject=data["subject"],
            html_content=data["html_content"],
            plain_content=data["plain_content"],
            content_data=DraftContent(**data["content_data"]),
            status=DraftStatus(data["status"]),
            metadata=DraftMetadata(**data["metadata"]) if data.get("metadata") else DraftMetadata(),
            notes=data.get("notes"),
            outcome=data.get("outcome"),
            rejection_reason=data.get("rejection_reason"),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
            reviewed_at=datetime.fromisoformat(data["reviewed_at"].replace("Z", "+00:00")) if data.get("reviewed_at") else None,
            approved_at=datetime.fromisoformat(data["approved_at"].replace("Z", "+00:00")) if data.get("approved_at") else None,
            sent_at=datetime.fromisoformat(data["sent_at"].replace("Z", "+00:00")) if data.get("sent_at") else None
        )
