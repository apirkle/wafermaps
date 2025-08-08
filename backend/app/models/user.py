from sqlalchemy import Column, String, Boolean, DateTime, UUID
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")  # admin, engineer, operator, viewer
    department = Column(String(50))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
    
    @property
    def is_engineer(self) -> bool:
        return self.role in ["admin", "engineer"]
    
    @property
    def is_operator(self) -> bool:
        return self.role in ["admin", "engineer", "operator"]
