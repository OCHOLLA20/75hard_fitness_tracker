# app/api/v1/endpoints/workouts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from ....db.database import get_db
from ....core.auth import get_current_user

# Create workouts router
router = APIRouter()

# Schema for workout create/update
class WorkoutCreate(BaseModel):
    daily_progress_id: int
    workout_type: str  # "morning" or "evening"
    workout_category: str  # e.g., "Push", "Pull", "Legs", etc.
    duration_minutes: int
    was_outdoor: bool = False
    notes: Optional[str] = None

# Schema for workout response
class WorkoutResponse(WorkoutCreate):
    id: int
    user_id: int
    
    class Config:
        orm_mode = True

# Get all workouts
@router.get("/", response_model=List[WorkoutResponse])
async def get_all_workouts(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    # Import Workout model here to avoid circular imports
    from ....db.models import Workout
    
    workouts = db.query(Workout)\
        .filter(Workout.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return workouts

# Get a specific workout
@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Import Workout model here to avoid circular imports
    from ....db.models import Workout
    
    workout = db.query(Workout)\
        .filter(
            Workout.id == workout_id,
            Workout.user_id == current_user.id
        )\
        .first()
    
    if workout is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout with id {workout_id} not found"
        )
    
    return workout

# Create a new workout
@router.post("/", response_model=WorkoutResponse)
async def create_workout(
    workout_data: WorkoutCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Import models here to avoid circular imports
    from ....db.models import Workout, DailyProgress
    
    # Verify daily progress exists and belongs to the user
    daily_progress = db.query(DailyProgress)\
        .filter(
            DailyProgress.id == workout_data.daily_progress_id,
            DailyProgress.user_id == current_user.id
        )\
        .first()
    
    if daily_progress is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Daily progress with id {workout_data.daily_progress_id} not found"
        )
    
    # Create new workout
    new_workout = Workout(
        user_id=current_user.id,
        daily_progress_id=workout_data.daily_progress_id,
        workout_type=workout_data.workout_type,
        workout_category=workout_data.workout_category,
        duration_minutes=workout_data.duration_minutes,
        was_outdoor=workout_data.was_outdoor,
        notes=workout_data.notes
    )
    
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)
    
    # Update progress based on the workout type
    if workout_data.workout_type == "morning":
        daily_progress.morning_workout_completed = True
    elif workout_data.workout_type == "evening":
        daily_progress.evening_workout_completed = True
    
    # Check if all requirements are completed
    all_completed = all([
        daily_progress.morning_workout_completed,
        daily_progress.evening_workout_completed,
        daily_progress.water_intake >= 4,
        daily_progress.diet_followed,
        daily_progress.progress_photo_taken,
        daily_progress.reading_completed
    ])
    
    daily_progress.completed = all_completed
    db.commit()
    
    return new_workout

# Update a workout
@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: int,
    workout_data: WorkoutCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Import models here to avoid circular imports
    from ....db.models import Workout, DailyProgress
    
    # Verify workout exists and belongs to the user
    workout = db.query(Workout)\
        .filter(
            Workout.id == workout_id,
            Workout.user_id == current_user.id
        )\
        .first()
    
    if workout is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout with id {workout_id} not found"
        )
    
    # Verify daily progress exists and belongs to the user
    daily_progress = db.query(DailyProgress)\
        .filter(
            DailyProgress.id == workout_data.daily_progress_id,
            DailyProgress.user_id == current_user.id
        )\
        .first()
    
    if daily_progress is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Daily progress with id {workout_data.daily_progress_id} not found"
        )
    
    # Update workout
    workout.daily_progress_id = workout_data.daily_progress_id
    workout.workout_type = workout_data.workout_type
    workout.workout_category = workout_data.workout_category
    workout.duration_minutes = workout_data.duration_minutes
    workout.was_outdoor = workout_data.was_outdoor
    workout.notes = workout_data.notes
    
    db.commit()
    db.refresh(workout)
    
    return workout
