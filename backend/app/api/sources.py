"""
Source management API endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query

from ..models.user import UserInDB
from ..models.source import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceListResponse,
)
from ..services.source_service import SourceService
from ..api.dependencies import get_current_user

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.post("/", response_model=SourceResponse, status_code=201)
async def create_source(
    source_data: SourceCreate,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Create a new content source

    Supported source types:
    - twitter: Twitter/X profiles
    - youtube: YouTube channels
    - rss: RSS feeds
    - newsletter: Newsletter archives
    """
    try:
        source = await SourceService.create_source(current_user.id, source_data)
        return SourceResponse(**source.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=SourceListResponse)
async def get_sources(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Get all sources for the current user

    Supports filtering by:
    - source_type: twitter, youtube, rss, newsletter
    - is_active: true/false

    Supports pagination with page and page_size parameters
    """
    offset = (page - 1) * page_size
    sources, total = await SourceService.get_sources(
        user_id=current_user.id,
        source_type=source_type,
        is_active=is_active,
        limit=page_size,
        offset=offset,
    )

    return SourceListResponse(
        sources=[SourceResponse(**source.model_dump()) for source in sources],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats")
async def get_source_stats(
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Get statistics about user's sources

    Returns count by source type and total count
    """
    stats = await SourceService.count_sources(current_user.id)
    return stats


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: UUID,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Get a specific source by ID
    """
    source = await SourceService.get_source(source_id, current_user.id)

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    return SourceResponse(**source.model_dump())


@router.patch("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: UUID,
    source_data: SourceUpdate,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Update a source

    You can update any of the following fields:
    - source_url
    - source_identifier
    - name
    - is_active
    - metadata
    """
    source = await SourceService.update_source(source_id, current_user.id, source_data)

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    return SourceResponse(**source.model_dump())


@router.delete("/{source_id}", status_code=204)
async def delete_source(
    source_id: UUID,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Delete a source

    This will also delete all content associated with this source
    """
    deleted = await SourceService.delete_source(source_id, current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")

    return None
