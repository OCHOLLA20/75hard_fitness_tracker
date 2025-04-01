from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date


class ProgressBase(BaseModel):
    """Base schema with common progress tracking fields."""
    morning_workout_completed: bool = Field(default=False, description="First workout completed")
    evening_workout_completed: bool = Field(default=False, description="Second workout completed")
    water_intake: int = Field(
        default=0, 
        ge=0, 
        le=4, 
        description="Water intake in liters (0-4)"
    )
    diet_followed: bool = Field(default=False, description="Diet compliance for the day")
    progress_photo_taken: bool = Field(default=False, description="Daily progress photo taken")
    reading_completed: bool = Field(default=False, description="Daily reading requirement completed")


class ProgressCreate(ProgressBase):
    """Schema for creating a new progress record."""
    # Additional fields specific to creation can be added here
    pass


class ProgressUpdate(ProgressBase):
    """Schema for updating an existing progress record."""
    # All fields are optional for updates
    morning_workout_completed: Optional[bool] = None
    evening_workout_completed: Optional[bool] = None
    water_intake: Optional[int] = Field(None, ge=0, le=4)
    diet_followed: Optional[bool] = None
    progress_photo_taken: Optional[bool] = None
    reading_completed: Optional[bool] = None


class WorkoutBrief(BaseModel):
    """Brief workout information for inclusion in progress response."""
    id: int
    workout_type: str  # "morning" or "evening"
    workout_category: str
    duration_minutes: int
    was_outdoor: bool

    class Config:
        orm_mode = True


class ProgressResponse(ProgressBase):
    """Schema for returning progress data."""
    id: int
    user_id: int
    day_number: int
    date: date
    completed: bool
    workouts: List[WorkoutBrief] = []

    class Config:
        orm_mode = True


class ProgressStats(BaseModel):
    """Schema for progress statistics."""
    total_days: int
    completed_days: int
    completion_rate: float  # Percentage of days completed successfully
    current_streak: int  # Current streak of consecutive completed days
    longest_streak: int  # Longest streak of consecutive completed days
    water_intake_avg: float  # Average daily water intake
    most_missed_task: str  # The task that is most frequently missed


class DailyCompletionSummary(BaseModel):
    """Summary of daily completions by task type."""
    morning_workouts: int
    evening_workouts: int  
    diet_days: int
    photo_days: int
    reading_days: int
    water_goal_days: int  # Days where water intake goal was met
    perfect_days: int  # Days where all tasks were completed


class ProgressSummary(BaseModel):
    """Comprehensive progress summary."""
    stats: ProgressStats
    completion_summary: DailyCompletionSummary
    day_statuses: List[dict]  # List of day numbers and their completion status