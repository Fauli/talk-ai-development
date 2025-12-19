import pytest
from fastapi import status
from app.auth_simple import get_password_hash, verify_password, authenticate_user, get_user_by_email
from app.models import User

def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original
    assert hashed != password
    # Should verify correctly
    assert verify_password(password, hashed) is True
    # Wrong password should not verify
    assert verify_password("wrongpassword", hashed) is False

def test_register_user(client):
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "password": "newpassword123"
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register_duplicate_email(client):
    # Register first user
    client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    
    # Try to register same email again
    response = client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "differentpassword"
    })
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"]

def test_login_success(client):
    # Register user first
    client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "loginpassword"
    })
    
    # Login
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "loginpassword"
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    # Register user first
    client.post("/auth/register", json={
        "email": "wrongpwd@example.com",
        "password": "correctpassword"
    })
    
    # Login with wrong password
    response = client.post("/auth/login", json={
        "email": "wrongpwd@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "somepassword"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticate_user_function(test_db, test_user):
    # Test successful authentication
    user = authenticate_user(test_db, "test@example.com", "testpassword")
    assert user is not None
    assert user.email == "test@example.com"
    
    # Test wrong password
    user = authenticate_user(test_db, "test@example.com", "wrongpassword")
    assert user is None
    
    # Test nonexistent user
    user = authenticate_user(test_db, "nonexistent@example.com", "password")
    assert user is None

def test_get_user_by_email(test_db, test_user):
    # Test existing user
    user = get_user_by_email(test_db, "test@example.com")
    assert user is not None
    assert user.email == "test@example.com"
    
    # Test nonexistent user
    user = get_user_by_email(test_db, "nonexistent@example.com")
    assert user is None
