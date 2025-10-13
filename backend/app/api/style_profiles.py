"""Style Profile API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.style_profile import (
    StyleProfileCreate,
    StyleProfileResponse,
    StyleProfileList,
    StyleSummary
)
from app.services.style_profile_service import StyleProfileService
from app.api.dependencies import get_current_user
from app.models.user import UserInDB

router = APIRouter(prefix="/api/style-profiles", tags=["Style Profiles"])
style_service = StyleProfileService()


@router.post("/", response_model=StyleProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_style_profile(
    profile_data: StyleProfileCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload and analyze a past newsletter to create a style profile

    - **newsletter_text**: Full text content of the newsletter
    - **newsletter_title**: Optional title of the newsletter
    """
    try:
        profile = await style_service.create_and_analyze_profile(
            user_id=str(current_user.id),  # Convert UUID to string
            profile_data=profile_data
        )
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create style profile: {str(e)}"
        )


@router.get("/", response_model=StyleProfileList)
async def get_style_profiles(
    page: int = 1,
    page_size: int = 10,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all style profiles for the current user with pagination

    - **page**: Page number (default: 1)
    - **page_size**: Number of profiles per page (default: 10)
    """
    result = await style_service.get_user_profiles(
        user_id=str(current_user.id),  # Convert UUID to string
        page=page,
        page_size=page_size
    )
    return StyleProfileList(**result)


@router.get("/primary", response_model=StyleProfileResponse)
async def get_primary_profile(
    current_user: UserInDB = Depends(get_current_user)
):
    """Get the user's primary style profile"""
    profile = await style_service.get_primary_profile(str(current_user.id))  # Convert UUID to string
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No primary style profile found. Please upload a newsletter first."
        )
    return profile


@router.get("/aggregated", response_model=dict)
async def get_aggregated_style(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get an aggregated style summary from all uploaded newsletters

    This combines characteristics from all style profiles to create
    a comprehensive understanding of the user's writing style.
    """
    aggregated = await style_service.get_aggregated_style(str(current_user.id))  # Convert UUID to string
    if not aggregated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No style profiles found. Please upload newsletters first."
        )
    return aggregated


@router.get("/stats")
async def get_style_stats(
    current_user: UserInDB = Depends(get_current_user)
):
    """Get statistics about style profiles"""
    return await style_service.get_stats(str(current_user.id))  # Convert UUID to string


@router.get("/{profile_id}", response_model=StyleProfileResponse)
async def get_style_profile(
    profile_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific style profile by ID"""
    profile = await style_service.get_profile(profile_id, str(current_user.id))  # Convert UUID to string
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style profile not found"
        )
    return profile


@router.patch("/{profile_id}/primary", response_model=StyleProfileResponse)
async def set_as_primary(
    profile_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Set a style profile as the primary one"""
    try:
        profile = await style_service.set_primary_profile(profile_id, str(current_user.id))  # Convert UUID to string
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set primary profile: {str(e)}"
        )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_style_profile(
    profile_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete a style profile"""
    success = await style_service.delete_profile(profile_id, str(current_user.id))  # Convert UUID to string
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style profile not found"
        )
    return None
