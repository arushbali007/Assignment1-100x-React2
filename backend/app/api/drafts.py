from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_user
from app.core.database import get_supabase as get_db
from app.models.user import UserInDB
from app.models.draft import (
    DraftCreate, DraftUpdate, DraftResponse,
    DraftListResponse, DraftStats, DraftStatus
)
from app.services.draft_service import DraftService

router = APIRouter(prefix="/api/drafts", tags=["drafts"])


@router.post("/generate", response_model=DraftResponse)
async def generate_draft(
    request: DraftCreate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Generate a new newsletter draft

    - Pulls top trends and recent content
    - Uses user's writing style profile
    - Generates AI-powered newsletter
    - Returns structured draft (HTML + plain text)
    """
    service = DraftService(db)

    try:
        draft = await service.generate_draft(
            user_id=str(current_user.id),  # Convert UUID to string
            request=request
        )
        return draft
    except Exception as e:
        import traceback
        print(f"Draft generation error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate draft: {str(e)}")


@router.get("/", response_model=DraftListResponse)
async def get_drafts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status: Optional[DraftStatus] = None,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Get paginated list of drafts

    - Filter by status (pending, reviewed, edited, sent, archived)
    - Paginated results
    - Ordered by creation date (newest first)
    """
    service = DraftService(db)
    return await service.get_drafts(
        user_id=str(current_user.id),  # Convert UUID to string
        page=page,
        page_size=page_size,
        status=status
    )


@router.get("/stats", response_model=DraftStats)
async def get_draft_stats(
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Get draft statistics

    - Total drafts
    - Count by status
    - Last draft date
    - Average generation time
    """
    service = DraftService(db)
    return await service.get_stats(user_id=str(current_user.id))  # Convert UUID to string


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get specific draft by ID"""
    service = DraftService(db)
    draft = await service.get_draft(
        draft_id=draft_id,
        user_id=str(current_user.id)  # Convert UUID to string
    )

    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    return draft


@router.patch("/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: str,
    update: DraftUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Update draft

    - Update status (reviewed, edited, sent, archived)
    - Edit subject line
    - Edit HTML/plain text content
    - Update structured content data
    - Add notes
    """
    service = DraftService(db)
    draft = await service.update_draft(
        draft_id=draft_id,
        user_id=str(current_user.id),  # Convert UUID to string
        update=update
    )

    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    return draft


@router.delete("/{draft_id}")
async def delete_draft(
    draft_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """Delete draft"""
    service = DraftService(db)
    success = await service.delete_draft(
        draft_id=draft_id,
        user_id=str(current_user.id)  # Convert UUID to string
    )

    if not success:
        raise HTTPException(status_code=404, detail="Draft not found")

    return {"message": "Draft deleted successfully"}
