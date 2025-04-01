from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException, status

from ..db.models import Workout, DailyProgress, User
from ..schemas.workout import WorkoutCreate, WorkoutUpdate


def get_workouts(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Workout]:
    """
    Retrieve all workouts for a specific user.
    
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of workout objects
    """
    return db.query(Workout)\
        .filter(Workout.user_id == user_id)\
        .order_by(desc(Workout.id))\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_workout_by_id(db: Session, workout_id: int, user_id: int) -> Optional[Workout]:
    """
    Retrieve a specific workout by ID.
    
    Args:
        db: Database session
        workout_id: ID of the workout to retrieve
        user_id: ID of the user (for authorization)
        
    Returns:
        Workout object if found, None otherwise
    """
    return db.query(Workout)\
        .filter(Workout.id == workout_id, Workout.user_id == user_id)\
        .first()


def get_workouts_by_date(db: Session, user_id: int, target_date: date) -> List[Workout]:
    """
    Retrieve all workouts for a specific date.
    
    Args:
        db: Database session
        user_id: ID of the user
        target_date: Date to filter workouts
        
    Returns:
        List of workout objects for the specified date
    """
    # Find the daily progress ID for the specified date
    daily_progress = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id, DailyProgress.date == target_date)\
        .first()
        
    if not daily_progress:
        return []
        
    return db.query(Workout)\
        .filter(
            Workout.user_id == user_id, 
            Workout.daily_progress_id == daily_progress.id
        )\
        .all()


def get_workouts_by_day_number(db: Session, user_id: int, day_number: int) -> List[Workout]:
    """
    Retrieve all workouts for a specific day number in the 75 Hard challenge.
    
    Args:
        db: Database session
        user_id: ID of the user
        day_number: Day number in the 75 Hard challenge (1-75)
        
    Returns:
        List of workout objects for the specified day
    """
    # Find the daily progress ID for the specified day number
    daily_progress = db.query(DailyProgress)\
        .filter(
            DailyProgress.user_id == user_id, 
            DailyProgress.day_number == day_number
        )\
        .first()
        
    if not daily_progress:
        return []
        
    return db.query(Workout)\
        .filter(
            Workout.user_id == user_id, 
            Workout.daily_progress_id == daily_progress.id
        )\
        .all()


def create_workout(
    db: Session, 
    workout: WorkoutCreate, 
    user_id: int, 
    daily_progress_id: int
) -> Workout:
    """
    Create a new workout record.
    
    Args:
        db: Database session
        workout: Workout data from request
        user_id: ID of the user
        daily_progress_id: ID of the daily progress record
        
    Returns:
        Created workout object
    """
    # Validate daily progress exists and belongs to user
    daily_progress = db.query(DailyProgress)\
        .filter(
            DailyProgress.id == daily_progress_id,
            DailyProgress.user_id == user_id
        )\
        .first()
        
    if not daily_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily progress record not found"
        )
    
    # Check if this type of workout (morning/evening) already exists for this day
    existing_workout = db.query(Workout)\
        .filter(
            Workout.daily_progress_id == daily_progress_id,
            Workout.workout_type == workout.workout_type
        )\
        .first()
        
    if existing_workout:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{workout.workout_type.capitalize()} workout already exists for this day"
        )
    
    # Create new workout
    db_workout = Workout(
        user_id=user_id,
        daily_progress_id=daily_progress_id,
        workout_type=workout.workout_type,
        workout_category=workout.workout_category,
        duration_minutes=workout.duration_minutes,
        was_outdoor=workout.was_outdoor,
        notes=workout.notes
    )
    
    db.add(db_workout)
    
    # Update the daily progress record based on workout type
    if workout.workout_type == "morning":
        daily_progress.morning_workout_completed = True
    elif workout.workout_type == "evening":
        daily_progress.evening_workout_completed = True
    
    # Check if all daily requirements are now met
    update_daily_completion_status(db, daily_progress)
    
    db.commit()
    db.refresh(db_workout)
    
    return db_workout


