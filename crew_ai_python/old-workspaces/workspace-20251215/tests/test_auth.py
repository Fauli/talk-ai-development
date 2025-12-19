"""Tests for authentication functionality."""
import pytest
from fastapi.testclient import TestClient

from app.auth import create_access_token, verify_password, hash_password


def test_hash_password():
    """Test password hashing."""
    password = "testpassword123"
    hashed = hash_password(password)
    
    # Should return salt:hash format
    assert ":" in hashed
    assert len(hashed.split(":")) == 2
    
    # Should verify correctly
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token():
    """Test JWT token creation."""
    user_id = 1
    token = create_access_token({"sub": str(user_id)})
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_register_success(client, test_user_data):
    """Test successful user registration."""
    response = client.post("/auth/register", json=test_user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client, test_user_data):
    """Test registration with duplicate email."""
    # Register first user
    client.post("/auth/register", json=test_user_data)
    
    # Try to register same email again
    response = client.post("/auth/register", json=test_user_data)
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client, test_user_data):
    """Test successful login."""
    # First register a user
    client.post("/auth/register", json=test_user_data)
    
    # Then login
    response = client.post("/auth/login", json=test_user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password."""
    # First register a user
    client.post("/auth/register", json=test_user_data)
    
    # Try login with wrong password
    wrong_data = test_user_data.copy()
    wrong_data["password"] = "wrongpassword"
    
    response = client.post("/auth/login", json=wrong_data)
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client, test_user_data):
    """Test login with nonexistent user."""
    response = client.post("/auth/login", json=test_user_data)
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]