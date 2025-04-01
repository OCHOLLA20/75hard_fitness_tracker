import pytest
from fastapi import status
from app.core.auth import get_password_hash, verify_password
from app.db.models import User


def test_signup_success(client, db):
    """Test successful user registration."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepassword123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify user was created in the database
    user = db.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None
    assert user.username == "newuser"
    assert verify_password("securepassword123", user.hashed_password)


def test_signup_duplicate_email(client, test_user):
    """Test registration with an email that already exists."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "user1@example.com",  # Already exists from conftest.py
            "username": "differentusername",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]


def test_signup_duplicate_username(client, test_user):
    """Test registration with a username that already exists."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "different@example.com",
            "username": "testuser1",  # Already exists from conftest.py
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already registered" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "user1@example.com",  # Using email as username for OAuth2 form
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_email(client):
    """Test login with non-existent email."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_wrong_password(client, test_user):
    """Test login with incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "user1@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["detail"]


def test_access_protected_route_with_token(client, auth_headers):
    """Test accessing a protected route with a valid token."""
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert data["email"] == "user1@example.com"


def test_access_protected_route_without_token(client):
    """Test accessing a protected route without a token."""
    response = client.get("/api/v1/users/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]


def test_access_protected_route_with_invalid_token(client):
    """Test accessing a protected route with an invalid token."""
    headers = {"Authorization": "Bearer invalidtoken123"}
    response = client.get(
        "/api/v1/users/me",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in response.json()["detail"]


def test_token_refresh(client, auth_headers):
    """Test refreshing an access token."""
    response = client.post(
        "/api/v1/auth/refresh-token",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Test the new token works
    new_headers = {"Authorization": f"Bearer {data['access_token']}"}
    user_response = client.get(
        "/api/v1/users/me",
        headers=new_headers
    )
    
    assert user_response.status_code == status.HTTP_200_OK


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_expired_token(client, monkeypatch):
    """Test behavior with an expired token."""
    import jwt
    from datetime import datetime, timedelta
    from app.core.config import settings
    
    # Create an expired token
    data = {"sub": "user1@example.com", "exp": datetime.utcnow() - timedelta(minutes=1)}
    expired_token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get(
        "/api/v1/users/me",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in response.json()["detail"]
