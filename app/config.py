import os

class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///default.db")
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
    CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")

class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///test.db")

class ProductionConfig(BaseConfig):
    """Production configuration."""
    DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///prod.db")
    SESSION_COOKIE_SECURE = True
