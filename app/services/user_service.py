from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException, status

from ..db.models import User, DailyProgress, Workout
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieve a user by ID.
    
    Args:
        db: Database session
        user_id: ID of the user to retrieve
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieve a user by email.
    
    Args:
        db: Database session
        email: Email of the user to retrieve
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Retrieve a user by username.
    
    Args:
        db: Database session
        username: Username of the user to retrieve
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user.
    
    Args:
        db: Database session
        user_data: User data from request
        
    Returns:
        Created user object
    """
    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name if hasattr(user_data, 'full_name') else None,
        profile_image=user_data.profile_image if hasattr(user_data, 'profile_image') else None,
        challenge_start_date=user_data.challenge_start_date if hasattr(user_data, 'challenge_start_date') else None
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    """
    Update an existing user.
    
    Args:
        db: Database session
        user_id: ID of the user to update
        user_update: Updated user data
        
    Returns:
        Updated user object
    """
    # Find the user
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check for username uniqueness if being updated
    if user_update.username and user_update.username != db_user.username:
        existing_user = get_user_by_username(db, user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Check for email uniqueness if being updated
    if user_update.email and user_update.email != db_user.email:
        existing_user = get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update password if provided
    if user_update.password:
        user_update.hashed_password = get_password_hash(user_update.password)
        # Remove the plain password from the update data
        user_update.password = None
    
    # Update fields if provided in the request
    update_data = user_update.dict(exclude_unset=True, exclude={"password"})
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username/email and password.
    
    Args:
        db: Database session
        username_or_email: Username or email of the user
        password: Plain password to verify
        
    Returns:
        User object if authentication successful, None otherwise
    """
    # Try to find user by email
    user = get_user_by_email(db, username_or_email)
    
    # If not found by email, try by username
    if not user:
        user = get_user_by_username(db, username_or_email)
    
    # If user not found or password is incorrect
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    return user


def deactivate_user(db: Session, user_id: int) -> bool:
    """
    Deactivate a user account.
    
    Args:
        db: Database session
        user_id: ID of the user to deactivate
        
    Returns:
        True if deactivated successfully, False otherwise
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db_user.is_active = False
    db.commit()
    
    return True


def reactivate_user(db: Session, user_id: int) -> bool:
    """
    Reactivate a deactivated user account.
    
    Args:
        db: Database session
        user_id: ID of the user to reactivate
        
    Returns:
        True if reactivated successfully, False otherwise
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db_user.is_active = True
    db.commit()
    
    return True


