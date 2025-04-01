from fastapi import APIRouter

# Import endpoint routers
# Uncomment these as you implement them
# from app.api.v1.endpoints.auth import router as auth_router
# from app.api.v1.endpoints.users import router as users_router
# from app.api.v1.endpoints.progress import router as progress_router
# from app.api.v1.endpoints.workouts import router as workouts_router

# Main router for API v1
api_router = APIRouter()

# Include the endpoint routers
# Uncomment these as you implement them
# api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(users_router, prefix="/users", tags=["Users"])
# api_router.include_router(progress_router, prefix="/progress", tags=["Progress"])
# api_router.include_router(workouts_router, prefix="/workouts", tags=["Workouts"])
