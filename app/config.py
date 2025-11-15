# backend/app/config.py

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings"""

    # Application
    APP_NAME: str = "İş Fizibilitesi API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/fizibilite_db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]  # Change in production

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # Business Logic Defaults
    DEFAULT_WORKING_DAYS: int = 26
    MIN_GROSS_MARGIN: float = 30.0
    RECOMMENDED_EMERGENCY_MONTHS: int = 3

    # File Upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".png", ".jpg", ".jpeg"]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()