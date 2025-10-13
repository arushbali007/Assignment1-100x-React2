"""Trend API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import Optional

from app.models.user import UserInDB
from app.models.trend import TrendResponse, TrendList, TrendStats
from app.api.dependencies import get_current_user
from app.services.trend_service import trend_service

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.post("/detect")
async def detect_trends(current_user: UserInDB = Depends(get_current_user)):
    """
    Detect trending topics from user's content and save them
    """
    try:
        results = await trend_service.detect_and_save_trends(current_user.id)
        return {
            "message": f"Detected {results['detected']} trends, saved {results['saved']}",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top")
async def get_top_trends(
    limit: int = Query(3, ge=1, le=10, description="Number of top trends to return"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get top N trending topics for the user
    """
    try:
        trends = await trend_service.get_top_trends(current_user.id, limit=limit)
        return {
            "trends": trends,
            "count": len(trends)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_trend_stats(current_user: UserInDB = Depends(get_current_user)):
    """
    Get trend statistics for the user
    """
    try:
        stats = await trend_service.get_trend_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=TrendList)
async def get_trends(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get paginated list of all trends for the user
    """
    try:
        from app.core.database import get_supabase
        from datetime import datetime, timedelta

        supabase = get_supabase()

        # Get trends from last 30 days
        cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()

        offset = (page - 1) * page_size

        # Get paginated trends
        response = supabase.table('trends').select('*', count='exact').eq('user_id', str(current_user.id)).gte('detected_at', cutoff_date).order('score', desc=True).range(offset, offset + page_size - 1).execute()

        trends = [TrendResponse(**item) for item in response.data]
        total = response.count if response.count else 0
        pages = (total + page_size - 1) // page_size

        return TrendList(
            items=trends,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trend_id}", response_model=TrendResponse)
async def get_trend_by_id(
    trend_id: UUID,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get specific trend by ID
    """
    try:
        from app.core.database import get_supabase

        supabase = get_supabase()

        response = supabase.table('trends').select('*').eq('user_id', str(current_user.id)).eq('id', str(trend_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Trend not found")

        return TrendResponse(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{trend_id}")
async def delete_trend(
    trend_id: UUID,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a trend
    """
    try:
        from app.core.database import get_supabase

        supabase = get_supabase()

        response = supabase.table('trends').delete().eq('user_id', str(current_user.id)).eq('id', str(trend_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Trend not found")

        return {"message": "Trend deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
