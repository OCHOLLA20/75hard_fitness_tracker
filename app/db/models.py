from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    progress = relationship("DailyProgress", back_populates="user", cascade="all, delete-orphan")
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")

class DailyProgress(Base):
    __tablename__ = "daily_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day_number = Column(Integer)  # 1-75
    date = Column(Date)
    morning_workout_completed = Column(Boolean, default=False)
    evening_workout_completed = Column(Boolean, default=False)
    water_intake = Column(Integer, default=0)  # in liters (0-4)
    diet_followed = Column(Boolean, default=False)
    progress_photo_taken = Column(Boolean, default=False)
    reading_completed = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)  # Overall day completed
    
    # Relationships
    user = relationship("User", back_populates="progress")
    workouts = relationship("Workout", back_populates="daily_progress", cascade="all, delete-orphan")

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    daily_progress_id = Column(Integer, ForeignKey("daily_progress.id"))
    workout_type = Column(String)  # "morning" or "evening"
    workout_category = Column(String)  # e.g., "Push", "Pull", "Legs", etc.
    duration_minutes = Column(Integer)
    was_outdoor = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="workouts")
    daily_progress = relationship("DailyProgress", back_populates="workouts")