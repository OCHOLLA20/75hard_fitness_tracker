# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ....db.database import get_db
from ....core.auth import get_current_user

# Create users router
router = APIRouter()

# Schema for user response
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    
    class Config:
        orm_mode = True

# Schema for user update
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

# Get current user profile
@router.get("/me", response_model=UserResponse)
async def get_user_profile(current_user = Depends(get_current_user)):
    return current_user

# Update user profile
@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Import User model here to avoid circular imports
    from ....db.models import User
    
    db_user = db.query(User).filter(User.id == current_user.id).first()
    
    if user_update.username is not None:
        db_user.username = user_update.username
    
    if user_update.email is not None:
        # Check if email is already taken
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        db_user.email = user_update.email
    
    db.commit()
    db.refresh(db_user)
    
    return db_user
