from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import structlog

from app.core.database import get_db
from app.core.config import settings
from app.core.auth import AuthService, get_current_user
from app.schemas.auth import UserLogin, UserRegister, TokenResponse, UserResponse
from app.models.user import User

router = APIRouter()
logger = structlog.get_logger()
security = HTTPBearer()

@router.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access token"""
    try:
        auth_service = AuthService()
        user = await auth_service.authenticate_user(
            db, user_credentials.username, user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Update last login
        user.last_login = auth_service.get_current_time()
        await db.commit()
        
        logger.info("User logged in successfully", username=user.username)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        logger.error("Login failed", error=str(e), username=user_credentials.username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    try:
        auth_service = AuthService()
        
        # Check if user already exists
        existing_user = await auth_service.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        existing_email = await auth_service.get_user_by_email(db, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = await auth_service.create_user(db, user_data)
        
        logger.info("User registered successfully", username=user.username)
        
        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            department=user.department,
            is_active=user.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e), username=user_data.username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        department=current_user.department,
        is_active=current_user.is_active
    )

@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    try:
        auth_service = AuthService()
        username = auth_service.verify_token(credentials.credentials)
        user = await auth_service.get_user_by_username(db, username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user (client should discard token)"""
    logger.info("User logged out", username=current_user.username)
    return {"message": "Successfully logged out"}
