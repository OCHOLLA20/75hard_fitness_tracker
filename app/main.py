from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
import os

# Import the router
from app.api.v1.router import api_router
# Import settings from config
from app.core.config import settings
# Import database functions
from app.db.database import setup_database, engine, Base
# Import auth function - needed for the /me endpoint
from app.core.auth import get_current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Ensure necessary directories exist
os.makedirs("app/db", exist_ok=True)

# Initialize database first
setup_database()

# Initialize the FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for tracking progress in the 75 Hard Fitness Challenge",
    version="1.0.0",
)

# Create database tables after engine is initialized
try:
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    raise

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Updated to use the property method
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing basic information about the API.
    """
    return {
        "message": "Welcome to 75 Hard Fitness Tracker API",
        "version": "1.0.0",
        "documentation": f"{settings.API_V1_STR}/docs"
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"}

# User info endpoint - commented out until auth is fully implemented
# @app.get("/me", tags=["User"])
# async def read_users_me(current_user = Depends(get_current_user)):
#     """
#     Get information about the currently authenticated user.
#     """
#     return current_user

# Only run the server if this file is executed directly
if __name__ == "__main__":
    logger.info(f"Starting 75 Hard API server on port {settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )
