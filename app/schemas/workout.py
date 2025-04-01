from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum

# Enum for workout types
class WorkoutType(str, Enum):
    """Enum for the two required daily workout types in 75 Hard challenge."""
    MORNING = "morning"
    EVENING = "evening"

# Enum for common workout categories (for reference, not enforced)
class WorkoutCategory(str, Enum):
    """Common workout categories (reference only, not enforced)."""
    PUSH = "push"
    PULL = "pull"
    LEGS = "legs"
    CARDIO = "cardio"
    HIIT = "hiit"
    YOGA = "yoga"
    FLEXIBILITY = "flexibility"
    STRENGTH = "strength"
    OTHER = "other"

class WorkoutBase(BaseModel):
    """Base Workout Schema with common attributes."""
    workout_type: WorkoutType = Field(..., description="Type of workout: 'morning' or 'evening'")
    workout_category: str = Field(..., description="Category of workout e.g., 'Push', 'Pull', 'Legs'")
    duration_minutes: int = Field(..., description="Duration of workout in minutes")
    was_outdoor: bool = Field(default=False, description="Whether the workout was performed outdoors")
    notes: Optional[str] = Field(None, description="Additional notes about the workout")

    @validator('duration_minutes')
    def duration_must_be_positive(cls, v):
        """Validate that workout duration is positive."""
        if v <= 0:
            raise ValueError('Duration must be greater than 0 minutes')
        return v

class WorkoutCreate(WorkoutBase):
    """Schema for creating a new workout."""
    daily_progress_id: int = Field(..., description="ID of the daily progress record this workout belongs to")

class WorkoutUpdate(BaseModel):
    """Schema for updating an existing workout."""
    workout_type: Optional[WorkoutType] = Field(None, description="Type of workout: 'morning' or 'evening'")
    workout_category: Optional[str] = Field(None, description="Category of workout")
    duration_minutes: Optional[int] = Field(None, description="Duration of workout in minutes")
    was_outdoor: Optional[bool] = Field(None, description="Whether the workout was performed outdoors")
    notes: Optional[str] = Field(None, description="Additional notes about the workout")

    @validator('duration_minutes')
    def duration_must_be_positive(cls, v):
        """Validate that workout duration is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError('Duration must be greater than 0 minutes')
        return v

class WorkoutInDB(WorkoutBase):
    """Schema for workout as stored in the database."""
    id: int
    user_id: int
    daily_progress_id: int

    class Config:
        orm_mode = True  # For Pydantic V1

class WorkoutResponse(WorkoutInDB):
    """Schema for workout responses (includes all fields)."""
    pass
