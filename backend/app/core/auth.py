from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import structlog

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

logger = structlog.get_logger()

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> str:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return username
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def authenticate_user(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        user = await self.get_user_by_username(db, username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
    
    async def get_user_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create_user(self, db: AsyncSession, user_data: UserRegister) -> User:
        """Create a new user"""
        hashed_password = self.get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role or "viewer",
            department=user_data.department
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    def get_current_time(self) -> datetime:
        """Get current UTC time"""
        return datetime.utcnow()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    auth_service = AuthService()
    username = auth_service.verify_token(credentials.credentials)
    user = await auth_service.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def require_role(required_role: str):
    """Decorator to require specific user role"""
    def decorator(func):
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role != required_role and current_user.role != 'admin':
                raise HTTPException(
                    status_code=403,
                    detail=f"Role '{required_role}' required"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
