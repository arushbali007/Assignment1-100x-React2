from typing import Optional
from datetime import timedelta
from supabase import Client
from app.models.user import UserCreate, UserLogin, Token, UserResponse
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from fastapi import HTTPException, status


class AuthService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def signup(self, user_data: UserCreate) -> dict:
        """Register a new user"""
        try:
            # Import admin client to bypass RLS for user creation
            from app.core.database import supabase_admin

            # Check if user already exists
            existing_user = supabase_admin.table("users").select("*").eq("email", user_data.email).execute()

            if existing_user.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Hash password
            password_hash = get_password_hash(user_data.password)

            # Create user in database using admin client to bypass RLS
            user_dict = {
                "email": user_data.email,
                "password_hash": password_hash,
                "full_name": user_data.full_name,
                "timezone": user_data.timezone,
                "preferences": user_data.preferences,
                "is_active": True
            }

            result = supabase_admin.table("users").insert(user_dict).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )

            user = result.data[0]

            # Create access token
            access_token = create_access_token(
                data={"sub": str(user["id"]), "email": user["email"]},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )

            return {
                "user": user,
                "access_token": access_token,
                "token_type": "bearer"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Signup error: {str(e)}"
            )

    async def login(self, login_data: UserLogin) -> dict:
        """Authenticate user and return token"""
        try:
            # Import admin client to bypass RLS for user lookup
            from app.core.database import supabase_admin

            # Get user by email
            result = supabase_admin.table("users").select("*").eq("email", login_data.email).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            user = result.data[0]

            # Verify password
            if not verify_password(login_data.password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            # Check if user is active
            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive"
                )

            # Create access token
            access_token = create_access_token(
                data={"sub": str(user["id"]), "email": user["email"]},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )

            return {
                "user": user,
                "access_token": access_token,
                "token_type": "bearer"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login error: {str(e)}"
            )

    async def get_current_user(self, token: str) -> Optional[dict]:
        """Get current user from token"""
        try:
            from app.utils.security import decode_access_token
            from app.core.database import supabase_admin

            payload = decode_access_token(token)
            if not payload:
                return None

            user_id: str = payload.get("sub")
            if not user_id:
                return None

            # Get user from database using admin client
            result = supabase_admin.table("users").select("*").eq("id", user_id).execute()

            if not result.data:
                return None

            return result.data[0]

        except Exception:
            return None
