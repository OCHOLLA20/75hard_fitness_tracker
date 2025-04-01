from pydantic_settings import BaseSettings
from typing import List
import os
import json

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # API configuration
    PROJECT_NAME: str = "75 Hard Fitness Tracker API"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True  # Set to False in production
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]  # Default value

    # Logging settings
    LOGGING_LEVEL: str = "INFO"
    
    # Cache settings
    CACHE_TYPE: str = "simple"
    
    # Session settings
    SESSION_COOKIE_SECURE: bool = False

    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./75hard.db"  # Default SQLite database - DEVELOPMENT ONLY
    )
    DB_ECHO_LOG: bool = False
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGEME_in_production_this_needs_to_be_secure")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    @property
    def allowed_origins(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, str):
            try:
                return json.loads(self.ALLOWED_ORIGINS)
            except Exception:
                return [self.ALLOWED_ORIGINS]
        return self.ALLOWED_ORIGINS

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
