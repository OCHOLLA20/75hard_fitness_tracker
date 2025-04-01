import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Configure logging for this module
logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

# Engine and session maker, initialized in setup_database
SessionLocal = None

def setup_database():
    """
    Initializes the SQLAlchemy database engine and session maker.
    Must be called before using SessionLocal or engine.
    """
    global engine, SessionLocal

    try:
        database_url = settings.DATABASE_URL
        if not database_url:
            raise ValueError("DATABASE_URL is not set in environment variables")

        logger.info(f"Connecting to database at {database_url}")

        # Special connect args for SQLite
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

        engine = create_engine(
            database_url,
            connect_args=connect_args,
            echo=settings.DB_ECHO_LOG
        )

        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        logger.info("Database connection established successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

def get_db():
    """
    Yields a SQLAlchemy session for dependency injection.
    Usage: Depends(get_db)
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call setup_database() first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
