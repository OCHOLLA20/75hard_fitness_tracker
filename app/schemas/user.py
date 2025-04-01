from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base User Schema with common attributes."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username for account")
    
    @validator('username')
    def username_must_be_valid(cls, v):
        """Validate that username meets requirements."""
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 30:
            raise ValueError('Username must be less than 30 characters')
        if not v.isalnum() and not any(c in '_-' for c in v):
            raise ValueError('Username must contain only alphanumeric characters, underscores, or hyphens')
        return v

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., description="User's password")
    
    @validator('password')
    def password_must_be_strong(cls, v):
        """Validate that password meets strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    username: Optional[str] = Field(None, description="Username for account")
    password: Optional[str] = Field(None, description="User's password")
    
    @validator('username')
    def username_must_be_valid(cls, v):
        """Validate that username meets requirements if provided."""
        if v is not None:
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters')
            if len(v) > 30:
                raise ValueError('Username must be less than 30 characters')
            if not v.isalnum() and not any(c in '_-' for c in v):
                raise ValueError('Username must contain only alphanumeric characters, underscores, or hyphens')
        return v
    
    @validator('password')
    def password_must_be_strong(cls, v):
        """Validate that password meets strength requirements if provided."""
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters')
            if not any(c.isupper() for c in v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not any(c.isdigit() for c in v):
                raise ValueError('Password must contain at least one number')
        return v

class UserInDB(UserBase):
    """Schema for user as stored in the database."""
    id: int
    is_active: bool = True
    created_at: datetime
    
    class Config:
        orm_mode = True  # For Pydantic v1

class UserResponse(UserBase):
    """Schema for user responses (excludes sensitive information)."""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True  # For Pydantic v1

class UserStats(BaseModel):
    """Schema for user statistics."""
    total_days_completed: int = Field(..., description="Total number of days completed")
    current_streak: int = Field(..., description="Current streak of consecutive days")
    longest_streak: int = Field(..., description="Longest streak of consecutive days")
    completion_rate: float = Field(..., description="Percentage of days successfully completed")
    favorite_workout_category: Optional[str] = Field(None, description="Most common workout category")
    total_workout_minutes: int = Field(..., description="Total minutes spent working out")
    
    class Config:
        orm_mode = True  # For Pydantic v1
