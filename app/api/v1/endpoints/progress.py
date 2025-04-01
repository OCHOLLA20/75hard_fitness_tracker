# app/api/v1/endpoints/progress.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date as date_type  # Renamed to avoid conflict

from ....db.database import get_db
from ....core.auth import get_current_user

# Create progress router
router = APIRouter()

# Schema for progress create/update
class ProgressUpdate(BaseModel):
    day_number: int
    date: Optional[date_type] = None  # Fixed: Using renamed import
    morning_workout_completed: bool = False
    evening_workout_completed: bool = False
    water_intake: int = 0
    diet_followed: bool = False
    progress_photo_taken: bool = False
    reading_completed: bool = False

# Schema for progress response
class ProgressResponse(ProgressUpdate):
    id: int
    user_id: int
    completed: bool
    
    class Config:
        orm_mode = True

# Get all progress records
@router.get("/", response_model=List[ProgressResponse])
async def get_all_progress(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    # Import DailyProgress model here to avoid circular imports
    from ....db.models import DailyProgress
    
    progress = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == current_user.id)\
        .order_by(DailyProgress.day_number)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return progress

# Get progress for a specific day
@router.get("/{day_number}", response_model=ProgressResponse)
async def get_progress_by_day(
    day_number: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Import DailyProgress model here to avoid circular imports
    from ....db.models import DailyProgress
    
    progress = db.query(DailyProgress)\
        .filter(
            DailyProgress.user_id == current_user.id,
            DailyProgress.day_number == day_number
        )\
        .first()
    
    if progress is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No progress found for day {day_number}"
        )
    
    return progress

# Create or update progress for a day
@router.post("/{day_number}", response_model=ProgressResponse)
async def create_or_update_progress(
    day_number: int,
    progress_data: ProgressUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Import DailyProgress model here to avoid circular imports
    from ....db.models import DailyProgress
    
    # Check if progress for this day already exists
    existing_progress = db.query(DailyProgress)\
        .filter(
            DailyProgress.user_id == current_user.id,
            DailyProgress.day_number == day_number
        )\
        .first()
    
    # Calculate if all requirements are completed
    all_completed = all([
        progress_data.morning_workout_completed,
        progress_data.evening_workout_completed,
        progress_data.water_intake >= 4,  # 4 liters required
        progress_data.diet_followed,
        progress_data.progress_photo_taken,
        progress_data.reading_completed
    ])
    
    if existing_progress:
        # Update existing progress
        existing_progress.morning_workout_completed = progress_data.morning_workout_completed
        existing_progress.evening_workout_completed = progress_data.evening_workout_completed
        existing_progress.water_intake = progress_data.water_intake
        existing_progress.diet_followed = progress_data.diet_followed
        existing_progress.progress_photo_taken = progress_data.progress_photo_taken
        existing_progress.reading_completed = progress_data.reading_completed
        existing_progress.completed = all_completed
        
        if progress_data.date:
            existing_progress.date = progress_data.date
        
        db.commit()
        db.refresh(existing_progress)
        return existing_progress
    else:
        # Create new progress
        new_progress = DailyProgress(
            user_id=current_user.id,
            day_number=day_number,
            date=progress_data.date or date_type.today(),  # Using renamed import
            morning_workout_completed=progress_data.morning_workout_completed,
            evening_workout_completed=progress_data.evening_workout_completed,
            water_intake=progress_data.water_intake,
            diet_followed=progress_data.diet_followed,
            progress_photo_taken=progress_data.progress_photo_taken,
            reading_completed=progress_data.reading_completed,
            completed=all_completed
        )
        
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        return new_progress