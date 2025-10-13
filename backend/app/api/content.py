"""Content API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import Optional

from app.models.user import UserInDB
from app.models.content import ContentResponse, ContentList
from app.api.dependencies import get_current_user
from app.services.content_service import content_service

router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("/fetch")
async def fetch_content(current_user: UserInDB = Depends(get_current_user)):
    """
    Fetch content from all active sources
    """
    try:
        results = await content_service.fetch_all_content(current_user.id)
        return {
            "message": f"Fetched {results['total_new_items']} new items",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=ContentList)
async def get_content(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    source_id: Optional[UUID] = Query(None, description="Filter by source ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get paginated list of content
    """
    try:
        offset = (page - 1) * page_size
        content_list, total = await content_service.get_content_list(
            user_id=current_user.id,
            content_type=content_type,
            source_id=source_id,
            limit=page_size,
            offset=offset
        )

        pages = (total + page_size - 1) // page_size

        return ContentList(
            items=content_list,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_content_stats(current_user: UserInDB = Depends(get_current_user)):
    """
    Get content statistics
    """
    try:
        stats = await content_service.get_content_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content_by_id(
    content_id: UUID,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get specific content by ID
    """
    try:
        content = await content_service.get_content_by_id(current_user.id, content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        return content
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{content_id}")
async def delete_content(
    content_id: UUID,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete content
    """
    try:
        deleted = await content_service.delete_content(current_user.id, content_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Content not found")
        return {"message": "Content deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
