"""Tests for API routes."""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "PixelPet"


def test_home_page(client):
    """Test home page renders."""
    response = client.get("/")
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_login_page(client):
    """Test login page renders."""
    response = client.get("/login")
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_create_pet_endpoint(client, test_user_data, test_pet_data):
    """Test pet creation endpoint."""
    # Register and login user first
    register_response = client.post("/auth/register", json=test_user_data)
    token = register_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create pet
    response = client.post("/pets/", json=test_pet_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_pet_data["name"]
    assert data["species"] == test_pet_data["species"]
    assert data["hunger"] == 50
    assert data["happiness"] == 50
    assert data["energy"] == 50


def test_get_pet_endpoint(client, test_user_data, test_pet_data):
    """Test get pet endpoint."""
    # Register user and create pet
    register_response = client.post("/auth/register", json=test_user_data)
    token = register_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create pet
    client.post("/pets/", json=test_pet_data, headers=headers)
    
    # Get pet
    response = client.get("/pets/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_pet_data["name"]
    assert data["species"] == test_pet_data["species"]


def test_feed_pet_endpoint(client, test_user_data, test_pet_data):
    """Test feed pet endpoint."""
    # Register user and create pet
    register_response = client.post("/auth/register", json=test_user_data)
    token = register_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Create pet
    client.post("/pets/", json=test_pet_data, headers=headers)

    # Feed pet
    response = client.post("/pets/feed", headers=headers)

    assert response.status_code == 200
    data = response.json()
    # Returns PetResponse with updated stats
    assert "hunger" in data
    assert data["hunger"] == 70  # 50 + 20 from feeding


def test_play_pet_endpoint(client, test_user_data, test_pet_data):
    """Test play with pet endpoint."""
    # Register user and create pet
    register_response = client.post("/auth/register", json=test_user_data)
    token = register_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Create pet
    client.post("/pets/", json=test_pet_data, headers=headers)

    # Play with pet
    response = client.post("/pets/play", headers=headers)

    assert response.status_code == 200
    data = response.json()
    # Returns PetResponse with updated stats
    assert "happiness" in data
    assert data["happiness"] == 65  # 50 + 15 from playing


def test_sleep_pet_endpoint(client, test_user_data, test_pet_data):
    """Test put pet to sleep endpoint."""
    # Register user and create pet
    register_response = client.post("/auth/register", json=test_user_data)
    token = register_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Create pet
    client.post("/pets/", json=test_pet_data, headers=headers)

    # Put pet to sleep
    response = client.post("/pets/sleep", headers=headers)

    assert response.status_code == 200
    data = response.json()
    # Returns PetResponse with updated stats
    assert "is_sleeping" in data
    assert data["is_sleeping"] is True


def test_unauthorized_access(client):
    """Test that endpoints require authentication."""
    # Try to access pet endpoints without token
    endpoints = [
        ("/pets/", "GET"),
        ("/pets/", "POST"),
        ("/pets/feed", "POST"),
        ("/pets/play", "POST"),
        ("/pets/sleep", "POST")
    ]
    
    for endpoint, method in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={})
        
        assert response.status_code == 401


def test_pet_not_found(client, test_user_data):
    """Test accessing pet endpoints when user has no pet."""
    # Register user but don't create pet
    register_response = client.post("/auth/register", json=test_user_data)
    token = register_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to get pet
    response = client.get("/pets/", headers=headers)
    assert response.status_code == 404
    
    # Try to feed pet
    response = client.post("/pets/feed", headers=headers)
    assert response.status_code == 404
