from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import get_supabase
from app.services.auth_service import AuthService
from app.models.user import UserInDB
from supabase import Client

security = HTTPBearer()


async def get_auth_service(supabase: Client = Depends(get_supabase)) -> AuthService:
    """Get auth service instance"""
    return AuthService(supabase)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserInDB:
    """Get current authenticated user"""
    token = credentials.credentials

    user_dict = await auth_service.get_current_user(token)

    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert dict to UserInDB model
    return UserInDB(**user_dict)
