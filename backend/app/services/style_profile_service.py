"""Style Profile Service for managing user writing styles"""
from datetime import datetime
from typing import Optional
from app.core.database import supabase_admin
from app.models.style_profile import StyleProfileCreate, StyleProfileUpdate, StyleProfileResponse, StyleAnalysis
from app.services.style_analysis_service import StyleAnalysisService


class StyleProfileService:
    """Service for managing style profiles"""

    def __init__(self):
        self.supabase = supabase_admin
        self.style_analyzer = StyleAnalysisService()

    async def create_and_analyze_profile(
        self,
        user_id: str,
        profile_data: StyleProfileCreate
    ) -> StyleProfileResponse:
        """
        Create a new style profile and analyze it

        Args:
            user_id: User ID
            profile_data: Profile creation data

        Returns:
            Created and analyzed style profile
        """
        # Analyze the writing style
        style_analysis: StyleAnalysis = await self.style_analyzer.analyze_writing_style(
            profile_data.newsletter_text
        )

        # Convert to dict for storage
        style_data = style_analysis.model_dump()

        # Check if this is the user's first profile
        existing = self.supabase.table("style_profiles")\
            .select("id")\
            .eq("user_id", user_id)\
            .execute()

        is_primary = len(existing.data) == 0  # First profile is primary

        # Insert into database
        result = self.supabase.table("style_profiles").insert({
            "user_id": user_id,
            "newsletter_text": profile_data.newsletter_text,
            "newsletter_title": profile_data.newsletter_title,
            "style_data": style_data,
            "is_primary": is_primary,
            "analyzed_at": datetime.utcnow().isoformat()
        }).execute()

        if not result.data:
            raise Exception("Failed to create style profile")

        return StyleProfileResponse(**result.data[0])

    async def get_profile(self, profile_id: str, user_id: str) -> Optional[StyleProfileResponse]:
        """Get a specific style profile"""
        result = self.supabase.table("style_profiles")\
            .select("*")\
            .eq("id", profile_id)\
            .eq("user_id", user_id)\
            .execute()

        if result.data:
            return StyleProfileResponse(**result.data[0])
        return None

    async def get_user_profiles(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """Get all style profiles for a user with pagination"""
        offset = (page - 1) * page_size

        # Get total count
        count_result = self.supabase.table("style_profiles")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()

        total = count_result.count or 0

        # Get paginated results
        result = self.supabase.table("style_profiles")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .range(offset, offset + page_size - 1)\
            .execute()

        profiles = [StyleProfileResponse(**p) for p in result.data]

        return {
            "profiles": profiles,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_primary_profile(self, user_id: str) -> Optional[StyleProfileResponse]:
        """Get the user's primary style profile"""
        result = self.supabase.table("style_profiles")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("is_primary", True)\
            .execute()

        if result.data:
            return StyleProfileResponse(**result.data[0])
        return None

    async def set_primary_profile(self, profile_id: str, user_id: str) -> StyleProfileResponse:
        """Set a profile as the primary one"""
        # Unset all primary flags for this user
        self.supabase.table("style_profiles")\
            .update({"is_primary": False})\
            .eq("user_id", user_id)\
            .execute()

        # Set this profile as primary
        result = self.supabase.table("style_profiles")\
            .update({"is_primary": True})\
            .eq("id", profile_id)\
            .eq("user_id", user_id)\
            .execute()

        if not result.data:
            raise Exception("Failed to set primary profile")

        return StyleProfileResponse(**result.data[0])

    async def delete_profile(self, profile_id: str, user_id: str) -> bool:
        """Delete a style profile"""
        # Check if it's primary
        profile = await self.get_profile(profile_id, user_id)
        if not profile:
            return False

        # Delete the profile
        result = self.supabase.table("style_profiles")\
            .delete()\
            .eq("id", profile_id)\
            .eq("user_id", user_id)\
            .execute()

        # If this was primary, set another one as primary
        if profile.is_primary:
            remaining = self.supabase.table("style_profiles")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()

            if remaining.data:
                await self.set_primary_profile(remaining.data[0]["id"], user_id)

        return len(result.data) > 0

    async def get_aggregated_style(self, user_id: str) -> dict:
        """Get an aggregated style profile from all user's profiles"""
        result = self.supabase.table("style_profiles")\
            .select("style_data")\
            .eq("user_id", user_id)\
            .execute()

        if not result.data:
            return {}

        style_profiles = [p["style_data"] for p in result.data if p.get("style_data")]

        return await self.style_analyzer.aggregate_style_profiles(style_profiles)

    async def get_stats(self, user_id: str) -> dict:
        """Get statistics about user's style profiles"""
        result = self.supabase.table("style_profiles")\
            .select("id, is_primary, analyzed_at")\
            .eq("user_id", user_id)\
            .execute()

        total_profiles = len(result.data)
        analyzed_count = len([p for p in result.data if p.get("analyzed_at")])

        return {
            "total_profiles": total_profiles,
            "analyzed_profiles": analyzed_count,
            "has_primary": any(p.get("is_primary") for p in result.data)
        }
