from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserCreate, UserLogin, Token, UserResponse
from app.services.auth_service import AuthService
from app.api.dependencies import get_auth_service, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user

    - **email**: Valid email address
    - **password**: Minimum 6 characters
    - **full_name**: Optional full name
    - **timezone**: User timezone (default: UTC)
    """
    result = await auth_service.signup(user_data)
    return {
        "message": "User created successfully",
        "user": {
            "id": result["user"]["id"],
            "email": result["user"]["email"],
            "full_name": result["user"]["full_name"],
            "timezone": result["user"]["timezone"],
        },
        "access_token": result["access_token"],
        "token_type": result["token_type"]
    }


@router.post("/login", response_model=dict)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and get access token

    - **email**: User email
    - **password**: User password
    """
    result = await auth_service.login(login_data)
    return {
        "message": "Login successful",
        "user": {
            "id": result["user"]["id"],
            "email": result["user"]["email"],
            "full_name": result["user"]["full_name"],
            "timezone": result["user"]["timezone"],
        },
        "access_token": result["access_token"],
        "token_type": result["token_type"]
    }


@router.get("/me", response_model=dict)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile (requires authentication)
    """
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "timezone": current_user["timezone"],
        "preferences": current_user.get("preferences", {}),
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"]
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user (client should delete token)
    """
    return {
        "message": "Logout successful. Please delete the token on client side."
    }
