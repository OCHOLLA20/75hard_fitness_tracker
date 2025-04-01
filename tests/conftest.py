import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import os
import random

# Import the main application
from app.main import app
from app.db.database import Base, get_db
from app.db.models import User, DailyProgress, Workout
from app.core.auth import create_access_token, get_password_hash
from app.core.config import settings

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test data
TEST_USERS = [
    {"email": "user1@example.com", "username": "testuser1", "password": "password123"},
    {"email": "user2@example.com", "username": "testuser2", "password": "password456"}
]

WORKOUT_CATEGORIES = ["Push", "Pull", "Legs", "Cardio", "Yoga", "Outdoor Walk", "HIIT"]


@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    # Clean up
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="function")
def db(db_engine):
    """Create a new database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Create test users
    for user_data in TEST_USERS:
        hashed_password = get_password_hash(user_data["password"])
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=hashed_password
        )
        session.add(user)
    
    session.commit()
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
            session.commit()
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield session
    
    # Tear down
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(db):
    """Create a test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def test_user(db):
    """Return a test user."""
    return db.query(User).filter(User.email == TEST_USERS[0]["email"]).first()


@pytest.fixture(scope="function")
def test_user_token(test_user):
    """Create access token for test user."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture(scope="function")
def auth_headers(test_user_token):
    """Headers with bearer token for authenticated requests."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture(scope="function")
def create_test_progress(db, test_user):
    """Create test progress data for a user."""
    progress_data = []
    
    for day in range(1, 11):  # Create 10 days of progress data
        today = datetime.now().date() - timedelta(days=10-day)
        is_completed = random.choice([True, False])
        
        progress = DailyProgress(
            user_id=test_user.id,
            day_number=day,
            date=today,
            morning_workout_completed=is_completed,
            evening_workout_completed=is_completed,
            water_intake=random.randint(2, 4),
            diet_followed=is_completed,
            progress_photo_taken=is_completed,
            reading_completed=is_completed,
            completed=is_completed
        )
        db.add(progress)
        progress_data.append(progress)
    
    db.commit()
    
    for progress in progress_data:
        # Create workouts for progress days
        if progress.morning_workout_completed:
            morning_workout = Workout(
                user_id=test_user.id,
                daily_progress_id=progress.id,
                workout_type="morning",
                workout_category=random.choice(WORKOUT_CATEGORIES),
                duration_minutes=random.randint(30, 90),
                was_outdoor=random.choice([True, False]),
                notes=f"Test morning workout on day {progress.day_number}"
            )
            db.add(morning_workout)
        
        if progress.evening_workout_completed:
            evening_workout = Workout(
                user_id=test_user.id,
                daily_progress_id=progress.id,
                workout_type="evening",
                workout_category=random.choice(WORKOUT_CATEGORIES),
                duration_minutes=random.randint(30, 90),
                was_outdoor=random.choice([True, False]),
                notes=f"Test evening workout on day {progress.day_number}"
            )
            db.add(evening_workout)
    
    db.commit()
    
    return progress_data


@pytest.fixture(scope="function")
def create_test_workouts(db, test_user, create_test_progress):
    """Create additional test workouts for a user."""
    # The workouts are already created in the create_test_progress fixture
    workouts = db.query(Workout).filter(Workout.user_id == test_user.id).all()
    return workouts


@pytest.fixture(scope="function")
def second_test_user(db):
    """Return second test user."""
    return db.query(User).filter(User.email == TEST_USERS[1]["email"]).first()


@pytest.fixture(scope="function")
def second_user_token(second_test_user):
    """Create access token for second test user."""
    return create_access_token(data={"sub": second_test_user.email})


@pytest.fixture(scope="function")
def second_auth_headers(second_user_token):
    """Headers with bearer token for second test user."""
    return {"Authorization": f"Bearer {second_user_token}"}