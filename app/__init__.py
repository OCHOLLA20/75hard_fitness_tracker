from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import Base, setup_database

# Initialize the database
setup_database()
from .db.database import engine
from .api.v1.router import api_router
from .core.config import settings

# Create and configure the FastAPI app
def create_app() -> FastAPI:
    """Initialize and configure the FastAPI application."""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Backend API for 75 Hard Fitness Challenge Tracker",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,  # This will now call the property method
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Add root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to 75 Hard Fitness Tracker API",
            "version": "1.0.0",
            "documentation": "/docs"
        }
    
    return app

# Version
__version__ = "1.0.0"
