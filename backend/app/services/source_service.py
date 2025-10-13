"""
Source service for managing content sources
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..core.database import supabase, supabase_admin
from ..models.source import SourceCreate, SourceUpdate, SourceInDB


class SourceService:
    """Service for source CRUD operations"""

    @staticmethod
    async def create_source(user_id: UUID, source_data: SourceCreate) -> SourceInDB:
        """Create a new source for a user"""
        data = {
            "user_id": str(user_id),
            "source_type": source_data.source_type,
            "source_url": source_data.source_url,
            "source_identifier": source_data.source_identifier,
            "name": source_data.name,
            "is_active": source_data.is_active,
            "metadata": source_data.metadata,
        }

        # Use admin client to bypass RLS
        result = supabase_admin.table("sources").insert(data).execute()

        if not result.data:
            raise Exception("Failed to create source")

        return SourceInDB(**result.data[0])

    @staticmethod
    async def get_source(source_id: UUID, user_id: UUID) -> Optional[SourceInDB]:
        """Get a source by ID"""
        # Use admin client to bypass RLS
        result = (
            supabase_admin.table("sources")
            .select("*")
            .eq("id", str(source_id))
            .eq("user_id", str(user_id))
            .execute()
        )

        if not result.data:
            return None

        return SourceInDB(**result.data[0])

    @staticmethod
    async def get_sources(
        user_id: UUID,
        source_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[SourceInDB], int]:
        """Get all sources for a user with optional filters"""
        # Start building the query - use admin client to bypass RLS
        query = supabase_admin.table("sources").select("*", count="exact").eq("user_id", str(user_id))

        # Apply filters
        if source_type:
            query = query.eq("source_type", source_type)

        if is_active is not None:
            query = query.eq("is_active", is_active)

        # Apply pagination and ordering
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

        result = query.execute()

        sources = [SourceInDB(**source) for source in result.data] if result.data else []
        total = result.count if result.count else 0

        return sources, total

    @staticmethod
    async def update_source(
        source_id: UUID, user_id: UUID, source_data: SourceUpdate
    ) -> Optional[SourceInDB]:
        """Update a source"""
        # Build update data (only include fields that are not None)
        update_data = {}

        if source_data.source_url is not None:
            update_data["source_url"] = source_data.source_url

        if source_data.source_identifier is not None:
            update_data["source_identifier"] = source_data.source_identifier

        if source_data.name is not None:
            update_data["name"] = source_data.name

        if source_data.is_active is not None:
            update_data["is_active"] = source_data.is_active

        if source_data.metadata is not None:
            update_data["metadata"] = source_data.metadata

        if not update_data:
            # Nothing to update, just return the existing source
            return await SourceService.get_source(source_id, user_id)

        # Use admin client to bypass RLS
        result = (
            supabase_admin.table("sources")
            .update(update_data)
            .eq("id", str(source_id))
            .eq("user_id", str(user_id))
            .execute()
        )

        if not result.data:
            return None

        return SourceInDB(**result.data[0])

    @staticmethod
    async def delete_source(source_id: UUID, user_id: UUID) -> bool:
        """Delete a source"""
        # Use admin client to bypass RLS
        result = (
            supabase_admin.table("sources")
            .delete()
            .eq("id", str(source_id))
            .eq("user_id", str(user_id))
            .execute()
        )

        return bool(result.data)

    @staticmethod
    async def get_sources_by_type(
        user_id: UUID, source_type: str
    ) -> List[SourceInDB]:
        """Get all active sources of a specific type for a user"""
        # Use admin client to bypass RLS
        result = (
            supabase_admin.table("sources")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("source_type", source_type)
            .eq("is_active", True)
            .order("created_at", desc=True)
            .execute()
        )

        if not result.data:
            return []

        return [SourceInDB(**source) for source in result.data]

    @staticmethod
    async def count_sources(user_id: UUID) -> dict:
        """Get count of sources by type for a user"""
        # Use admin client to bypass RLS
        result = (
            supabase_admin.table("sources")
            .select("source_type", count="exact")
            .eq("user_id", str(user_id))
            .execute()
        )

        # Count by type
        counts = {"twitter": 0, "youtube": 0, "rss": 0, "newsletter": 0, "total": 0}

        if result.data:
            for source in result.data:
                source_type = source.get("source_type")
                if source_type in counts:
                    counts[source_type] += 1
                counts["total"] += 1

        return counts
