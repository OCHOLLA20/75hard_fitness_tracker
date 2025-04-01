import pytest
from fastapi import status
from app.db.models import User
from app.core.auth import verify_password


def test_get_current_user(client, auth_headers):
    """Test getting the current user's profile."""
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "user1@example.com"
    assert data["username"] == "testuser1"
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned


def test_update_user_profile(client, auth_headers, db):
    """Test updating the user's profile."""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "username": "updatedusername",
            "email": "user1@example.com"  # Keep the same email
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "updatedusername"
    
    # Verify database was updated
    user = db.query(User).filter(User.email == "user1@example.com").first()
    assert user.username == "updatedusername"


def test_update_user_email(client, auth_headers, db):
    """Test updating the user's email."""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "username": "testuser1",  # Keep the same username
            "email": "updated@example.com"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "updated@example.com"
    
    # Verify database was updated
    user = db.query(User).filter(User.id == data["id"]).first()
    assert user.email == "updated@example.com"


def test_update_profile_duplicate_username(client, auth_headers, second_test_user):
    """Test updating username to one that already exists."""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "username": "testuser2",  # Username of second test user
            "email": "user1@example.com"  # Keep the same email
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already registered" in response.json()["detail"]


def test_update_profile_duplicate_email(client, auth_headers, second_test_user):
    """Test updating email to one that already exists."""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "username": "testuser1",  # Keep the same username
            "email": "user2@example.com"  # Email of second test user
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]


def test_update_user_password(client, auth_headers, db):
    """Test updating user profile with password change."""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "username": "testuser1",
            "email": "user1@example.com",
            "password": "newpassword123",
            "current_password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    # Verify password was updated
    user = db.query(User).filter(User.email == "user1@example.com").first()
    assert verify_password("newpassword123", user.hashed_password)
    
    # Test login with new password
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "user1@example.com",
            "password": "newpassword123"
        }
    )
    
    assert login_response.status_code == status.HTTP_200_OK
    assert "access_token" in login_response.json()


def test_update_password_incorrect_current(client, auth_headers):
    """Test updating password with incorrect current password."""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "username": "testuser1",
            "email": "user1@example.com",
            "password": "newpassword123",
            "current_password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Incorrect current password" in response.json()["detail"]


def test_get_user_stats(client, auth_headers, create_test_progress):
    """Test getting user statistics."""
    response = client.get(
        "/api/v1/users/me/stats",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Check that the statistics fields are present
    assert "days_completed" in data
    assert "total_days" in data
    assert "completion_rate" in data
    assert "water_intake_average" in data
    assert "workout_categories" in data
    
    # Basic validation of the statistics
    assert data["total_days"] >= 0
    assert 0 <= data["completion_rate"] <= 100
    assert data["water_intake_average"] >= 0


def test_get_empty_user_stats(client, auth_headers, db):
    """Test getting stats for a user with no progress data."""
    # First, create a new user
    new_user_email = "nodata@example.com"
    new_user = User(
        email=new_user_email,
        username="nodatauser",
        hashed_password=get_password_hash("testpass123")
    )
    db.add(new_user)
    db.commit()
    
    # Create token for this user
    from app.core.auth import create_access_token, get_password_hash
    token = create_access_token(data={"sub": new_user_email})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get stats for this user
    response = client.get(
        "/api/v1/users/me/stats",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # For a user with no data, stats should show zeros or empty values
    assert data["days_completed"] == 0
    assert data["total_days"] == 0
    assert data["completion_rate"] == 0
    assert data["water_intake_average"] == 0
    assert len(data["workout_categories"]) == 0


def test_user_not_found(client):
    """Test behavior when user is not found."""
    # Generate a token for a non-existent user
    from app.core.auth import create_access_token
    token = create_access_token(data={"sub": "nonexistent@example.com"})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(
        "/api/v1/users/me",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]


def test_inactive_user_access(client, db, test_user):
    """Test that inactive users cannot access the API."""
    # Deactivate the user
    test_user.is_active = False
    db.commit()
    
    # Try to log in
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "user1@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Inactive user" in response.json()["detail"]
    
    # Restore the user for other tests
    test_user.is_active = True
    db.commit()
