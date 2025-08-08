from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WaferMaps"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://wafermaps_user:wafermaps_password@localhost:5433/wafermaps_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6380"
    
    # MinIO/S3
    MINIO_URL: str = "http://localhost:9002"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "wafermaps"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/tiff", "application/pdf"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Analytics
    CACHE_TTL: int = 3600  # 1 hour
    TREND_WINDOW_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Override settings based on environment
if settings.ENVIRONMENT == "production":
    settings.DEBUG = False
    settings.LOG_LEVEL = "WARNING"
    settings.ALLOWED_HOSTS = ["your-domain.com", "www.your-domain.com"]