def update_workout(
    db: Session, 
    workout_id: int, 
    workout_update: WorkoutUpdate, 
    user_id: int
) -> Optional[Workout]:
    """
    Update an existing workout.
    
    Args:
        db: Database session
        workout_id: ID of the workout to update
        workout_update: Updated workout data
        user_id: ID of the user (for authorization)
        
    Returns:
        Updated workout object if successful, None otherwise
    """
    # Find the workout
    db_workout = get_workout_by_id(db, workout_id, user_id)
    
    if not db_workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    # If changing workout type, check for conflicts
    if workout_update.workout_type and workout_update.workout_type != db_workout.workout_type:
        existing_workout = db.query(Workout)\
            .filter(
                Workout.daily_progress_id == db_workout.daily_progress_id,
                Workout.workout_type == workout_update.workout_type,
                Workout.id != workout_id
            )\
            .first()
            
        if existing_workout:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{workout_update.workout_type.capitalize()} workout already exists for this day"
            )
    
    # Update fields if provided in the request
    update_data = workout_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_workout, key, value)
    
    # Get related daily progress
    daily_progress = db.query(DailyProgress)\
        .filter(DailyProgress.id == db_workout.daily_progress_id)\
        .first()
    
    # Update daily progress completion flags based on workout type
    if daily_progress:
        if db_workout.workout_type == "morning":
            daily_progress.morning_workout_completed = True
        elif db_workout.workout_type == "evening":
            daily_progress.evening_workout_completed = True
        
        # Check if all daily requirements are now met
        update_daily_completion_status(db, daily_progress)
    
    db.commit()
    db.refresh(db_workout)
    
    return db_workout


def delete_workout(db: Session, workout_id: int, user_id: int) -> bool:
    """
    Delete a workout by ID.
    
    Args:
        db: Database session
        workout_id: ID of the workout to delete
        user_id: ID of the user (for authorization)
        
    Returns:
        True if deleted successfully, False otherwise
    """
    # Find the workout
    db_workout = get_workout_by_id(db, workout_id, user_id)
    
    if not db_workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    # Store workout type and daily progress ID before deletion
    workout_type = db_workout.workout_type
    daily_progress_id = db_workout.daily_progress_id
    
    # Delete the workout
    db.delete(db_workout)
    
    # Update daily progress completion flags
    daily_progress = db.query(DailyProgress)\
        .filter(DailyProgress.id == daily_progress_id)\
        .first()
        
    if daily_progress:
        if workout_type == "morning":
            daily_progress.morning_workout_completed = False
        elif workout_type == "evening":
            daily_progress.evening_workout_completed = False
        
        # Update completion status
        update_daily_completion_status(db, daily_progress)
    
    db.commit()
    
    return True


def get_workout_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get workout statistics for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary containing workout statistics
    """
    # Get total workout count
    total_workouts = db.query(func.count(Workout.id))\
        .filter(Workout.user_id == user_id)\
        .scalar() or 0
    
    # Get outdoor workout count
    outdoor_workouts = db.query(func.count(Workout.id))\
        .filter(Workout.user_id == user_id, Workout.was_outdoor == True)\
        .scalar() or 0
    
    # Get average workout duration
    avg_duration = db.query(func.avg(Workout.duration_minutes))\
        .filter(Workout.user_id == user_id)\
        .scalar() or 0
    
    # Get category distribution
    category_query = db.query(
            Workout.workout_category, 
            func.count(Workout.id).label('count')
        )\
        .filter(Workout.user_id == user_id)\
        .group_by(Workout.workout_category)\
        .all()
    
    category_distribution = {category: count for category, count in category_query}
    
    # Get recent workouts
    recent_workouts = db.query(Workout)\
        .filter(Workout.user_id == user_id)\
        .order_by(desc(Workout.id))\
        .limit(5)\
        .all()
    
    return {
        "total_workouts": total_workouts,
        "outdoor_workouts": outdoor_workouts,
        "outdoor_percentage": round((outdoor_workouts / total_workouts * 100) if total_workouts else 0, 1),
        "avg_duration_minutes": round(float(avg_duration), 1) if avg_duration else 0,
        "category_distribution": category_distribution,
        "recent_workouts": recent_workouts
    }


def update_daily_completion_status(db: Session, daily_progress: DailyProgress) -> None:
    """
    Update the completion status of a daily progress record.
    
    Args:
        db: Database session
        daily_progress: DailyProgress object to update
        
    Returns:
        None
    """
    # Check if all requirements are met
    daily_progress.completed = all([
        daily_progress.morning_workout_completed,
        daily_progress.evening_workout_completed,
        daily_progress.water_intake >= 4,  # 4 liters minimum
        daily_progress.diet_followed,
        daily_progress.progress_photo_taken,
        daily_progress.reading_completed
    ])