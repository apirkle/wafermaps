from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "viewer"
    department: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    user_id: UUID
    username: str
    email: str
    role: str
    department: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