def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
    """
    Change a user's password.
    
    Args:
        db: Database session
        user_id: ID of the user
        current_password: Current password for verification
        new_password: New password to set
        
    Returns:
        True if password changed successfully, False otherwise
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(current_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Set new password
    db_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return True


def get_user_challenge_status(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get the current status of a user's 75 Hard challenge.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary containing challenge status information
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get all daily progress records for the user
    progress_records = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id)\
        .order_by(DailyProgress.day_number)\
        .all()
    
    # Calculate current day and completion stats
    total_days = len(progress_records)
    completed_days = sum(1 for p in progress_records if p.completed)
    current_day = total_days + 1 if total_days < 75 else 75
    
    # Find current streak (consecutive completed days)
    current_streak = 0
    for p in reversed(progress_records):
        if p.completed:
            current_streak += 1
        else:
            break
    
    # Calculate longest streak
    longest_streak = 0
    current_count = 0
    for p in progress_records:
        if p.completed:
            current_count += 1
            longest_streak = max(longest_streak, current_count)
        else:
            current_count = 0
    
    # Determine challenge status
    if total_days >= 75 and completed_days == 75:
        status = "Completed"
    elif db_user.challenge_start_date:
        days_since_start = (datetime.now().date() - db_user.challenge_start_date).days + 1
        if days_since_start > total_days + 1:
            status = "Behind"
        else:
            status = "In Progress"
    else:
        status = "Not Started"
    
    # Calculate expected completion date if challenge has started
    expected_completion_date = None
    if db_user.challenge_start_date:
        expected_completion_date = db_user.challenge_start_date + timedelta(days=74)
    
    # Calculate adjusted completion date based on failed days
    adjusted_completion_date = None
    if db_user.challenge_start_date and total_days > 0:
        failed_days = total_days - completed_days
        adjusted_completion_date = expected_completion_date + timedelta(days=failed_days) if expected_completion_date else None
    
    return {
        "status": status,
        "current_day": current_day,
        "total_days_tracked": total_days,
        "total_days_completed": completed_days,
        "completion_percentage": round(completed_days / 75 * 100, 1),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "challenge_start_date": db_user.challenge_start_date,
        "expected_completion_date": expected_completion_date,
        "adjusted_completion_date": adjusted_completion_date
    }


def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get comprehensive statistics for a user's 75 Hard journey.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary containing user statistics
    """
    # Get challenge status
    challenge_status = get_user_challenge_status(db, user_id)
    
    # Total workouts completed
    total_workouts = db.query(func.count(Workout.id))\
        .filter(Workout.user_id == user_id)\
        .scalar() or 0
    
    # Count of workout types
    morning_workouts = db.query(func.count(Workout.id))\
        .filter(Workout.user_id == user_id, Workout.workout_type == "morning")\
        .scalar() or 0
    
    evening_workouts = db.query(func.count(Workout.id))\
        .filter(Workout.user_id == user_id, Workout.workout_type == "evening")\
        .scalar() or 0
    
    # Count of outdoor workouts
    outdoor_workouts = db.query(func.count(Workout.id))\
        .filter(Workout.user_id == user_id, Workout.was_outdoor == True)\
        .scalar() or 0
    
    # Average workout duration
    avg_duration = db.query(func.avg(Workout.duration_minutes))\
        .filter(Workout.user_id == user_id)\
        .scalar() or 0
    
    # Total water intake (in liters)
    total_water = db.query(func.sum(DailyProgress.water_intake))\
        .filter(DailyProgress.user_id == user_id)\
        .scalar() or 0
    
    # Recent progress - last 5 days
    recent_progress = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id)\
        .order_by(desc(DailyProgress.day_number))\
        .limit(5)\
        .all()
    
    # Get daily tasks completion rate
    progress_records = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id)\
        .all()
    
    task_completion = {
        "morning_workouts": sum(1 for p in progress_records if p.morning_workout_completed),
        "evening_workouts": sum(1 for p in progress_records if p.evening_workout_completed),
        "diet_adherence": sum(1 for p in progress_records if p.diet_followed),
        "water_intake": sum(1 for p in progress_records if p.water_intake >= 4),
        "progress_photos": sum(1 for p in progress_records if p.progress_photo_taken),
        "reading": sum(1 for p in progress_records if p.reading_completed)
    }
    
    # Calculate task completion percentages
    total_days = len(progress_records)
    task_completion_percentage = {
        key: round(value / total_days * 100, 1) if total_days else 0
        for key, value in task_completion.items()
    }
    
    return {
        "challenge_status": challenge_status,
        "workout_stats": {
            "total_workouts": total_workouts,
            "morning_workouts": morning_workouts,
            "evening_workouts": evening_workouts,
            "outdoor_workouts": outdoor_workouts,
            "outdoor_percentage": round(outdoor_workouts / total_workouts * 100, 1) if total_workouts else 0,
            "avg_duration_minutes": round(float(avg_duration), 1) if avg_duration else 0
        },
        "wellness_stats": {
            "total_water_intake_liters": total_water,
            "avg_daily_water_liters": round(total_water / total_days, 1) if total_days else 0
        },
        "task_completion": task_completion,
        "task_completion_percentage": task_completion_percentage,
        "recent_progress": recent_progress
    }


def start_challenge(db: Session, user_id: int, start_date=None) -> Dict[str, Any]:
    """
    Start the 75 Hard challenge for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        start_date: Optional specific start date, defaults to today
        
    Returns:
        Dictionary with challenge start information
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Set start date to today if not specified
    if not start_date:
        start_date = datetime.now().date()
    
    # Check if user already has progress records
    existing_progress = db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id)\
        .first()
    
    if existing_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge already started. Reset progress first if you want to restart."
        )
    
    # Set challenge start date for user
    db_user.challenge_start_date = start_date
    db.commit()
    
    # Calculate expected completion date
    expected_completion_date = start_date + timedelta(days=74)
    
    return {
        "message": "75 Hard challenge started successfully",
        "start_date": start_date,
        "expected_completion_date": expected_completion_date
    }


def reset_challenge(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Reset the 75 Hard challenge for a user, removing all progress.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary with reset confirmation
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete all workouts for the user
    db.query(Workout)\
        .filter(Workout.user_id == user_id)\
        .delete(synchronize_session=False)
    
    # Delete all daily progress records for the user
    db.query(DailyProgress)\
        .filter(DailyProgress.user_id == user_id)\
        .delete(synchronize_session=False)
    
    # Reset challenge start date
    db_user.challenge_start_date = None
    
    db.commit()
    
    return {
        "message": "75 Hard challenge progress has been reset successfully",
        "user_id": user_id
    }


def get_latest_day_number(db: Session, user_id: int) -> int:
    """
    Get the latest day number for a user's challenge.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Latest day number (0 if no progress records exist)
    """
    latest_day = db.query(func.max(DailyProgress.day_number))\
        .filter(DailyProgress.user_id == user_id)\
        .scalar() or 0
    
    return latest_day
