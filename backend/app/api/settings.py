"""
User settings API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.api.dependencies import get_current_user
from app.core.database import get_supabase
from app.models.user import User

router = APIRouter(prefix="/api/settings", tags=["settings"])


class DeliverySettings(BaseModel):
    """Delivery preference settings"""
    delivery_enabled: bool
    delivery_time: str = "08:00:00"  # HH:MM:SS format
    delivery_days: str = "weekdays"  # weekdays, daily, weekends, or custom (Mon,Wed,Fri)


class DeliverySettingsResponse(BaseModel):
    """Delivery settings response"""
    delivery_enabled: bool
    delivery_time: str
    delivery_days: str
    timezone: str


@router.get("/delivery", response_model=DeliverySettingsResponse)
async def get_delivery_settings(current_user: User = Depends(get_current_user)):
    """Get user's delivery preferences"""
    db = get_supabase()

    response = db.table("users").select("*").eq("id", current_user.id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")

    user = response.data[0]

    return DeliverySettingsResponse(
        delivery_enabled=user.get("delivery_enabled", True),
        delivery_time=user.get("delivery_time", "08:00:00"),
        delivery_days=user.get("delivery_days", "weekdays"),
        timezone=user.get("timezone", "UTC")
    )


@router.patch("/delivery")
async def update_delivery_settings(
    settings: DeliverySettings,
    current_user: User = Depends(get_current_user)
):
    """Update user's delivery preferences"""
    db = get_supabase()

    # Validate delivery_time format
    try:
        parts = settings.delivery_time.split(":")
        hour, minute = int(parts[0]), int(parts[1])
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError()
    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid delivery_time format. Use HH:MM:SS (e.g., 08:00:00)"
        )

    # Validate delivery_days
    valid_days = ["weekdays", "daily", "weekends"]
    if settings.delivery_days not in valid_days and "," not in settings.delivery_days:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid delivery_days. Use: {', '.join(valid_days)} or custom (e.g., Mon,Wed,Fri)"
        )

    # Update database
    update_data = {
        "delivery_enabled": settings.delivery_enabled,
        "delivery_time": settings.delivery_time,
        "delivery_days": settings.delivery_days
    }

    response = db.table("users").update(update_data).eq("id", current_user.id).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to update settings")

    return {
        "message": "Delivery settings updated successfully",
        "settings": settings
    }
