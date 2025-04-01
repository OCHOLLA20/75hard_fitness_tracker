import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date

from app.main import app
from app.db.models import User, DailyProgress, Workout
from app.core.auth import create_access_token
from app.services.user_service import create_user
from app.schemas.user import UserCreate

client = TestClient(app)

@pytest.fixture
def test_user(db: Session):
    """Create a test user for authentication"""
    user_data = UserCreate(
        email="workout_test@example.com",
        username="workout_tester",
        password="testpassword"
    )
    user = create_user(db, user_data)
    return user

@pytest.fixture
def test_token(test_user: User):
    """Create a test token for authentication"""
    return create_access_token(data={"sub": test_user.email})

@pytest.fixture
def authenticated_client(test_token: str):
    """Create a test client with authentication headers"""
    test_client = TestClient(app)
    test_client.headers = {
        "Authorization": f"Bearer {test_token}"
    }
    return test_client

@pytest.fixture
def test_daily_progress(db: Session, test_user: User):
    """Create a test daily progress entry"""
    progress = DailyProgress(
        user_id=test_user.id,
        day_number=1,
        date=date.today(),
        morning_workout_completed=False,
        evening_workout_completed=False,
        water_intake=0,
        diet_followed=False,
        progress_photo_taken=False,
        reading_completed=False,
        completed=False
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress

@pytest.fixture
def test_workout(db: Session, test_user: User, test_daily_progress: DailyProgress):
    """Create a test workout entry"""
    workout = Workout(
        user_id=test_user.id,
        daily_progress_id=test_daily_progress.id,
        workout_type="morning",
        workout_category="Push",
        duration_minutes=45,
        was_outdoor=False,
        notes="Test workout"
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout

def test_create_workout(authenticated_client, test_user: User, test_daily_progress: DailyProgress):
    """Test creating a new workout"""
    workout_data = {
        "workout_type": "evening",
        "workout_category": "Pull",
        "duration_minutes": 60,
        "was_outdoor": True,
        "notes": "Evening pull workout",
        "daily_progress_id": test_daily_progress.id
    }
    
    response = authenticated_client.post("/api/v1/workouts", json=workout_data)
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["workout_type"] == "evening"
    assert data["workout_category"] == "Pull"
    assert data["duration_minutes"] == 60
    assert data["was_outdoor"] is True
    assert data["notes"] == "Evening pull workout"
    assert data["user_id"] == test_user.id
    assert data["daily_progress_id"] == test_daily_progress.id

def test_get_workouts(authenticated_client, test_workout: Workout):
    """Test getting all workouts for a user"""
    response = authenticated_client.get("/api/v1/workouts")
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == test_workout.id
    assert data[0]["workout_type"] == test_workout.workout_type
    assert data[0]["workout_category"] == test_workout.workout_category
    assert data[0]["duration_minutes"] == test_workout.duration_minutes

def test_get_workout_by_id(authenticated_client, test_workout: Workout):
    """Test getting a specific workout by ID"""
    response = authenticated_client.get(f"/api/v1/workouts/{test_workout.id}")
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_workout.id
    assert data["workout_type"] == test_workout.workout_type
    assert data["workout_category"] == test_workout.workout_category
    assert data["duration_minutes"] == test_workout.duration_minutes
    assert data["was_outdoor"] == test_workout.was_outdoor
    assert data["notes"] == test_workout.notes

def test_update_workout(authenticated_client, test_workout: Workout):
    """Test updating a workout"""
    update_data = {
        "workout_type": test_workout.workout_type,
        "workout_category": "Legs",  # Changed from Push to Legs
        "duration_minutes": 75,  # Changed from 45 to 75
        "was_outdoor": True,  # Changed from False to True
        "notes": "Updated workout notes"  # Changed notes
    }
    
    response = authenticated_client.put(f"/api/v1/workouts/{test_workout.id}", json=update_data)
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_workout.id
    assert data["workout_type"] == test_workout.workout_type  # Unchanged
    assert data["workout_category"] == "Legs"  # Changed
    assert data["duration_minutes"] == 75  # Changed
    assert data["was_outdoor"] is True  # Changed
    assert data["notes"] == "Updated workout notes"  # Changed

def test_get_nonexistent_workout(authenticated_client):
    """Test getting a workout that doesn't exist"""
    response = authenticated_client.get("/api/v1/workouts/999999")
    
    # Assert response
    assert response.status_code == 404
    assert "detail" in response.json()

def test_update_nonexistent_workout(authenticated_client):
    """Test updating a workout that doesn't exist"""
    update_data = {
        "workout_type": "morning",
        "workout_category": "Cardio",
        "duration_minutes": 30,
        "was_outdoor": True,
        "notes": "This workout doesn't exist"
    }
    
    response = authenticated_client.put("/api/v1/workouts/999999", json=update_data)
    
    # Assert response
    assert response.status_code == 404
    assert "detail" in response.json()

def test_create_workout_with_invalid_data(authenticated_client, test_daily_progress: DailyProgress):
    """Test creating a workout with invalid data"""
    # Missing required field (workout_category)
    invalid_data = {
        "workout_type": "morning",
        "duration_minutes": 45,
        "was_outdoor": False,
        "notes": "Invalid workout data",
        "daily_progress_id": test_daily_progress.id
    }
    
    response = authenticated_client.post("/api/v1/workouts", json=invalid_data)
    
    # Assert response
    assert response.status_code == 422  # Unprocessable Entity

def test_update_workout_with_invalid_data(authenticated_client, test_workout: Workout):
    """Test updating a workout with invalid data"""
    # Invalid duration (negative minutes)
    invalid_data = {
        "workout_type": "morning",
        "workout_category": "Push",
        "duration_minutes": -10,  # Invalid duration
        "was_outdoor": False,
        "notes": "Invalid workout data"
    }
    
    response = authenticated_client.put(f"/api/v1/workouts/{test_workout.id}", json=invalid_data)
    
    # Assert response
    assert response.status_code == 422  # Unprocessable Entity

def test_unauthorized_access(test_workout: Workout):
    """Test accessing workouts without authentication"""
    # Client without authentication token
    unauthenticated_client = TestClient(app)
    
    # Try to get workouts
    response = unauthenticated_client.get("/api/v1/workouts")
    assert response.status_code == 401  # Unauthorized
    
    # Try to get specific workout
    response = unauthenticated_client.get(f"/api/v1/workouts/{test_workout.id}")
    assert response.status_code == 401  # Unauthorized
    
    # Try to create workout
    workout_data = {
        "workout_type": "evening",
        "workout_category": "Pull",
        "duration_minutes": 60,
        "was_outdoor": True,
        "notes": "Evening pull workout"
    }
    response = unauthenticated_client.post("/api/v1/workouts", json=workout_data)
    assert response.status_code == 401  # Unauthorized
    
    # Try to update workout
    response = unauthenticated_client.put(f"/api/v1/workouts/{test_workout.id}", json=workout_data)
    assert response.status_code == 401  # Unauthorized

def test_get_workouts_by_date_range(authenticated_client, test_workout: Workout, db: Session, test_user: User, test_daily_progress: DailyProgress):
    """Test filtering workouts by date range"""
    # Create another workout for tomorrow
    tomorrow_progress = DailyProgress(
        user_id=test_user.id,
        day_number=2,
        date=date.today().replace(day=date.today().day + 1),  # Tomorrow
        morning_workout_completed=False,
        evening_workout_completed=False,
        water_intake=0,
        diet_followed=False,
        progress_photo_taken=False,
        reading_completed=False,
        completed=False
    )
    db.add(tomorrow_progress)
    db.commit()
    db.refresh(tomorrow_progress)
    
    tomorrow_workout = Workout(
        user_id=test_user.id,
        daily_progress_id=tomorrow_progress.id,
        workout_type="morning",
        workout_category="Cardio",
        duration_minutes=30,
        was_outdoor=True,
        notes="Tomorrow's workout"
    )
    db.add(tomorrow_workout)
    db.commit()
    db.refresh(tomorrow_workout)
    
    # Test filtering by date range
    today = date.today().isoformat()
    tomorrow = date.today().replace(day=date.today().day + 1).isoformat()
    
    # Get only today's workouts
    response = authenticated_client.get(f"/api/v1/workouts?start_date={today}&end_date={today}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_workout.id
    
    # Get all workouts (today and tomorrow)
    response = authenticated_client.get(f"/api/v1/workouts?start_date={today}&end_date={tomorrow}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    workout_ids = [workout["id"] for workout in data]
    assert test_workout.id in workout_ids
    assert tomorrow_workout.id in workout_ids

def test_get_workouts_by_type(authenticated_client, test_workout: Workout, db: Session, test_user: User, test_daily_progress: DailyProgress):
    """Test filtering workouts by type (morning/evening)"""
    # Create an evening workout
    evening_workout = Workout(
        user_id=test_user.id,
        daily_progress_id=test_daily_progress.id,
        workout_type="evening",
        workout_category="Abs",
        duration_minutes=20,
        was_outdoor=False,
        notes="Evening abs workout"
    )
    db.add(evening_workout)
    db.commit()
    db.refresh(evening_workout)
    
    # Get only morning workouts
    response = authenticated_client.get("/api/v1/workouts?workout_type=morning")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for workout in data:
        assert workout["workout_type"] == "morning"
    
    # Get only evening workouts
    response = authenticated_client.get("/api/v1/workouts?workout_type=evening")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for workout in data:
        assert workout["workout_type"] == "evening"

def test_get_workouts_by_category(authenticated_client, test_workout: Workout, db: Session, test_user: User, test_daily_progress: DailyProgress):
    """Test filtering workouts by category"""
    # Create a workout with different category
    cardio_workout = Workout(
        user_id=test_user.id,
        daily_progress_id=test_daily_progress.id,
        workout_type="evening",
        workout_category="Cardio",
        duration_minutes=45,
        was_outdoor=True,
        notes="Cardio workout"
    )
    db.add(cardio_workout)
    db.commit()
    db.refresh(cardio_workout)
    
    # Get only Push workouts
    response = authenticated_client.get("/api/v1/workouts?category=Push")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for workout in data:
        assert workout["workout_category"] == "Push"
    
    # Get only Cardio workouts
    response = authenticated_client.get("/api/v1/workouts?category=Cardio")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for workout in data:
        assert workout["workout_category"] == "Cardio"
